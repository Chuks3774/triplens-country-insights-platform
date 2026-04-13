import time
import requests
from requests.exceptions import HTTPError, RequestException
from .config import urls
def api_connect():
    complete_data = []

    try:
        response = requests.get(urls["url_1"])
        response.raise_for_status()

        data_1 = response.json()

        # wait for 2 seconds
        time.sleep(2)

        response_2 = requests.get(urls["url_2"])
        response_2.raise_for_status()

        data_2 = response_2.json()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except RequestException as req_err:
        print(f"A general request error occurred: {req_err}")

    for response_1, response_2 in zip(data_1, data_2):
        complete_data.append({**response_1, **response_2})

    return complete_data