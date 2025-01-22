import pycountry

from bodspipelines.infrastructure.schemes.data import load_data, get_scheme, lookup_scheme
from bodspipelines.infrastructure.utils import current_date_iso
from bodsukpscpipeline import nationalities
from .utils import country_code

def get_country(text):
    country = None
    if "," in text:
        if text.split(",")[-1].strip().lower() in ("usa", "us", "united states"):
            #print("Searching for:", text.split(",")[0].lower())
            state = pycountry.subdivisions.search_fuzzy(text.split(",")[0].strip().lower())
            country = state
        else:
            try:
                country = pycountry.countries.search_fuzzy(text.split(",")[-1].strip().lower())
            except LookupError:
                pass
    if not country:
        try:
             country = pycountry.countries.search_fuzzy(text)
        except LookupError:
            for c in pycountry.countries:
                if c.name.lower()in text.lower():
                     country = c
    if not country:
        for c in ('england', 'wales', 'scotland', 'northern ireland'):
            if c in text.lower():
                country = pycountry.countries.get(alpha_2='GB')
    #print("Country:", country)
    return country[0] if isinstance(country, list) else country

def infer_scheme(item):
    if ("name" in item["data"] and "address" in item["data"] and "country" in 
         item["data"]["address"]):
        if item["data"]["name"].split()[-1].lower() in ("ag", "sa", "s.a.", "n.v.",
               "s/a", "d.d.", "a.s.", "a/s", "as", "oy", "a.e.", "rt", "pt", "k.k.",
               "spa", "bhd", "ПАО", "a.d.", "ab"):
            country = get_country(item["data"]["address"]["country"])
            code, name = lookup_scheme(country.alpha_2, "company", unconfirmed=True)
            return code, "company"
    if "identification" in item["data"]:
        #print("Ident:", item["data"]["identification"])
        if ("legal_authority" in item["data"]["identification"] and
            item["data"]["identification"]["legal_authority"] in ("Companies Act",
                                            "Companies Act 2006", "English Law",
                                            "Uk Companies Act 2006", "UK Companies Act 2006",
                                            'Companies Act 1985', "Limited Companys Act 2006",
                                            "Companies Acts", "Companies Act 2014",
                                            "Company Act 2006")):
            if "legal_form" in item["data"]["identification"]:
                for name in ("company", "compnay", "compamy", "companies", "limited"):
                    if name in item["data"]["identification"]["legal_form"].lower():
                        return "GB-COH", "company"
            else:
                return "GB-COH", "company"
        if ("legal_authority" in item["data"]["identification"] and 
            item["data"]["identification"]["legal_authority"] == "Trust Acts"):
            if "legal_form" in item["data"]["identification"]:
                if "trust" in item["data"]["identification"]["legal_form"].lower():
                    return "GB-COH", "trust"
        if ("legal_authority" in item["data"]["identification"] and
            "company" in item["data"]["identification"]["legal_authority"].lower()):
            if "legal_form" in item["data"]["identification"]:
                if "uk" in item["data"]["identification"]["legal_form"].lower():
                    return "GB-COH", "company"
        if "country_registered" in item["data"]["identification"]:
            country = get_country(item["data"]["identification"]["country_registered"])
        elif "legal_authority" in item["data"]["identification"]:
            country = get_country(item["data"]["identification"]["legal_authority"])
        if "legal_form" in item["data"]["identification"]:
            if "Government" in item["data"]["identification"]["legal_form"]:
                if "Department" in item["data"]["identification"]:
                    structure = "government_agency"
                else:
                    structure = "government"
            else:
                structure = "company"
        if structure == "government":
            return f"{country.alpha_2}-GOV", "government"
        else:
            country_code = country.alpha_2 if hasattr(country, "alpha_2") else country.code
            code, name = lookup_scheme(country_code, structure, unconfirmed=True)
            return code, structure

def build_entity_id(item):
    code, structure = infer_scheme(item)
    if structure == "government":
        name = item["data"]["name"]
        return f"{code}-{name.replace(' ','-')}"
    elif structure == "government_agency":
        name = item["data"]["name"]
        return f"{code}-{name.replace(' ','-')}"
    elif structure == "trust":
        name = item["data"]["name"]
        return f"{code}-{name.replace(' ','-')}"
    elif structure == "company":
        if "identification" in item["data"] and "registration_number" in item["data"]["identification"]:
            name = item["data"]["identification"]["registration_number"]
        else:
            name = item["data"]["name"].replace(' ','-')
        return f"{code}-{name}"

