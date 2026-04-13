from .config import client
import json
import boto3
from botocore.exceptions import ClientError

def load_to_bucket(data):

    bucket_name = "triplens-bucket"
    folder_path = "bronze"
    object_name = f"{folder_path}/countries_raw.json"


    # check if bucket exists and create it if not
    try:
        client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            client.create_bucket(Bucket=bucket_name)
            print(f"{bucket_name} created")

    data = json.dumps(data, ensure_ascii=False).encode("utf-8")

    # Upload the data stream
    client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=data,
        ContentType="application/json",
    )
    print('data loaded successfully')

    return None