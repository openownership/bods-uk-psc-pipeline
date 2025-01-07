import csv
import json
import pycountry
from py_i18n_countries import get_country, get_nationality

def check_subdivisions(row, data, subdivisions):
    match = [sub for sub in subdivisions if sub.name == row[1]]
    if match and len(match) == 1:
        data[row[0]] = match[0].country_code

def add_data(data):
    data["Arabian"] = "SA"
    data["Afghani"] = "AF"
    data["British Virgin Islander"] = "VG"
    data["Federation Of Saint Kitts & Nevis"] = "KN"
    data["USA"] = "US"
    data["N.Irish"] = "GB"
    data["Bulga"] = "BG"
    data["British Cornish"] = "GB"
    data["Congolese"] = "CD"
    data["Tansanian"] = "TZ"
    data["Brit Scot"] = "GB"
    data["Unitied Kingdom"] = "GB"
    data["Bristish"] = "GB"
    data["British Asian"] = "GB"
    data["Republic Of Lebanon"] = "LB"
    data["Lituania"] = "LT"
    data["Congolease"] = "CD"
    data["Deutsch"] = "DE"
    data["Us Citizen- American(United States Of America)"] = "US"
    data["Nigeria British"] = "GB"
    data["Korean"] = "KR"

def load_data():
    data = {}
    with open("demonyms.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        subdivisions = list(pycountry.subdivisions)
        for row in csv_reader:
            try:
                country = pycountry.countries.get(name=row[1])
                if country:
                    data[row[0]] = country.alpha_2
                else:
                    check_subdivisions(row, data, subdivisions)
            except:
                check_subdivisions(row, data, subdivisions)
    with open("uk_nationality_data.txt") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if not row[0] in data:
                data[row[0]] = row[1]
    for country in pycountry.countries:
        if not country.name in data:
            data[country.name] = country.alpha_2
    add_data(data)
    return data

def lookup_nationality(data, text):
    for nationality in data:
        if text.lower() == nationality.lower():
            return data[nationality]
        country = pycountry.countries.get(name=text)
        if country:
            return country.alpha_2
        if '/' in text:
            for n in text.split('/'):
                 if n.strip().lower() == nationality.lower():
                     return data[nationality]
    return None
