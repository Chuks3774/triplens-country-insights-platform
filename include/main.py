from extract import api_connect
from load_to_bucket import load_to_bucket
from load_to_snowflake import transfer_minio_json_to_snowflake

def main():
    api_response = api_connect()
    load_to_bucket(api_response)

    transfer_minio_json_to_snowflake(
        bucket="triplens-bucket",
        file_key="bronze/countries_raw.json",
        target_table="COUNTRIES_RAW",
    )

    return None

main()