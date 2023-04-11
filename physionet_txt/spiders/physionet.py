import scrapy
from scrapy.spiders import Spider
from physionet_txt.items import PhysionetTxtItem
import logging
import re
import mariadb
import sys
from dotenv import dotenv_values


class PhysionetSpider(Spider):
    name = "physionet"
    allowed_domains = ["physionet.org"]
    start_urls = ["https://physionet.org/files/mimic-cxr/2.0.0/files/"]

    http_auth_domain = "physionet.org"
    user_agent = "Wget/1.21.3"

    def __init__(self):
        env = dotenv_values(".env")
        if env:
            logging.info("Loaded dotenv file")
        else:
            logging.critical("No env file exists; terminating")
            exit(1)

        self.http_user = env.get("PHYSIONET_USERNAME", None)
        self.http_pass = env.get("PHYSIONET_PASSWORD", None)

        self.mariadb_username = env.get("MARIADB_USERNAME", None)
        self.mariadb_password = env.get("MARIADB_PASSWORD", None)
        self.mariadb_host = env.get("MARIADB_HOST", None)
        self.mariadb_port = env.get("MARIADB_PORT", "3306")
        self.mariadb_database = env.get("MARIADB_DATABASE", "mimiciv")
        self.mariadb_conn = None

        if (not self.http_user) or (not self.http_pass):
            logging.critical(
                "Did not receive username or password from environment; use variables: PHYSIONET_USER and PHYSIONET_PASSWORD")
            exit(1)
        else:
            logging.info("Basic auth for Physionet configured.")
        if not self.mariadb_username or not self.mariadb_password:
            logging.warn(
                "No connection to MariaDB was configured, you can use these environment variables.")
            logging.warn(
                "MARIADB_USERNAME and MARIADB_PASSWORD; MARIADB_HOST, MARIADB_PORT and MARIADB_DATABASE (default 'mimiciv').")
            logging.warn(
                "Otherwise, the data will not be inserted into the MariaDB database.")
        else:
            logging.info("MariaDB credentials: username %s, password: %s***",
                         self.mariadb_username, self.mariadb_password[:3])
            try:
                self.mariadb_conn = mariadb.connect(
                    user=self.mariadb_username,
                    password=self.mariadb_password,
                    host=self.mariadb_host,
                    port=int(self.mariadb_port),
                    database=self.mariadb_database
                )
                self.mariadb_conn.autocommit = True
                logging.info("Connected to MariaDB version %s at: %s using autocommit",
                             self.mariadb_conn.server_info, self.mariadb_conn.server_name)
                # since we're starting from scratch, we need to truncate the table
                self.mariadb_conn.cursor().execute("TRUNCATE mimiciv.cxr_note;")
                logging.info("truncated mimiciv.cxr_note table")
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(1)

    def parse(self, response):
        """
        This function parses the result returned from the spider,
        depending on the content type
        """
        content_type = response.headers["Content-Type"]
        if b"text/plain" in content_type:
            # this is a txt file (i.e. an item)
            url = response.url
            subject_match = re.search("p\\d{4,10}", url)
            study_match = re.search("s\\d{4,10}", url)
            if subject_match and study_match:
                text = response.body.decode('utf-8')
                filename = response.url.rstrip("/").split("/")[-1]
                item = PhysionetTxtItem(
                    url=url,
                    subject=subject_match.group(0),
                    study=study_match.group(0),
                    filename=filename,
                    text=text)
                logging.info(f"Retrieved from {url}")
                yield item
            else:
                logging.warn(
                    f"No match at url: subject {subject_match}, study {study_match}")
        elif b"text/html" in content_type:
            # this is a html file (i.e. it contains more links)
            paths = []
            for a in response.xpath("//a").getall():
                href = re.search("href=\"([sp]\d*(\.txt|\/))\"", a)
                if href:
                    relpath = href.group(1)
                    paths.append(relpath)
                    # todo yield links
            #logging.debug(f"At {response.url}: {paths}")
            for path in paths:
                yield scrapy.Request(response.urljoin(path), self.parse)
        # else: this applies to DCM files, which we don't care about at all.

    def closed(self, reason):
        """
        This function is called when the spider is closed; making sure to close the connection to the database.
        """
        if self.mariadb_conn is not None:
            self.mariadb_conn.close()
            logging.info(f"Closed mariadb connection: {reason}")
