import os

def set_environment_variables():
    """Set environment variables"""
    os.environ['ELASTICSEARCH_PROTOCOL'] = 'http'
    os.environ['ELASTICSEARCH_HOST'] = 'localhost'
    os.environ['ELASTICSEARCH_PORT'] = '9876'
    os.environ['ELASTICSEARCH_PASSWORD'] = '********'
    os.environ['BODS_AWS_REGION'] = "eu-west-1"
    os.environ['BODS_AWS_ACCESS_KEY_ID'] ="********************"
    os.environ['BODS_AWS_SECRET_ACCESS_KEY'] = "****************************************"
