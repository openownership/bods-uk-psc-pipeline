import json
import os
import pytest

from bodspipelines.infrastructure.utils import current_date_iso

from .config import set_environment_variables
from .run_pipeline import run_transform_pipeline

# Setup environment variables
set_environment_variables()

@pytest.fixture(scope="module")
def wait_for_es(module_scoped_container_getter):
    service = module_scoped_container_getter.get("bods_pipeline_uk_psc_es_test").network_info[0]
    os.environ['ELASTICSEARCH_HOST'] = service.hostname
    os.environ['ELASTICSEARCH_PORT'] = service.host_port
    return service

@pytest.fixture
def company_data_1():
    """UK Companies House company data"""
    with open("tests/fixtures/company-data-1.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_sample_10000():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-first-10000.json", "r") as read_file:
        return json.load(read_file)

#@pytest.mark.asyncio
#@pytest.mark.order(1)
#async def test_company_data_1(wait_for_es, company_data_1):
#    """Test transform pipeline stage on relationship update when lei updated"""
#
#    output_stream = await run_transform_pipeline(company_data_1)
#
#    print(json.dumps(output_stream, indent=2))
#
#    assert len(output_stream) == 2


@pytest.mark.asyncio
@pytest.mark.order(2)
async def test_psc_sample_10000(wait_for_es, psc_data_sample_10000):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_sample_10000)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2
