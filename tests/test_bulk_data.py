import json
import pytest

from pathlib import Path

from bodspipelines.infrastructure.pipeline import Source
from bodspipelines.infrastructure.processing.bulk_data import BulkData
from bodspipelines.infrastructure.processing.json_data import JSONData
from bodspipelines.infrastructure.processing.csv_data import CSVData
from bodsukpscpipeline.utils import UKCOHData, identify_uk_coh
from bodsukpscpipeline.transforms import RemovePeriodsFromProperties, AddContentDate

class TestUKCompanyData:
    """Test download of single file"""
    source = 'company-data'

    @pytest.fixture(scope="class")
    def temp_dir(self, tmp_path_factory):
        """Fixture to create temporary directory"""
        return tmp_path_factory.getbasetemp()

    @pytest.fixture(scope="class")
    def stage_dir(self, temp_dir):
        """Fixture to create subdirectory"""
        output_dir = Path(temp_dir) / "data" / self.source
        output_dir.mkdir(parents=True)
        return output_dir

#    @pytest.mark.asyncio
#    async def test_company_data(self, stage_dir):
#        """Test downloading PSC data"""
#        print(stage_dir)
#
#        # Defintion of CH basic company data source
#        company_source = Source(name="company-data",
#                                origin=BulkData(display="UK Basic Company Data",
#                                                data=UKCOHData(url="https://download.companieshouse.gov.uk/BasicCompanyData-2024-11-01-part1_7.zip",
#                                                               update_frequency="monthly"),
#                                                size=6400,
#                                                directory="uk-companies"),
#                                datatype=CSVData()
#                                )
#
#        transform = RemovePeriodsFromProperties(identify=identify_uk_coh)
#
#        async for header, item in company_source.process(stage_dir, updates=True):
#            async for data in transform.process(item, None, None):
#                print(json.dumps(data))
#
#        assert False

class TestUKPSCData:
    """Test download of single file"""
    source = 'psc-data'

    @pytest.fixture(scope="class")
    def temp_dir(self, tmp_path_factory):
        """Fixture to create temporary directory"""
        return tmp_path_factory.getbasetemp()

    @pytest.fixture(scope="class")
    def stage_dir(self, temp_dir):
        """Fixture to create subdirectory"""
        output_dir = Path(temp_dir) / "data" / self.source
        output_dir.mkdir(parents=True)
        return output_dir

    @pytest.mark.asyncio
    async def test_psc_data(self, stage_dir):
        """Test downloading PSC data"""
        print(stage_dir)


        # Defintion of CH PSC data source
        psc_source = Source(name="psc-data",
                                origin=BulkData(display="UK People with significant control (PSC) Data",
                                                data=UKCOHData(url="https://download.companieshouse.gov.uk/psc-snapshot-2024-11-23_28of28.zip",
                                                               update_frequency="daily"),
                                                size=6500,
                                                directory="uk-psc"),
                                datatype=JSONData(header=-1)
                                )

        transform = AddContentDate(identify=identify_uk_coh)

        async for header, item in psc_source.process(stage_dir, updates=True):
            async for data in transform.process(item, None, header):
                print(json.dumps(item))

        print(header)

        assert False

