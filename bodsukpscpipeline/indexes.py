import hashlib

# UK Company Elasticsearch Properties
uk_company_properties = {"CompanyName": {'type': 'text'},
                         "CompanyNumber": {'type': 'text'},
                         "RegAddress_CareOf": {'type': 'text'},
                         "RegAddress_POBox": {'type': 'text'},
                         "RegAddress_AddressLine1": {'type': 'text'},
                         "RegAddress_AddressLine2": {'type': 'text'},
                         "RegAddress_PostTown": {'type': 'text'},
                         "RegAddress_County": {'type': 'text'},
                         "RegAddress_Country": {'type': 'text'},
                         "RegAddress_PostCode": {'type': 'text'},
                         "CompanyCategory": {'type': 'text'},
                         "CompanyStatus": {'type': 'text'},
                         "CountryOfOrigin": {'type': 'text'},
                         "DissolutionDate": {'type': 'text'},
                         "IncorporationDate": {'type': 'text'},
                         "Accounts_AccountRefDay": {'type': 'text'},
                         "Accounts_AccountRefMonth": {'type': 'text'},
                         "Accounts_NextDueDate": {'type': 'text'},
                         "Accounts_LastMadeUpDate": {'type': 'text'},
                         "Accounts_AccountCategory": {'type': 'text'},
                         "Returns_NextDueDate": {'type': 'text'},
                         "Returns_LastMadeUpDate": {'type': 'text'},
                         "Mortgages_NumMortCharges": {'type': 'text'},
                         "Mortgages_NumMortOutstanding": {'type': 'text'},
                         "Mortgages_NumMortPartSatisfied": {'type': 'text'},
                         "Mortgages_NumMortSatisfied": {'type': 'text'},
                         "SICCode_SicText_1": {'type': 'text'},
                         "SICCode_SicText_2": {'type': 'text'},
                         "SICCode_SicText_3": {'type': 'text'},
                         "SICCode_SicText_4": {'type': 'text'},
                         "LimitedPartnerships_NumGenPartners": {'type': 'text'},
                         "LimitedPartnerships_NumLimPartners": {'type': 'text'},
                         "URI": {'type': 'text'},
                         "PreviousName_1_CONDATE": {'type': 'text'},
                         "PreviousName_1_CompanyName": {'type': 'text'},
                         "PreviousName_2_CONDATE": {'type': 'text'},
                         "PreviousName_2_CompanyName": {'type': 'text'},
                         "PreviousName_3_CONDATE": {'type': 'text'},
                         "PreviousName_3_CompanyName": {'type': 'text'},
                         "PreviousName_4_CONDATE": {'type': 'text'},
                         "PreviousName_4_CompanyName": {'type': 'text'},
                         "PreviousName_5_CONDATE": {'type': 'text'},
                         "PreviousName_5_CompanyName": {'type': 'text'},
                         "PreviousName_6_CONDATE": {'type': 'text'},
                         "PreviousName_6_CompanyName": {'type': 'text'},
                         "PreviousName_7_CONDATE": {'type': 'text'},
                         "PreviousName_7_CompanyName": {'type': 'text'},
                         "PreviousName_8_CONDATE": {'type': 'text'},
                         "PreviousName_8_CompanyName": {'type': 'text'},
                         "PreviousName_9_CONDATE": {'type': 'text'},
                         "PreviousName_9_CompanyName": {'type': 'text'},
                         "PreviousName_10_CONDATE": {'type': 'text'},
                         "PreviousName_10_CompanyName": {'type': 'text'},
                         "ConfStmtNextDueDate": {'type': 'text'},
                         "ConfStmtLastMadeUpDate": {'type': 'text'}}

# UK PSC Elasticsearch Properties
uk_psc_properties = {"company_number": {'type': 'text'},
                     "data": {'type': 'object',
                               'properties': {"address": {'type': 'object',
                                                          'properties': {"address_line_1": {'type': 'text'},
                                                                         "address_line_2": {'type': 'text'},
                                                                         "country": {'type': 'text'},
                                                                         "locality": {'type': 'text'},
                                                                         "postal_code": {'type': 'text'},
                                                                         "premises": {'type': 'text'},
                                                                         "region": {'type': 'text'}}},
                                              "country_of_residence": {'type': 'text'},
                                              "date_of_birth": {'type': 'object',
                                                                'properties': {"month": {'type': 'integer'},
                                                                               "year": {'type': 'integer'}}},
                                              "etag": {'type': 'text'},
                                              "identification": {'type': 'object',
                                                                 'properties': {"country_registered": {'type': 'text'},
                                                                                "legal_authority": {'type': 'text'},
                                                                                "legal_form": {'type': 'text'},
                                                                                "place_registered": {'type': 'text'},
                                                                                "registration_number": {'type': 'text'}}},
                                              "kind": {'type': 'text'},
                                              "links": {'type': 'object',
                                                        'properties': {"self": {'type': 'text'}}},
                                              "name": {'type': 'text'},
                                              "name_elements": {'type': 'object',
                                                                'properties': {"forename": {'type': 'text'},
                                                                               "surname": {'type': 'text'},
                                                                               "title": {'type': 'text'}}},
                                              "nationality": {'type': 'text'},
                                              "natures_of_control": {'type': 'text'},
                                              "ceased_on": {'type': 'text'},
                                              "notified_on": {'type': 'text'}}}}


def match_company(item):
    return {"match": {"CompanyNumber": item["CompanyNumber"]}}

def match_psc(item):
    return {"match": {"data.links.self": item["data"]["links"]["self"]}}

def id_company(item):
    return f"{item['CompanyNumber']}"

def id_psc(item):
    return f"{item['data']['links']['self']}"


# Elasticsearch indexes for UK PSC data
uk_psc_index_properties = {"uk_company": {"properties": uk_company_properties,
                                         "match": match_company,
                                         "id": id_company},
                          "uk_psc": {"properties": uk_psc_properties,
                                  "match": match_psc,
                                  "id": id_psc}}
