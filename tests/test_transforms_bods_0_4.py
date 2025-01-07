import pytest
import os
import json

from bodspipelines.infrastructure.bods.transforms import (transform_entity, transform_person,
                                                          transform_relationship, transform_exception)
from bodsukpscpipeline.source import UKCOHSource

@pytest.fixture
def company_data_1():
    """UK Companies House company data"""
    with open("tests/fixtures/company-data-1.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_1():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-1.json", "r") as read_file:
        return json.load(read_file)

def test_company_transform(company_data_1):
    print(company_data_1)
    source = UKCOHSource()
    status = 'new'
    bods_statement = transform_entity(source, company_data_1[0], status)
    print(json.dumps(bods_statement, indent=2))
    assert False

def test_relationship_transform(psc_data_1):
    print(psc_data_1)
    source = UKCOHSource()
    status = 'new'
    bods_statement = transform_relationship(source, psc_data_1[0], status)
    print(json.dumps(bods_statement, indent=2))
    assert False

def test_person_transform(psc_data_1):
    print(psc_data_1)
    source = UKCOHSource()
    status = 'new'
    bods_statement = transform_person(source, psc_data_1[0], status)
    print(json.dumps(bods_statement, indent=2))
    assert False