def build_entity_local_id(item):
    if ("identification" in item["data"] and
        "registration_number" in item["data"]["identification"]):
        return f"GB-COH-{item['data']['identification']['registration_number']}"
    else:
        link_id = item['data']['links']['self'].split('/')[-1]
        return f"GB-COH-ENT-{item['company_number']}-{link_id}"

def build_date(date):
    if date and "/" in date:
        comp = date.split("/")
        comp.reverse()
        return "-".join(comp)
    elif date and "-" in date:
        return date
    else:
        return None

def relationship_type(item):
    rtype = item["Relationship"]["RelationshipType"]
    if rtype == "IS_ULTIMATELY_CONSOLIDATED_BY":
        return "U"
    elif rtype == "IS_DIRECTLY_CONSOLIDATED_BY":
        return "D"
    else:
        return "O"

def exception_type(item):
    etype = item["ExceptionCategory"]
    if etype == "ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT":
        return "U"
    elif etype == "DIRECT_ACCOUNTING_CONSOLIDATION_PARENT":
        return "D"

def exception_unspecified(item):
    if item["data"]["kind"] == "persons-with-significant-control-statement":
        if item["data"]["statement"] == "no-individual-or-entity-with-signficant-control":
            return {"reason":"noBeneficialOwners","description":"Exception Reason: The company knows or has reasonable cause to believe that there is no registrable person or registrable relevant legal entity in relation to the company"}
        elif item["data"]["statement"] == "steps-to-find-psc-not-yet-completed":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The company has not yet completed taking reasonable steps to find out if there is anyone who is a registrable person or a registrable relevant legal entity in relation to the company"}
        elif item["data"]["statement"] == "psc-exists-but-not-identified":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The company knows or has reasonable cause to believe that there is a registrable person in relation to the company but it has not identified the registrable person"}
        elif item["data"]["statement"] == "psc-details-not-confirmed":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The company has identified a registrable person in relation to the company but all the required particulars of that person have not been confirmed"}
        elif item["data"]["statement"] == "steps-to-find-psc-not-yet-completed-partnership":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The partnership has not yet completed taking reasonable steps to find out if there is anyone who is a registrable person or a registrable relevant legal entity in relation to the partnership"}
        elif item["data"]["statement"] == "no-beneficial-owner-identified":
            return {"reason":"noBeneficialOwners","description":"Exception Reason: No beneficial owners have been identified"}
        elif item["data"]["statement"] == "psc-contacted-but-no-response":
            return {"reason":"interestedPartyHasNotProvidedInformation","description":"Exception Reason: The company has given a notice under section 790D of the Act which has not been complied with"}
        elif item["data"]["statement"] == "no-individual-or-entity-with-signficant-control-partnership":
            return {"reason":"noBeneficialOwners","description":"Exception Reason: The partnership knows or has reasonable cause to believe that there is no registrable person or registrable relevant legal entity in relation to the partnership"}
        elif item["data"]["statement"] == "somebody-has-become-or-ceased-to-be-a-beneficial-owner":
            return {"reason":"unknown","description":"Exception Reason: Somebody has become or ceased to be a beneficial owner during the update period"}
        elif item["data"]["statement"] == "psc-details-not-confirmed-partnership":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The partnership has identified a registrable person in relation to the partnership but all the required particulars of that person have not been confirmed"}
        elif item["data"]["statement"] == "psc-exists-but-not-identified-partnership":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The partnership knows or has reasonable cause to believe that there is a registrable person in relation to the partnership but it has not identified the registrable person"}
        elif item["data"]["statement"] == "at-least-one-beneficial-owner-unidentified":
            return {"reason":"unknown","description":"Exception Reason: Some beneficial owners have been identified and all required information can be provided"}
        elif item["data"]["statement"] == "restrictions-notice-issued-to-psc":
            return {"reason":"subjectExemptFromDisclosure","description":"Exception Reason: The company has issued a restrictions notice under paragraph 1 of Schedule 1B to the Act"}
        elif item["data"]["statement"] == "psc-has-failed-to-confirm-changed-details":
            return {"reason":"interestedPartyHasNotProvidedInformation","description":f"Exception Reason: {item['data']['statement']} has failed to comply with a notice given by the company under section 790E of the Act"}
        elif item["data"]["statement"] == "at-least-one-beneficial-owner-unidentified-and-information-not-provided-for-at-least-one-beneficial-owner":
            return {"reason":"unknown","description":"Exception Reason: Some beneficial owners have been identified and only some required information can be provided"}
        elif item["data"]["statement"] == "psc-contacted-but-no-response-partnership":
            return {"reason":"interestedPartyHasNotProvidedInformation","description":"Exception Reason: The partnership has given a notice under Regulation 10 of The Scottish Partnerships (Register of People with Significant Control) Regulations 2017 which has not been complied with"}
        elif item["data"]["statement"] == "information-not-provided-for-at-least-one-beneficial-owner":
            return {"reason":"unknown","description":"Exception Reason: All beneficial owners have been identified but only some required information can be provided"}
        # Not currently used
        elif item["data"]["statement"] == "psc-has-failed-to-confirm-changed-details-partnership":
            return {"reason":"subjectUnableToConfirmOrIdentifyBeneficialOwner","description":"Exception Reason: The partnership has given a notice under Regulation 11 of The Scottish Partnerships (Register of People with Significant Control) Regulations 2017 which has not been complied with"}
        elif item["data"]["statement"] == "restrictions-notice-issued-to-psc-partnership":
            return {"reason":"subjectExemptFromDisclosure","description":"Exception Reason: The partnership has issued a restrictions notice under paragraph 1 of Schedule 2 to The Scottish Partnerships (Register of People with Significant Control) Regulations 2017"}
    elif item["data"]["kind"] == "super-secure-person-with-significant-control": # ???
        return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: Super secure person with significant control"}
    elif item["data"]["kind"] == "super-secure-beneficial-owner": #???
        return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: Super secure beneficial owner"}
    elif item["data"]["kind"] == "exemptions":
        return {"reason":"interestedPartyExemptFromDisclosure","description": ""} # Include exemptions?

    #if item['ExceptionReason'] == 'NO_LEI':
    #    return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NO_LEI. This parent legal entity does not consent to obtain an LEI or to authorize its child entity to obtain an LEI on its behalf."}
    #elif item['ExceptionReason'] == 'NATURAL_PERSONS':
    #    return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NATURAL_PERSONS. The entity is controlled by a natural person(s) without any intermediate legal entity."}
    #elif item['ExceptionReason'] == 'NON_CONSOLIDATING':
    #    return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NON_CONSOLIDATING. The legal entity or entities are not obliged to provide consolidated accounts in relation to the entity they control."}
    #elif item['ExceptionReason'] == 'NO_KNOWN_PERSON':
    #    return {"reason":"informationUnknownToPublisher","description":"Exception Reason: NO KNOWN_PERSON. There is no known person(s) controlling the entity."}
    #elif item['ExceptionReason'] == 'NON_PUBLIC':
    #    return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NON_PUBLIC. Information about the relationship with the controlling entity is not public."}

