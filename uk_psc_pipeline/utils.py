from datetime import datetime

def latest_date():
    current_time = datetime.now()
    if current_time.hour > 10:
        return current_time.strftime("%Y-%m-%d")
    else:
        if current_time.day > 1:
            last_date = current_time.replace(day=current_time.day-1)
        else:
            last_date = current_time.replace(day=1, month=current_time.month-1)
        return last_date.strftime("%Y-%m-%d")

def build_url(url):
    return re.sub(r"\d{4}-\d{2}-\d{2}", latest_date(), url)

class UKCOHData:
    def __init__(self, url=None, data_date=None):
        """Initialise with url"""
        self.url = url
        self.data_date = data_date

    def sources(self, last_update=False, delta_type=None):
        """Yield data sources"""
        yield build_url(self.url)
