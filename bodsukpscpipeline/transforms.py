class RemovePeriodsFromProperties:
    """Data processor to add ContentDate"""
    def __init__(self, identify=None):
        """Initial setup"""
        self.identify = identify

    async def process(self, item, item_type, header, mapping={}, updates=False):
        """Process item"""
        if self.identify: item_type = self.identify(item)
        if item_type == 'uk_company':
            out = {}
            for property in item:
                out[property.replace(".", "_")] = item[property]
        else:
            out = item
        yield out

class AddContentDate:
    """Data processor to add ContentDate"""
    def __init__(self, identify=None):
        """Initial setup"""
        self.identify = identify

    async def process(self, item, item_type, header, mapping={}, updates=False):
        """Process item"""
        if self.identify: item_type = self.identify(item)
        if item_type == 'uk_psc':
            item["ContentDate"] = header["data"]["generated_at"].split("T")[0]
        yield item
