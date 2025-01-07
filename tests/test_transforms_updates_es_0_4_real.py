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
def psc_data_1():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-1.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_2():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-2.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_3():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-3.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_4():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-4.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_5():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-5.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_6():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-6.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_7():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-7.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_8():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-8.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_9():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-9.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_10():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-10.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_11():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-11.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_12():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-12.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_13():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-13.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_14():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-14.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_15():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-15.json", "r") as read_file:
        return json.load(read_file)

@pytest.fixture
def psc_data_16():
    """UK Companies House PSC data"""
    with open("tests/fixtures/psc-data-16.json", "r") as read_file:
        return json.load(read_file)

@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_company_data_1(wait_for_es, company_data_1):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(company_data_1)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2


@pytest.mark.asyncio
@pytest.mark.order(2)
async def test_psc_data_1(wait_for_es, psc_data_1):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_1)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(3)
async def test_psc_data_2(wait_for_es, psc_data_2):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_2)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 1

@pytest.mark.asyncio
@pytest.mark.order(4)
async def test_psc_data_3(wait_for_es, psc_data_3):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_3)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(5)
async def test_psc_data_4(wait_for_es, psc_data_4):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_4)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(6)
async def test_psc_data_5(wait_for_es, psc_data_5):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_5)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(7)
async def test_psc_data_6(wait_for_es, psc_data_6):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_6)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(8)
async def test_psc_data_7(wait_for_es, psc_data_7):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_7)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(9)
async def test_psc_data_8(wait_for_es, psc_data_8):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_8)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 5

@pytest.mark.asyncio
@pytest.mark.order(10)
async def test_psc_data_9(wait_for_es, psc_data_9):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_9)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(11)
async def test_psc_data_10(wait_for_es, psc_data_10):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_10)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

@pytest.mark.asyncio
@pytest.mark.order(12)
async def test_psc_data_11(wait_for_es, psc_data_11):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_11)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

    assert False

@pytest.mark.asyncio
@pytest.mark.order(13)
async def test_psc_data_12(wait_for_es, psc_data_12):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_12)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

    assert False

@pytest.mark.asyncio
@pytest.mark.order(14)
async def test_psc_data_13(wait_for_es, psc_data_13):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_13)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

    assert False

@pytest.mark.asyncio
@pytest.mark.order(15)
async def test_psc_data_14(wait_for_es, psc_data_14):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_14)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

    assert False

@pytest.mark.asyncio
@pytest.mark.order(16)
async def test_psc_data_15(wait_for_es, psc_data_15):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_15)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

    assert False

@pytest.mark.asyncio
@pytest.mark.order(17)
async def test_psc_data_16(wait_for_es, psc_data_16):
    """Test transform pipeline stage on relationship update when lei updated"""

    output_stream = await run_transform_pipeline(psc_data_16)

    print(json.dumps(output_stream, indent=2))

    assert len(output_stream) == 2

    assert False
