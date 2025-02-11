import os
import csv
import json
import pycountry
from py_i18n_countries import get_country, get_nationality

data_dir = os.path.dirname(__file__)

state_demonyms = {
  "vietnamese": "VN",
  "guamanian": "GU",
  "french": "FR",
  "senegalese": "SN",
  "thai": "TH",
  "bangladeshi": "BD",
  "nicaraguan": "NI",
  "gabonese": "GA",
  "brazilian": "BR",
  "greenlandic": "GL",
  "i-kiribati": "KI",
  "iraqi": "IQ",
  "liberian": "LR",
  "kenyan": "KE",
  "bosnian": "BA",
  "herzegovinian": "BA",
  "bosnian,herzegovinian": "BA",
  "indian": "IN",
  "cuban": "CU",
  "greek": "GR",
  "christmas island": "CX",
  "malaysian": "MY",
  "nigerian": "NG",
  "gambian": "GM",
  "gibraltar": "GI",
  "peruvian": "PE",
  "georgian": "GE",
  "irish": "IE",
  "belarusian": "BY",
  "bhutanese": "BT",
  "guatemalan": "GT",
  "albanian": "AL",
  "ukrainian": "UA",
  "togolese": "TG",
  "estonian": "EE",
  "guinea-bissauan": "GW",
  "chinese": "CN",
  "manx": "IM",
  "barbadian": "BB",
  "finnish": "FI",
  "new caledonian": "NC",
  "caymanian": "KY",
  "puerto rican": "PR",
  "japanese": "JP",
  "argentinean": "AR",
  "israeli": "IL",
  "haitian": "HT",
  "iranian": "IR",
  "canadian": "CA",
  "german": "DE",
  "ghanaian": "GH",
  "trinidadian": "TT",
  "sri lankan": "LK",
  "mongolian": "MN",
  "russian": "RU",
  "bermudian": "BM",
  "malian": "ML",
  "bahamian": "BS",
  "sierra leonean": "SL",
  "polish": "PL",
  "norwegian": "NO",
  "austrian": "AT",
  "anguillian": "AI",
  "kazakhstani": "KZ",
  "mauritanian": "MR",
  "czech": "CZ",
  "marshallese": "MH",
  "moldovan": "MD",
  "burundian": "BI",
  "faroese": "FO",
  "venezuelan": "VE",
  "ni-vanuatu": "VU",
  "turkish": "TR",
  "belgian": "BE",
  "motswana": "BW",
  "new zealander": "NZ",
  "bolivian": "BO",
  "kuwaiti": "KW",
  "uruguayan": "UY",
  "montserratian": "MS",
  "saudi arabian": "SA",
  "syrian": "SY",
  "mauritian": "MU",
  "uzbekistani": "UZ",
  "monegasque": "MC",
  "danish": "DK",
  "portuguese": "PT",
  "lithuanian": "LT",
  "tongan": "TO",
  "sudanese": "SD",
  "moroccan": "MA",
  "south african": "ZA",
  "egyptian": "EG",
  "guadeloupian": "GP",
  "american samoan": "AS",
  "comoran": "KM",
  "icelander": "IS",
  "italian": "IT",
  "south sudanese": "SS",
  "british": "GB",
  "bahraini": "BH",
  "yemeni": "YE",
  "bruneian": "BN",
  "tadzhik": "TJ",
  "jordanian": "JO",
  "dominican": "DM",
  "chilean": "CL",
  "azerbaijani": "AZ",
  "algerian": "DZ",
  "ethiopian": "ET",
  "kirghiz": "KG",
  "tanzanian": "TZ",
  "honduran": "HN",
  "ugandan": "UG",
  "maldivan": "MV",
  "lebanese": "LB",
  "romanian": "RO",
  "costa rican": "CR",
  "australian": "AU",
  "afghan": "AF",
  "east timorese": "TL",
  "grenadian": "GD",
  "mexican": "MX",
  "swazi": "SZ",
  "nepalese": "NP",
  "guyanese": "GY",
  "turkmen": "TM",
  "latvian": "LV",
  "surinamer": "SR",
  "spanish": "ES",
  "zimbabwean": "ZW",
  "ivorian": "CI",
  "congolese": "CD",
  "dutch": "NL",
  "american": "US",
  "niuean": "NU",
  "emirati": "AE",
  "cypriot": "CY",
  "singaporean": "SG",
  "libyan": "LY",
  "seychellois": "SC",
  "omani": "OM",
  "paraguayan": "PY",
  "zambian": "ZM",
  "ecuadorean": "EC",
  "saint vincentian": "VC",
  "kittian and nevisian": "KN",
  "cambodian": "KH",
  "north korean": "KP",
  "djibouti": "DJ",
  "maltese": "MT",
  "cameroonian": "CM",
  "hungarian": "HU",
  "french polynesian": "PF",
  "indonesian": "ID",
  "nauruan": "NR",
  "jamaican": "JM",
  "salvadoran": "SV",
  "micronesian": "FM",
  "armenian": "AM",
  "laotian": "LA",
  "malagasy": "MG",
  "cape verdian": "CV",
  "fijian": "FJ",
  "tokelauan": "TK",
  "sahrawi": "EH",
  "equatorial guinean": "GQ",
  "eritrean": "ER",
  "antiguan": "AG",
  "barbudan": "AG",
  "antiguan,barbudan": "AG",
  "sammarinese": "SM",
  "malawian": "MW",
  "chadian": "TD",
  "colombian": "CO",
  "qatari": "QA",
  "bulgarian": "BG",
  "beninese": "BJ",
  "tuvaluan": "TV",
  "south korean": "KR",
  "aruban": "AW",
  "angolan": "AO",
  "saint lucian": "LC",
  "croatian": "HR",
  "liechtensteiner": "LI",
  "filipino": "PH",
  "panamanian": "PA",
  "pakistani": "PK",
  "macedonian": "MK",
  "taiwanese": "TW",
  "tunisian": "TN",
  "saint helenian": "SH",
  "belizean": "BZ",
  "slovak": "SK",
  "nigerien": "NE",
  "central african": "CF",
  "rwandan": "RW",
  "slovene": "SI",
  "luxembourger": "LU",
  "samoan": "WS",
  "sao tomean": "ST",
  "serbian": "RS",
  "burkinabe": "BF",
  "namibian": "NA",
  "mosotho": "LS",
  "papua new guinean": "PG",
  "swedish": "SE",
  "mozambican": "MZ",
  "swiss": "CH",
  "somali": "SO",
  "palauan": "PW",
  "guinean": "GN"
}

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
    with open(f"{data_dir}/demonyms.csv") as csv_file:
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
    with open(f"{data_dir}/uk_nationality_data.txt") as csv_file:
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
