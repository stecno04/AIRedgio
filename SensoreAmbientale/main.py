
import requests
import time
from datetime import datetime

# Funzione per effettuare la richiesta API e ottenere i dati
def get_sensor_data():
    url = "http://10.144.230.89:20000/"  # Sostituisci con l'URL effettivo del tuo endpoint API
    response = requests.get(url)
    print(response.text)
    return write_to_csv(response.text)

metrics_mapping = {
    'Nuvap_Environment_co{sensorID="19602"}': 'co',
    'Nuvap_Environment_pm1{sensorID="19602"}': 'pm1',
    'Nuvap_Environment_pm2_5{sensorID="19602"}': 'pm2_5',
    'Nuvap_Environment_ch4{sensorID="19602"}': 'ch4',
    'Nuvap_Environment_pm10{sensorID="19602"}': 'pm10',
    'Nuvap_Environment_voc{sensorID="19602"}': 'voc',
    'Nuvap_Environment_temp{sensorID="19602"}': 'temp',
    'Nuvap_Environment_hygro{sensorID="19602"}': 'hygro',
    'Nuvap_Environment_formaldehyde{sensorID="19602"}': 'formaldehyde',
    'Nuvap_Environment_nox{sensorID="19602"}': 'nox',
    'Nuvap_Environment_ozone{sensorID="19602"}': 'ozone',
    'Nuvap_Environment_co2{sensorID="19602"}': 'co2',
    'Nuvap_Environment_q_total{sensorID="19602"}': 'q_total'
}

def process_line(line):
    metric, value = line.split(' ')[0], line.split(' ')[1]
    if metric in metrics_mapping:
        return metrics_mapping[metric], value
    else:
        return None, None

def process_data(data):
    respon = {'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M:%S")}

    for line in data.splitlines():
        if line.startswith('Nuvap_Environment'):
            metric, value = process_line(line)
            if metric:
                respon[metric] = value
    return respon

def write_to_csv(data):
    fieldnames = ['timestamp', 'co', 'pm1', 'pm2_5', 'ch4', 'pm10', 'voc', 'temp', 'hygro', 'formaldehyde', 'nox', 'ozone', 'co2', 'q_total']
    
    dictio = process_data(data)  # Pass 'data' directly here
    return dictio



# Now you can read the CS

# Loop principale per ottenere e scrivere i dati ogni 90 secondi
while True:
    sensor_data = get_sensor_data()
    print(sensor_data)
    time.sleep(90)
