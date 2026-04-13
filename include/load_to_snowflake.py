import snowflake.connector
from .config import snow_password, snow_account, snow_user, url_endpoint, access_key, secret_key
import boto3
import os

# Snowflake connection
ctx = snowflake.connector.connect(
    user=snow_user,
    password=snow_password,
    account=snow_account,
    warehouse='COMPUTE_WH',
    database='TRIPLENS',
    schema='RAW'
)

cs = ctx.cursor()

# MinIO client
client = boto3.client(
    's3',
    endpoint_url=url_endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=boto3.session.Config(signature_version='s3v4'),
    verify=False
)

def transfer_minio_json_to_snowflake(bucket: str, file_key: str, target_table: str) -> None:

    # Keep just filename
    filename = os.path.basename(file_key)
    local_temp_path = os.path.join(os.getcwd(), filename).replace("\\", "/")

    # Download file from MinIO
    client.download_file(bucket, file_key, local_temp_path)

    try:
        # Use schema
        cs.execute("USE SCHEMA TRIPLENS.RAW")

        # File format
        cs.execute("""
            CREATE OR REPLACE FILE FORMAT TRIPLENS_JSON_FMT
            TYPE = 'JSON'
        """)

        # Stage
        cs.execute("""
            CREATE OR REPLACE STAGE TRIPLENS_STAGE
            FILE_FORMAT = TRIPLENS_JSON_FMT
        """)

        # Table
        cs.execute("""
            CREATE OR REPLACE TABLE TRIPLENS.RAW.COUNTRIES_RAW (
                ingestion_ts TIMESTAMP_NTZ,
                src_file STRING,
                payload VARIANT
            )
        """)

        # PUT file to Snowflake stage
        cs.execute(f"""
            PUT 'file://{local_temp_path}'
            @TRIPLENS_STAGE
            AUTO_COMPRESS=TRUE
            OVERWRITE=TRUE
        """)

        # Clear table
        cs.execute(f"TRUNCATE TABLE {target_table}")

        # COPY INTO table
        cs.execute(f"""
            COPY INTO {target_table} (ingestion_ts, src_file, payload)
            FROM (
                SELECT
                    CURRENT_TIMESTAMP(),
                    METADATA$FILENAME,
                    $1
                FROM @TRIPLENS_STAGE
            )
            FILE_FORMAT = (TYPE = JSON)
            ON_ERROR = 'ABORT_STATEMENT'
        """)

        print(f"Successfully loaded {file_key} into {target_table}")
    except Exception as e:
      print(e)

    finally:
        # Cleanup temp file
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)