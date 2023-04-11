# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.exceptions import ScrapyDeprecationWarning
from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.url import url_is_from_any_domain
from w3lib.http import basic_auth_header

import warnings
import logging


class MyHttpAuthMiddleware:
    """Set Basic HTTP Authorization header
    (http_user and http_pass spider class attributes)

    @url https://docs.scrapy.org/en/latest/_modules/scrapy/downloadermiddlewares/httpauth.html#HttpAuthMiddleware
    """

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        usr = getattr(spider, "http_user", "")
        pwd = getattr(spider, "http_pass", "")
        if usr or pwd:
            self.auth = basic_auth_header(usr, pwd)
            # this is the main difference to the original file linked above
            # we don't want to print the password to the log, but give
            # the user a hint that we are using basic auth
            logging.info(
                f"Using basic auth with user {usr} and password {pwd[:3]}***, auth header {self.auth[:8]}***")
            if not hasattr(spider, "http_auth_domain"):
                warnings.warn(
                    "Using HttpAuthMiddleware without http_auth_domain is deprecated and can cause security "
                    "problems if the spider makes requests to several different domains. http_auth_domain "
                    "will be set to the domain of the first request, please set it to the correct value "
                    "explicitly.",
                    category=ScrapyDeprecationWarning,
                )
                self.domain_unset = True
            else:
                self.domain = spider.http_auth_domain
                self.domain_unset = False

    def process_request(self, request, spider):
        auth = getattr(self, "auth", None)
        if auth and b"Authorization" not in request.headers:
            domain = urlparse_cached(request).hostname
            if self.domain_unset:
                self.domain = domain
                self.domain_unset = False
            if not self.domain or url_is_from_any_domain(request.url, [self.domain]):
                request.headers[b"Authorization"] = auth
