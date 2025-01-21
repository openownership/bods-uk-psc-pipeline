import os
import time
import elastic_transport
import asyncio
from datetime import datetime

from bodspipelines.infrastructure.pipeline import Source, Stage, Pipeline
from bodspipelines.infrastructure.inputs import KinesisInput
from bodspipelines.infrastructure.storage import Storage
from bodspipelines.infrastructure.clients.elasticsearch_client import ElasticsearchClient
from bodspipelines.infrastructure.outputs import Output, OutputConsole, NewOutput, KinesisOutput
from bodspipelines.infrastructure.processing.bulk_data import BulkData
from bodspipelines.infrastructure.processing.csv_data import CSVData
from bodspipelines.infrastructure.processing.json_data import JSONData
from bodspipelines.infrastructure.updates import ProcessUpdates

from bodspipelines.infrastructure.indexes import bods_index_properties
from bodspipelines.infrastructure.utils import identify_bods, load_last_run, save_run

#from bodspipelines.pipelines.gleif.indexes import gleif_index_properties
#from bodspipelines.pipelines.gleif.transforms import Gleif2Bods, AddContentDate, RemoveEmptyExtension
#from bodspipelines.pipelines.gleif.indexes import (lei_properties, rr_properties, repex_properties,
#                                          match_lei, match_rr, match_repex,
#                                          id_lei, id_rr, id_repex)
#from bodspipelines.pipelines.gleif.utils import gleif_download_link, GLEIFData, identify_gleif
#from bodspipelines.pipelines.gleif.updates import GleifUpdates
#from bodspipelines.infrastructure.utils import identify_bods, load_last_run, save_run

from .indexes import uk_psc_index_properties
from .source import UKCOHSource
from .utils import UKCOHData, identify_uk_coh, psc_exclude
from .transforms import AddContentDate, RemovePeriodsFromProperties

# Defintion of CH basic company data source
company_source = Source(name="company-data",
                        origin=BulkData(display="UK Basic Company Data",
                                        data=UKCOHData(url="https://download.companieshouse.gov.uk/BasicCompanyData-2024-11-01-part1_7.zip",
                                                       update_frequency="monthly"),
                                        size=6400,
                                        directory="uk-companies"),
                        datatype=CSVData()
                       )

# Defintion of CH PSC data source
psc_source = Source(name="psc-data",
                    origin=BulkData(display="UK People with significant control (PSC) Data",
                                    data=UKCOHData(url="https://download.companieshouse.gov.uk/psc-snapshot-2024-11-23_1of28.zip",
                                                   update_frequency="daily"),
                                    size=6500,
                                    directory="uk-psc"),
                    datatype=JSONData(header=-1, exclude=psc_exclude)
                   )

# Easticsearch storage for UK PSC data
uk_psc_storage = ElasticsearchClient(indexes=uk_psc_index_properties)

# GLEIF data: Store in Easticsearch and output new to Kinesis stream
output_new = NewOutput(storage=Storage(storage=uk_psc_storage),
                       output=KinesisOutput(stream_name=os.environ.get('SOURCE_KINESIS_STREAM')),
                       identify=identify_uk_coh)

# Definition of UK PSC data pipeline ingest stage
ingest_stage = Stage(name="ingest",
              sources=[company_source, psc_source],
              processors=[AddContentDate(identify=identify_uk_coh),
                          RemovePeriodsFromProperties(identify=identify_uk_coh)],
              outputs=[output_new])

# Kinesis stream of UK PSC data from ingest stage
uk_psc_source = Source(name="uk-psc",
                      origin=KinesisInput(stream_name=os.environ.get('SOURCE_KINESIS_STREAM')),
                      datatype=JSONData())

# Easticsearch storage for BODS data
bods_storage = ElasticsearchClient(indexes=bods_index_properties,
                                   index_just_id = ["entity", "person", "relationship"])

# BODS data: Store in Easticsearch and output new to Kinesis stream
bods_output_new = NewOutput(storage=Storage(storage=bods_storage),
                            output=KinesisOutput(stream_name=os.environ.get('BODS_KINESIS_STREAM')),
                            identify=identify_bods)

# Definition of UK PSC data pipeline transform stage
transform_stage = Stage(name="transform",
              sources=[uk_psc_source],
              processors=[ProcessUpdates(id_name='GB-COH',
                                         transform=UKCOHSource(), # Gleif2Bods(identify=identify_gleif),
                                         storage=Storage(storage=bods_storage),
                                         #updates=GleifUpdates()
                                         )],
              outputs=[bods_output_new])

# Definition of UK PSC data pipeline
pipeline = Pipeline(name="uk-psc", stages=[ingest_stage, transform_stage])

# Setup storage indexes
async def setup_indexes():
    await uk_psc_storage.setup_indexes()
    await bods_storage.setup_indexes()

# Load run
async def load_previous(name):
    bods_storage_run = ElasticsearchClient(indexes=bods_index_properties)
    await bods_storage_run.setup()
    storage_run = Storage(storage=bods_storage_run)
    return await load_last_run(storage_run, name=name)

# Save data on current pipeline run
async def save_current_run(name, start_timestamp):
    bods_storage_run = ElasticsearchClient(indexes=bods_index_properties)
    await bods_storage_run.setup()
    storage_run = Storage(storage=bods_storage_run)
    run_data = {'stage_name': name,
                'start_timestamp': str(start_timestamp),
                'end_timestamp': datetime.now().timestamp()}
    await save_run(storage_run, run_data)

# Setup pipeline storage
def setup():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_indexes())

