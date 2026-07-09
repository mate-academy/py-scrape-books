from itemadapter import ItemAdapter


class ScrapeBooksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get("title"):
            adapter["title"] = adapter["title"].strip()

        if adapter.get("category"):
            adapter["category"] = adapter["category"].strip()

        if adapter.get("description"):
            adapter["description"] = adapter["description"].strip()

        return item
