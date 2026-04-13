from datetime import datetime, timedelta
from airflow import DAG

from include.extract import api_connect
from include.load_to_bucket import load_to_bucket
from include.load_to_snowflake import transfer_minio_json_to_snowflake

from airflow.sdk import task


default_args = {
    "owner": "triplens",
    "start_date": datetime(2026, 3, 30),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    'schedule': '@hourly'
}


@task()
def extract_data_from_api():
    api_response = api_connect()
    return api_response


@task()
def load_data_to_s3(api_response):
    load_to_bucket(api_response)


@task()
def transfer_to_snowflake():
    transfer_minio_json_to_snowflake(
        bucket="triplens-bucket",
        file_key="bronze/countries_raw.json",
        target_table="COUNTRIES_RAW",
    )


with DAG(
    dag_id='triplens-explorer',
    description='TripLens Countries Explorer',
    default_args=default_args,
    catchup=False,
    tags=["triplens-explorer", "tourism", "minio", "snowflake","dbt"],
) as dag:

    api_response = extract_data_from_api()


    # Task dependencies
    (
    api_response 
    >> load_data_to_s3(api_response) 
    >> transfer_to_snowflake()
    )