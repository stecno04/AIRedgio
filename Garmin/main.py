import time
import requests
import hashlib
import hmac
import base64

import webbrowser
from urllib.parse import quote
import matplotlib.pyplot as plt
import datetime
import pandas as pd

def toda():
    today = datetime.date.today()
    print(today)
    # start mezzanote unix
    start = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    start = int(start.timestamp())
    # end mezzanote unix
    end = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
    end = int(end.timestamp())
    
    return start, end
def generate_oauth_nonce():
    # Nonce is a unique value, here we use a simple timestamp
    return str(int(time.time()))

def generate_oauth_timestamp():
    # Current timestamp in seconds
    return str(int(time.time()))

def generate_oauth_signature(base_url, method, params, consumer_secret, token_secret, consumer_key, access_token):
    # Collecting all parameters
    all_params = {
        **params,
        'oauth_consumer_key': consumer_key,
        'oauth_token': access_token,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': generate_oauth_timestamp(),
        'oauth_nonce': generate_oauth_nonce(),
        'oauth_version': '1.0'
    }
    
    # Sorting the parameters and encoding them
    encoded_params = '&'.join([f"{quote(k, safe='')}={quote(str(all_params[k]), safe='')}" for k in sorted(all_params)])

    # Constructing the base string
    base_string = '&'.join([method, quote(base_url, safe=''), quote(encoded_params, safe='')])

    # Constructing the signing key
    signing_key = f"{quote(consumer_secret, safe='')}&{quote(token_secret, safe='')}"
    
    # Generating the signature
    hashed = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()

    return signature

def make_api_request(start_time, end_time, index):
    base_url = f"https://apis.garmin.com/wellness-api/rest/{index}"
    params = {
        "uploadStartTimeInSeconds": start_time,
        "uploadEndTimeInSeconds": end_time
    }

    # Add your OAuth 1.0 authentication keys here
    consumer_key = "4abf826a-87c6-434c-a7f0-b65c14fcf3f4"
    consumer_secret = "BiLzHopVh8h30KlnspZpwVvlierOZXHzFKu"
    access_token = "3b76468e-b934-45de-a90a-673add971181"
    token_secret = "XogfActj8BmA1QVHh3laaklbFxwuXkO52mo"

    method = 'GET'  # or 'POST' if it's a POST request
    oauth_signature = generate_oauth_signature(base_url, method, params, consumer_secret, token_secret, consumer_key, access_token)

    headers = {
        "Authorization": f'OAuth oauth_consumer_key="{consumer_key}", '
                         f'oauth_token="{access_token}", '
                         f'oauth_signature_method="HMAC-SHA1", '
                         f'oauth_timestamp="{generate_oauth_timestamp()}", '
                         f'oauth_nonce="{generate_oauth_nonce()}", '
                         f'oauth_version="1.0", '
                         f'oauth_signature="{quote(oauth_signature, safe="")}"'
    }

    try:
        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Process the data as needed
            return data
        else:
            print(f"{index}: Error: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"{index}: Error making API request: {e}")

miobattito = pd.DataFrame()
while True:
    try: 
        start, end = toda()
        data = make_api_request(start, end, "dailies")[-1]["timeOffsetHeartRateSamples"]
        last_key = list(data.keys())[-4:]
        last_value = list(data.values())[-4:]
        for i in range(len(last_key)):
            # lastkey formato today+hh:mm:ss
            ore = int(int(last_key[i])/60/60)
            minuti = int((int(last_key[i])/60)%60)
            secondi = int((int(last_key[i]))%60)
            tod = [datetime.date.today()]
            y,m,g = tod[0].year, tod[0].month, tod[0].day
            last_key[i] =pd.to_datetime(datetime.datetime(y, m, g, ore, minuti, secondi))
            
        miobattito = pd.concat([miobattito, pd.DataFrame(last_value, index=last_key)])
        print("Last key:", last_key[-1], "last_value: ", last_value[-1])
        print("")
        print(miobattito)
        time.sleep(60)
    except:
        #rimuovi doppioni
        miobattito = miobattito[~miobattito.index.duplicated()]
        plt.plot(miobattito.index, miobattito.values)
        plt.show()
        break