#def get_scheme(scheme_id, scheme_data):
#    match = [scheme for scheme in scheme_data if scheme[0] == scheme_id]
#    if match:
#        country = match[0][2]
#        return lookup_scheme(country, "company")
#    return None, None

def interest_share(control):
    interest_share = {"maximum": None,
                      "minimum": None,
                      "exclusiveMinimum": None,
                      "exclusiveMaximum": None}
    if "75-to-100-percent" in control:
        interest_share["maximum"] = 100
        interest_share["minimum"] = 75
    elif "25-to-50-percent" in control:
        interest_share["maximum"] = 50
        interest_share["minimum"] = 25
    elif "50-to-75-percent" in control:
        interest_share["maximum"] = 75
        interest_share["minimum"] = 50
    elif "more-than-25-percent" in control:
        interest_share["maximum"] = 100
        interest_share["minimum"] = 25
    return interest_share

def interest_type(item):
    interest_types = {}
    if not "natures_of_control" in item["data"]: return interest_types
    controls = item["data"]["natures_of_control"]
    for control in controls:
        match control:
            case "ownership-of-shares-75-to-100-percent":
                interest_types["shareholding"] = interest_share(control)
            case "right-to-appoint-and-remove-directors":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "voting-rights-75-to-100-percent":
                interest_types["votingRights"] = interest_share(control)
            case "ownership-of-shares-25-to-50-percent":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-25-to-50-percent":
                interest_types["votingRights"] = interest_share(control)
            case "significant-influence-or-control":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "ownership-of-shares-50-to-75-percent":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-50-to-75-percent":
                interest_types["votingRights"] = interest_share(control)
            case "significant-influence-or-control-as-firm":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-as-firm":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "ownership-of-shares-75-to-100-percent-as-firm":
                interest_types["shareholding"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-as-trust":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "voting-rights-75-to-100-percent-as-firm":
                interest_types["votingRights"] = interest_share(control)
            case "significant-influence-or-control-as-trust":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "ownership-of-shares-75-to-100-percent-as-trust":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-75-to-100-percent-as-trust":
                interest_types["votingRights"] = interest_share(control)
            case "voting-rights-25-to-50-percent-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-25-to-50-percent-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "ownership-of-shares-25-to-50-percent-as-firm":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-25-to-50-percent-as-firm":
                interest_types["votingRights"] = interest_share(control)
            case "significant-influence-or-control-limited-liability-partnership":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "ownership-of-shares-25-to-50-percent-as-trust":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-25-to-50-percent-as-trust":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-appoint-and-remove-members-limited-liability-partnership":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "ownership-of-shares-more-than-25-percent-registered-overseas-entity":
                interest_types["shareholding"] = interest_share(control)
            case "ownership-of-shares-50-to-75-percent-as-firm":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-50-to-75-percent-as-firm":
                interest_types["votingRights"] = interest_share(control)
            case "voting-rights-more-than-25-percent-registered-overseas-entity":
                interest_types["votingRights"] = interest_share(control)
            case "voting-rights-75-to-100-percent-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-75-to-100-percent-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "significant-influence-or-control-registered-overseas-entity":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "ownership-of-shares-50-to-75-percent-as-trust":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-50-to-75-percent-as-trust":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-registered-overseas-entity":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "part-right-to-share-surplus-assets-75-to-100-percent":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "ownership-of-shares-more-than-25-percent-as-trust-registered-overseas-entity":
                interest_types["shareholding"] = interest_share(control)
            case "right-to-appoint-and-remove-person":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "voting-rights-more-than-25-percent-as-trust-registered-overseas-entity":
                interest_types["votingRights"] = interest_share(control)
            case "voting-rights-50-to-75-percent-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-as-trust-registered-overseas-entity":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "right-to-share-surplus-assets-50-to-75-percent-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "significant-influence-or-control-as-trust-registered-overseas-entity":
                interest_types["trustee"] = interest_share(control)
            case "significant-influence-or-control-as-firm-limited-liability-partnership":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "right-to-appoint-and-remove-members-as-firm-limited-liability-partnership":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "voting-rights-25-to-50-percent-as-firm-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-25-to-50-percent-as-firm-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "part-right-to-share-surplus-assets-25-to-50-percent":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "significant-influence-or-control-as-trust-limited-liability-partnership":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "right-to-appoint-and-remove-members-as-trust-limited-liability-partnership":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "right-to-share-surplus-assets-25-to-50-percent-as-trust-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "voting-rights-25-to-50-percent-as-trust-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "voting-rights-75-to-100-percent-as-firm-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-75-to-100-percent-as-firm-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "voting-rights-75-to-100-percent-as-trust-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-75-to-100-percent-as-trust-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "voting-rights-50-to-75-percent-as-firm-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-50-to-75-percent-as-firm-limited-liability-partnership":
                interest_types["shareholding"] = interest_share(control)
            case "part-right-to-share-surplus-assets-50-to-75-percent":
                interest_types["shareholding"] = interest_share(control)
            case "part-right-to-share-surplus-assets-75-to-100-percent-as-trust":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "right-to-appoint-and-remove-person-as-trust":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "voting-rights-50-to-75-percent-as-trust-limited-liability-partnership":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-share-surplus-assets-50-to-75-percent-as-trust-limited-liability-partnership":
                interest_types["rightsToSurplusAssetsOnDissolution"] = interest_share(control)
            case "ownership-of-shares-more-than-25-percent-as-firm-registered-overseas-entity":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-more-than-25-percent-as-firm-registered-overseas-entity":
                interest_types["votingRights"] = interest_share(control)
            case "significant-influence-or-control-as-firm-registered-overseas-entity":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-as-firm-registered-overseas-entity":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "part-right-to-share-surplus-assets-25-to-50-percent-as-trust":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "right-to-appoint-and-remove-person-as-firm":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "part-right-to-share-surplus-assets-75-to-100-percent-as-firm":
                interest_types["shareholding"] = interest_share(control)
            case "part-right-to-share-surplus-assets-25-to-50-percent-as-firm":
                interest_types["shareholding"] = interest_share(control)
            case "part-right-to-share-surplus-assets-50-to-75-percent-as-trust":
                interest_types["shareholding"] = interest_share(control)
            case "part-right-to-share-surplus-assets-50-to-75-percent-as-firm":
                interest_types["shareholding"] = interest_share(control)
            case "ownership-of-shares-more-than-25-percent-as-control-over-trust-registered-overseas-entity":
                interest_types["shareholding"] = interest_share(control)
            case "ownership-of-shares-more-than-25-percent-as-control-over-firm-registered-overseas-entity":
                interest_types["shareholding"] = interest_share(control)
            case "voting-rights-more-than-25-percent-as-control-over-trust-registered-overseas-entity":
                interest_types["votingRights"] = interest_share(control)
            case "voting-rights-more-than-25-percent-as-control-over-firm-registered-overseas-entity":
                interest_types["votingRights"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-as-control-over-trust-registered-overseas-entity":
                interest_types["trustee"] = interest_share(control)
            case "right-to-appoint-and-remove-directors-as-control-over-firm-registered-overseas-entity":
                interest_types["appointmentOfBoard"] = interest_share(control)
            case "significant-influence-or-control-as-control-over-trust-registered-overseas-entity":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
            case "significant-influence-or-control-as-control-over-firm-registered-overseas-entity":
                interest_types["otherInfluenceOrControl"] = interest_share(control)
    return interest_types

#def interest_share(item):
#    interest_share = {"maximum": None,
#                      "minimum": None,
#                      "exclusiveMinimum": None,
#                      "exclusiveMaximum": None}
#    if not "natures_of_control" in item["data"]: return interest_share
#    controls = item["data"]["natures_of_control"]
#    for control in controls:
#        
#        if "75-to-100-percent" in control:
#            interest_share["maximum"] = 100
#            interest_share["minimum"] = 75
#            return interest_share

class UKCOHSource():
    """UK COH specific methods"""
    def __init__(self):
        #self.scheme_data = load_data()
        self.nationality_data = nationalities.load_data()

    def identify_item(self, item):
        """Identify type of GLEIF data"""
        #print("Item:", item)
        if 'CompanyNumber' in item:
            return 'entity'
        elif "company_number" in item:
            if item["data"]["kind"] in (
                #"super-secure-person-with-significant-control", "super-secure-beneficial-owner",
                "persons-with-significant-control-statement", "exemptions"):
                return 'exception'
            else:
                return 'relationship'

    def skip_item(self, item):
        if 'CompanyNumber' in item:
            return False
        else:
            if "kind" in item["data"] and item["data"]["kind"] == "totals#persons-of-significant-control-snapshot":
                return True
            elif "ceased_on" in item["data"] and item["data"]["ceased_on"]:
                return True
            else:
                return False

    def record_id(self, item, item_type):
        """recordId for UK COH item"""
        #item_type = self.identify_item(item)
        if item_type == 'entity':
            if 'CompanyNumber' in item:
                return f"GB-COH-{item['CompanyNumber']}"
            else:
                #if ("identification" in item["data"] and
                #    "registration_number" in item["data"]["identification"]):
                #    return f"GB-COH-{item['data']['identification']['registration_number']}"
                #else:
                #    link_id = item['data']['links']['self'].split('/')[-1]
                #    return f"GB-COH-ENT-{item['company_number']}-{link_id}"
                return build_entity_local_id(item)
        elif item_type == 'relationship':
            link_id = item['data']['links']['self'].split('/')[-1]
            return f"GB-COH-REL-{item['company_number']}-{link_id}"
        elif item_type == 'person':
            link_id = item['data']['links']['self'].split('/')[-1]
            return f"GB-COH-PER-{item['company_number']}-{link_id}"
        elif item_type == 'exception':
            link_id = item['data']['links']['self'].split('/')[-1]
            return f"GB-COH-REL-{item['company_number']}-{link_id}"

    def exception_id(self, record_id):
        """Relationship coresponding recordId for exception"""
        #return record_id.replace('-RR-', '-RE-')
        return record_id.rsplit("-", 1)[0].replace("-RR-", "-RE-")

    def declaration_subject(self, item):
        """declarationSubject for GLEIF item"""
        item_type = self.identify_item(item)
        if item_type == 'entity':
            return f"GB-COH-{item['CompanyNumber']}"
        elif item_type == 'relationship':
            return f"GB-COH-{item['company_number']}"
        elif item_type == 'exception':
            return f"GB-COH-{item['company_number']}"

    def item_updated(self, item):
        """statementDate for GLEIF item"""
        item_type = self.identify_item(item)
        if item_type == 'entity':
            if item["ConfStmtLastMadeUpDate"]:
                updated = item["ConfStmtLastMadeUpDate"]
            else:
                updated = item['ContentDate']
            return build_date(updated)
        elif item_type in ('relationship', 'exception'):
            if "notified_on" in item["data"]:
                return item["data"]["notified_on"]
            else:
                return item["ContentDate"]

    def item_closed(self, item):
        """Is item closed?"""
        item_type = self.identify_item(item)
        #print(item)
        if item_type == 'entity':
            return "Active" in item["CompanyStatus"]
        elif item_type == 'relationship':
            if "ceased_on" in item["data"]:
                return False
            else:
                return True
        elif item_type == 'exception':
            return True

    def name(self, item, item_type):
        """Name for GLEIF item"""
        if item_type == "entity":
            if "CompanyName" in item:
                 return item["CompanyName"]
            else:
                 return item["data"]["name"]
        else:
            name_data = {}
            if "name" in item["data"]:
                name_data["fullname"] = item["data"]["name"]
            if "name_elements" in item["data"]:
                if "forename" in item["data"]["name_elements"]:
                    name_data["firstname"] = item["data"]["name_elements"]["forename"]
                if "middle_name" in item["data"]["name_elements"]:
                    name_data["middlename"] = item["data"]["name_elements"]["middle_name"]
                if "surname" in item["data"]["name_elements"]:
                    name_data["surname"] = item["data"]["name_elements"]["surname"]
                if "title" in item["data"]["name_elements"]:
                    name_data["title"] = item["data"]["name_elements"]["title"]
            return name_data

    def jurisdiction(self, item):
        return "GB"

    @property
    def scheme(self) -> str:
        """Get scheme"""
        return 'GB-COH'

    @property
    def scheme_name(self) -> str:
        """Get scheme name"""
        return "Companies House"

    def scheme_url(self, item):
        """Scheme url"""
        return "https://www.gov.uk/government/organisations/companies-house"

    def identifier(self, item) -> str:
        """Get entity identifier"""
        if 'CompanyNumber' in item:
            return item['CompanyNumber']
        else:
            return item['company_number']

    def person_identifier(self, item) -> str:
        """Get person identifier"""
        return None

    def additional_identifiers(self, item) -> list:
        """Get list of additional identifiers"""
        #if ("RegistrationAuthority" in item['Entity']
        #    and "RegistrationAuthorityID" in item['Entity']["RegistrationAuthority"]
        #    and "RegistrationAuthorityEntityID" in item['Entity']["RegistrationAuthority"]):
        #    authority = item['Entity']["RegistrationAuthority"]
        #    scheme_code, scheme_name = get_scheme(authority["RegistrationAuthorityID"],
        #                                          self.scheme_data,
        #                                          country_code=item['Entity']['LegalJurisdiction'])
        #    #print(authority, scheme_code, scheme_name)
        #    return [{'id': authority["RegistrationAuthorityEntityID"],
        #            'scheme': scheme_code,
        #            'schemeName': scheme_name}]
        #else:
        return []

    def creation_date(self, item):
        """Creation date for item"""
        if "IncorporationDate" in item:
            return build_date(item["IncorporationDate"])
        else:
            return None

    def dissolution_date(self, item):
        """Creation date for item"""
        if "DissolutionDate" in item:
            return build_date(item["DissolutionDate"])
        else:
            return None

    def _extract_entity_address(self, address, data):
        #print("Data:", data)
        if "RegAddress.AddressLine1" in data and data["RegAddress.AddressLine1"]:
            address['address1'] = data["RegAddress.AddressLine1"]
        if "RegAddress.AddressLine2" in data and data["RegAddress.AddressLine2"]:
            address['address2'] = data["RegAddress.AddressLine2"]
        if "RegAddress.CareOf" in data and data["RegAddress.CareOf"]:
            address['address1'] = f"c/o {data['RegAddress.CareOf']}"
        if "RegAddress.POBox" in data and data["RegAddress.POBox"]:
            address['address2'] = data["RegAddress.POBox"]
        if "RegAddress.PostTown" in data and data["RegAddress.PostTown"]:
            address['city'] = data["RegAddress.PostTown"]
        if "RegAddress.PostCode" in data and data["RegAddress.PostCode"]:
            address['postcode'] = data["RegAddress.PostCode"]
        if "RegAddress.County" in data and data["RegAddress.County"]:
            address['region'] = data["RegAddress.County"]
        if "RegAddress.Country" in data and data["RegAddress.Country"]:
            if data["RegAddress.Country"].lower() in ("england", "scotland", "wales", "northern ireland"):
                if not 'region' in address:
                    address['region'] = data["RegAddress.Country"]
                address['country'] = "GB"
            else:
                address['country'] = data["RegAddress.Country"]
        if not 'country' in address:
            address['country'] = "GB"
        address['type'] = "registered"

    def _extract_person_address(self, address, data):
        address_data = data["data"]["address"]
        if "premises" in address_data and address_data["premises"]:
            if "address_line_1" in address_data and address_data["address_line_1"]:
                if address_data["premises"].isnumeric():
                    address['address1'] = f'{address_data["premises"]} {address_data["address_line_1"]}'
                else:
                    address['address1'] = f'{address_data["premises"]}, {address_data["address_line_1"]}'
            else:
                address['address1'] = address_data["premises"]
        else:
            if "address_line_1" in address_data and address_data["address_line_1"]:
                address['address1'] = address_data["address_line_1"]
        if "address_line_2" in address_data and address_data["address_line_2"]:
            address['address2'] = address_data["address_line_2"]
        if "locality" in address_data and address_data["locality"]:
            address['city'] = address_data["locality"]
        if "postal_code" in address_data and address_data["postal_code"]:
            address['postcode'] = address_data["postal_code"]
        if "region" in address_data and address_data["region"]:
            address['region'] = address_data["region"]
        if "country" in address_data and address_data["country"]:
            if address_data["country"].lower() in ("england", "scotland", "wales", "northern ireland"):
                if not 'region' in address:
                    address['region'] = address_data["country"]
                address['country'] = "GB"
            else:
                address['country'] = address_data["country"]
        if not 'country' in address:
            address['country'] = "GB"
        address['type'] = "service"

    def registered_address(self, item) -> dict:
        """Get registered address"""
        address = {}
        #print("Data:", item)
        if 'RegAddress.AddressLine1' in item:
            self._extract_entity_address(address, item)
        if "data" in item and "address" in item["data"]:
            self._extract_person_address(address, item)
        return address

    def business_address(self, item) -> dict:
        """Get registered address"""
        return None

    def create_interested_party(self, item):
        """Create interested party"""
        #print("In create_interested_party (kind):", item["data"]["kind"])
        if item["data"]["kind"] in ("individual-person-with-significant-control",
                                    "individual-beneficial-owner",
                                    "super-secure-person-with-significant-control",
                                    "super-secure-beneficial-owner"):
            return 'person'
        if item["data"]["kind"] in ("corporate-entity-person-with-significant-control",
                                    "corporate-entity-beneficial-owner",
                                    "legal-person-person-with-significant-control",
                                    "legal-person-beneficial-owner"):
            if ("identification" in item["data"] and
                "place_registered" in item["data"]["identification"] and
                "Companies House" in item["data"]["identification"]["place_registered"]):
                return None
            else:
                return 'entity'
        return None

    def relationship_subject(self, item) -> dict:
        """Get relationship subject"""
        item_type = self.identify_item(item)
        if item_type == "relationship":
            return f"GB-COH-{item['company_number']}"
        else:
            return f"GB-COH-{item['company_number']}"

    def relationship_interested_party(self, item) -> dict:
        """Get relationship subject"""
        item_type = self.identify_item(item)
        if item_type == "relationship":
            if item["data"]["kind"] in ("corporate-entity-person-with-significant-control",
                                    "corporate-entity-beneficial-owner",
                                    "legal-person-person-with-significant-control",
                                    "legal-person-beneficial-owner"):
                #return f"GB-COH-{item['data']['identification']['registration_number']}"
                return build_entity_local_id(item)
            elif item["data"]["kind"] in ("individual-person-with-significant-control",
                                    "individual-beneficial-owner",
                                    "super-secure-person-with-significant-control",
                                    "super-secure-beneficial-owner"):
                link_id = item['data']['links']['self'].split('/')[-1]
                return f"GB-COH-REL-{item['company_number']}-{link_id}"
            #return f"XI-LEI-{item['Relationship']['EndNode']['NodeID']}"
        else:
            return exception_unspecified(item)

    def interest_start_date(self, item) -> dict:
        """Get interest start date"""
        #start_date = False
        #if 'RelationshipPeriods' in item['Relationship']:
        #    periods = item['Relationship']['RelationshipPeriods']
        #    for period in periods:
        #        if 'StartDate' in period and 'PeriodType' in period:
        #            if period['PeriodType'] == "RELATIONSHIP_PERIOD":
        #                interestStartDate = period['StartDate']
        #            else:
        #                start_date = period['StartDate']
        #if not start_date:
        #    if not interestStartDate: interestStartDate = ""
        #else:
        #    if not interestStartDate: interestStartDate = start_date
        #return interestStartDate.split("T")[0]
        if "notified_on" in item["data"]:
            return item["data"]["notified_on"]
        else:
            return item['ContentDate']

    def _interest_level(self, item, default):
        """Calculate interest level"""
        relationship_type = item['Relationship']['RelationshipType']
        if relationship_type == "IS_ULTIMATELY_CONSOLIDATED_BY":
            return "indirect"
        elif relationship_type in ("IS_DIRECTLY_CONSOLIDATED_BY", "IS_INTERNATIONAL_BRANCH_OF",
                                   "IS_FUND-MANAGED_BY", "IS_SUBFUND_OF", "IS_FEEDER_TO"):
            return "direct"
        else:
            return default # Other options in data

    def interest_level(self, item):
        """Get interest level"""
        #interestLevel = self._interest_level(item, 'unknown')
        interestLevel = "unknown"
        return interestLevel

    def interest_types(self, item):
        """Get interest types"""
        return interest_type(item)

    def interest_details(self, item):
        """Get interest details"""
        item_type = self.identify_item(item)
        if item_type == "relationship":
            if 'natures_of_control' in item['data']:
                return f"Relationship Type: {item['data']['natures_of_control']}"
            else:
                return f"Unknown Relationship Type for {item['data']['kind']}"
            #return f"Relationship Type: {item['Relationship']['RelationshipType']}"
        else:
            return f"Relationship Type: {item['data']['kind']}"
            #return f"Exception Category: {item['ExceptionCategory']}"

    def source_type(self, item) -> str:
        """Get source type"""
        item_type = self.identify_item(item)
        if item_type == "entity":
            #return (['officialRegister'] if not item['Registration']['ValidationSources'] ==
            #     'FULLY_CORROBORATED' else ['officialRegister', 'verified'])
            return ['officialRegister']
        else:
            return ['officialRegister']

    @property
    def source_description(self) -> str:
        """Get source description"""
        return 'Companies House'

    @property
    def source_url(self) -> str:
        """Get source url"""
        return 'https://download.companieshouse.gov.uk/en_output.html'

    @property
    def entity_name(self) -> str:
        """Get GLEIF entity name"""
        return 'Company'

    def status(self, item) -> str:
        """Get GLEIF entity status"""
        if 'CompanyStatus' in item:
            return item['CompanyStatus']

    def person_type(self, item):
        if item["data"]["kind"] in ("super-secure-person-with-significant-control",
                                    "super-secure-beneficial-owner"):
            return "anonymousPerson"
        else:
            return "knownPerson" # Alternatives: anonymousPerson unknownPerson

    def person_nationalities(self, item):
        """Person nationalities"""
        if "nationality" in item["data"]:
            country = nationalities.lookup_nationality(self.nationality_data, item["data"]["nationality"])
            if country:
                return [country]
            else:
                return []
        else:
            return []

    def person_place_of_birth(self, item):
        """Person place of birth"""
        return None

    def person_birth_date(self, item):
        """Persion date of birth"""
        if "date_of_birth" in item["data"]:
            return f'{item["data"]["date_of_birth"]["year"]}-{item["data"]["date_of_birth"]["month"]:02d}'
        return None

    def person_death_date(self, item):
        """Person date of death"""
        return None

    def person_tax_residency(self, item):
        """Person tax residency country"""
        if "country_of_residence" in item["data"]:
            country = country_code(item["data"]["country_of_residence"])
            if country:
                return [country]
        return []

    def item_link(self, item, item_type):
        """Link to more info on entity"""
        if item_type == "entity":
            if "URI" in item and item["URI"]:
                return item["URI"]
            else:
                return None
        else:
            if "links" in item["data"] and 'self' in item["data"]["links"]:
                 if "persons-with-significant" in item["data"]["links"]["self"]:
                     link = item["data"]["links"]["self"].split("-statements")[0]
                     return "https://find-and-update.company-information.service.gov.uk{link}"
            return None

    def retrived_date(self, item):
        """Date that data was retrieve"""
        if "ContentDate" in item:
            return item["ContentDate"]
        else:
            return current_date_iso()

    def entity_details(self, item):
        """Link to more info on entity"""
        if "CompanyCategory" in item and item["CompanyCategory"]:
            return item["CompanyCategory"]
        return None

    def has_public_listing(self, item):
        """Does entity have public listing"""
        if "CompanyCategory" in item and item["CompanyCategory"]:
            company_type = item["CompanyCategory"].lower()
            if "public" in company_type and "company" in company_type:
                return True
        return False
