# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class PhysionetTxtPipeline:
    """
    This is the pipeline that will be called by the spider for each item.    
    """

    def process_item(self, item, spider):
        """
        We insert the item into the database as a side effect.
        """

        print(item)
        if spider.mariadb_conn is not None:
            cursor = spider.mariadb_conn.cursor()
            cursor.execute("INSERT INTO mimiciv.cxr_note (url, subject_id, study_id, text) VALUES (?,?,?,?);",
                           (item["url"], item["subject"].lstrip("p"),
                            item["study"].lstrip("s"), item["text"])
                           )
            
        return item
