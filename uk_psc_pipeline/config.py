import os
import time
import elastic_transport
import asyncio
from datetime import datetime

from bodspipelines.infrastructure.pipeline import Source, Stage, Pipeline
from bodspipelines.infrastructure.inputs import KinesisInput
from bodspipelines.infrastructure.storage import Storage
from bodspipelines.infrastructure.clients.elasticsearch_client import ElasticsearchClient
from bodspipelines.infrastructure.clients.redis_client import RedisClient
from bodspipelines.infrastructure.outputs import Output, OutputConsole, NewOutput, KinesisOutput
from bodspipelines.infrastructure.processing.bulk_data import BulkData
from bodspipelines.infrastructure.processing.xml_data import XMLData
from bodspipelines.infrastructure.processing.json_data import JSONData
from bodspipelines.infrastructure.updates import ProcessUpdates

from bodspipelines.pipelines.gleif.indexes import gleif_index_properties
from bodspipelines.infrastructure.indexes import bods_index_properties

from bodspipelines.pipelines.gleif.transforms import Gleif2Bods, AddContentDate, RemoveEmptyExtension
from bodspipelines.pipelines.gleif.indexes import (lei_properties, rr_properties, repex_properties,
                                          match_lei, match_rr, match_repex,
                                          id_lei, id_rr, id_repex)
from bodspipelines.pipelines.gleif.utils import gleif_download_link, GLEIFData, identify_gleif
from bodspipelines.pipelines.gleif.updates import GleifUpdates
from bodspipelines.infrastructure.utils import identify_bods, load_last_run, save_run

# Defintion of LEI-CDF v3.1 XML date source
lei_source = Source(name="lei",
                    origin=BulkData(display="LEI-CDF v3.1",
                       data=GLEIFData(url="https://goldencopy.gleif.org/api/v2/golden-copies/publishes/lei2/latest",
                                      data_date="2024-01-01"),
                              size=41491,
                              directory="lei-cdf"),
                    datatype=XMLData(item_tag="LEIRecord",
                                     namespace={"lei": "http://www.gleif.org/data/schema/leidata/2016",
                                          "gleif": "http://www.gleif.org/data/schema/golden-copy/extensions/1.0"},
                                     filter=['NextVersion', 'Extension']))

# Defintion of RR-CDF v2.1 XML date source
rr_source = Source(name="rr",
                   origin=BulkData(display="RR-CDF v2.1",
                       data=GLEIFData(url="https://goldencopy.gleif.org/api/v2/golden-copies/publishes/rr/latest",
                                      data_date="2024-01-01"),
                       size=2823,
                       directory="rr-cdf"),
                   datatype=XMLData(item_tag="RelationshipRecord",
                            namespace={"rr": "http://www.gleif.org/data/schema/rr/2016",
                                       "gleif": "http://www.gleif.org/data/schema/golden-copy/extensions/1.0"},
                            filter=['NextVersion', ]))

# Defintion of Reporting Exceptions v2.1 XML date source
repex_source = Source(name="repex",
                      origin=BulkData(display="Reporting Exceptions v2.1",
                      data=GLEIFData(url="https://goldencopy.gleif.org/api/v2/golden-copies/publishes/repex/latest",
                                     data_date="2024-01-01"),
                           size=3954,
                           directory="rep-ex"),
                      datatype=XMLData(item_tag="Exception",
                                 header_tag="Header",
                                 namespace={"repex": "http://www.gleif.org/data/schema/repex/2016",
                                            "gleif": "http://www.gleif.org/data/schema/golden-copy/extensions/1.0"},
                                 filter=['NextVersion', ]))

# Easticsearch storage for GLEIF data
gleif_storage = ElasticsearchClient(indexes=gleif_index_properties)

# GLEIF data: Store in Easticsearch and output new to Kinesis stream
output_new = NewOutput(storage=Storage(storage=gleif_storage),
                       output=KinesisOutput(stream_name=os.environ.get('GLEIF_KINESIS_STREAM')))

# Definition of GLEIF data pipeline ingest stage
ingest_stage = Stage(name="ingest",
              sources=[lei_source, rr_source, repex_source],
              processors=[AddContentDate(identify=identify_gleif),
                          RemoveEmptyExtension(identify=identify_gleif)],
              outputs=[output_new])

# Kinesis stream of GLEIF data from ingest stage
gleif_source = Source(name="gleif",
                      origin=KinesisInput(stream_name=os.environ.get('GLEIF_KINESIS_STREAM')),
                      datatype=JSONData())

# Easticsearch storage for BODS data
bods_storage = ElasticsearchClient(indexes=bods_index_properties)

# BODS data: Store in Easticsearch and output new to Kinesis stream
bods_output_new = NewOutput(storage=Storage(storage=bods_storage),
                            output=KinesisOutput(stream_name=os.environ.get('BODS_KINESIS_STREAM')),
                            identify=identify_bods)

# Definition of GLEIF data pipeline transform stage
transform_stage = Stage(name="transform",
              sources=[gleif_source],
              processors=[ProcessUpdates(id_name='XI-LEI',
                                         transform=Gleif2Bods(identify=identify_gleif),
                                         storage=Storage(storage=bods_storage),
                                         updates=GleifUpdates())],
              outputs=[bods_output_new])

# Definition of GLEIF data pipeline
pipeline = Pipeline(name="gleif", stages=[ingest_stage, transform_stage])

# Setup storage indexes
async def setup_indexes():
    await gleif_storage.setup_indexes()
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

