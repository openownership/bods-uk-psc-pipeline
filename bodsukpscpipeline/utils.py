import pycountry
import re

from datetime import datetime

def latest_date(update_frequency):
    current_time = datetime.now()
    if update_frequency == "daily":
        if current_time.hour > 10:
            return current_time.strftime("%Y-%m-%d")
        else:
            if current_time.day > 1:
                last_date = current_time.replace(day=current_time.day-1)
            else:
                last_date = current_time.replace(day=1, month=current_time.month-1)
            return last_date.strftime("%Y-%m-%d")
    else:
        last_date = current_time.replace(day=1)
        return last_date.strftime("%Y-%m-%d")

def build_url(url, update_frequency):
    return re.sub(r"\d{4}-\d{2}-\d{2}", latest_date(update_frequency), url)

def country_code(name):
    """Get country code"""
    if name.lower() in ("england", "wales"):
        code = "GB"
    else:
        try:
            code = pycountry.countries.lookup(name).alpha_2
        except LookupError:
            code = None
    return code

class UKCOHData:
    def __init__(self, url=None, update_frequency="daily"):
        """Initialise with url"""
        self.url = url
        self.update_frequency = update_frequency

    def sources(self, last_update=False, delta_type=None):
        """Yield data sources"""
        yield build_url(self.url, self.update_frequency)

def identify_uk_coh(item):
    """Identify type of UK COH data"""
    if 'CompanyName' in item:
        return 'uk_company'
    elif 'company_number' in item:
        return 'uk_psc'

def psc_exclude(item):
    if 'generated_at' in item['data']:
        return True
    return False
