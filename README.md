# BODS UK PSC Pipeline

Pipeline for producing statements in line with version 0.4 of the Beneficial Ownership Data Standard (BODS) 
using UK Companies House People with Significant Control (PSC) and basic company data. This pipeline depends on 
the [bodspipelines](https://github.com/openownership/bodspipelines) shared library for its core functionality.

## Data

The pipeline ultimately performs the following data transformations:

* UK Companies House Basic Company Data (CSV) -> BODS 0.4 Entity Records (JSON)
* UK Companies House Persons With Significant Control (JSON) -> BODS 0.4 Person or Entity Records (JSON)
* UK Companies House Persons With Significant Control (JSON) -> BODS 0.4 Relationship Records (JSON)

However this is done in 2 stages, Ingest and Transform, so itermediate JSON data, which is a direct JSON
representation of the raw data, with extra fields added, is output from the ingest stage. In particular a 
ContentDate (date of the input data) attribute is added, but the infrastucture potentially allows any
augmentation of the raw data. 

## Architecture

The pipeline is built to run on Amazon Web Services (AWS), using AWS Kinesis data streams to connect
the stages together and an AWS EC2 instance to run the pipeline stages. AWS Firehose delivery 
streams can optionally be connected to Kinesis data streams to save intermediate or final data, for instance
to an S3 bucket.

Storage between pipeline runs is achieved using Elasticsearch, which runs in the same EC2 instance
as the pipeline code. 

This repository contains the UK Companies House specific code, see bodsukpscpipeline/config.py for the 
pipeline configuration and bodsukpscpipeline/source.py for the data transformations, in methods of the
UKCOHSource class. 

This repository also contains all the scripts and Docker
container configuration necessary to run the pipeline on an EC2 instance.

The bulk of the pipeline code is contained within the 
[openownership/bodspipelines](https://github.com/openownership/bodspipelines) 
repository, which is a shared library intended to support all BODS pipelines in future. 

## Ingest Stage

The Ingest pipeline stage downloads the [UK Companies House Basic Company Data](https://download.companieshouse.gov.uk/en_output.html)
and the [UK Companies House Persons With Significant Control](https://download.companieshouse.gov.uk/en_pscdata.html)
and parses the CSV/JSON data, augments it and writes it to JSON which written to a Kinesis data stream (as well as
being storage in Elasticsearch). The uncompressed UK Companies House data takes up approximately 12GB of diskspace.

## Transform Stage

The Transform pipeline stage reads data from the Kinesis stream which is output by the Ingest stage.
The stage transforms the JSON representation of UK Companies House data into Beneficial Ownership Data Standard (BODS)
statements.

# Usage

## Requirements

The pipeline is designed to be run on Amazon Web Services (AWS) infrastruture and has roughly the following requirements:

* t2.2xlarge (or equilvalent) EC2 instance with approximately 48GB of storage
  - Caching of crtitical data (to allow reasonable performance) means the pipeline transform process takes over 20GB of memory alone, and if elasticsearch is being run on same instance then several (in general an instance with 32GB of memory will be required)
  - Currently the elasticsearch storage uses on the order of 28GB of diskspace, and input data about 12GB
* 2 Kinesis streams to connect pipeline stages
* Optionally Firehose delivery streams connecting data streams to S3 buckets

The ingestion of the full dataset takes 6.7 hours and the transform stage takes about 14.5 hours.

## Setup

Create an EC2 instance (see requirements above), install docker, setup Kinesis data streams for each 
pipeline stage to output to, and optionally create Kinesis delivery streams to connected
to output data to S3 buckets.	

### Configuration

Create a env.sh file with the environment variable below (also see env.sh.example file).
where the Kinesis streams are hosted.

```
BODS_AWS_REGION=
BODS_AWS_ACCESS_KEY_ID=
BODS_AWS_SECRET_ACCESS_KEY=
ELASTICSEARCH_HOST=bods_pipeline_uk_psc_es
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_PROTOCOL=http
SOURCE_KINESIS_STREAM=
BODS_KINESIS_STREAM=
LOCAL_DATA_DIRECTORY=uk
KINESIS_STATUS_DIRECTORY=status
```

### One-time Setup

Run on EC2 instance:

```
bin/build
bin/install_pipeline
bin/setup_indexes
```

### Ingest Pipeline Stage

Run on EC2 instance:

```
nohup bin/ingest_updates &> ingest_updates.log &
```

or

```
nohup bin/transform_updates &> transform_updates.log &
```

### Tests

The tests can be run with pytest. Note that docker is used to build elasticsearch
for the tests, so needs to be available on the machine running the tests.

### Testing

Note it is possible to run the pipeline on a local machine for testing purposes
but this will degrade performance, possibly very significantly depending on the
the bandwidth of the network connection between the machine and the data center
where the Kinesis streams are hosted.

