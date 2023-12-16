import requests
import time
from datetime import datetime
import json

# get api key from https://developer.jcdecaux.com/#/home
url = "https://api.jcdecaux.com/vls/v1/stations?contract=ljubljana&apiKey={api_key}"

counter = 0
while True:

    timestamp = time.time()
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_date_time = dt_object.strftime('%Y-%m-%d_%H-%M-%S')

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        filepath = f"data/{counter}_stations_at_{formatted_date_time}.json"
        
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    else:
        print(f"Error: {response.status_code}")

    counter += 1
    time.sleep(60)
