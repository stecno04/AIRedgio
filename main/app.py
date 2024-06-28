#imports
from PIL import ImageGrab
import numpy as np
import subprocess
import time
import os

import usb.core
import usb
import array

import cv2
from deepface import DeepFace


import requests
import hashlib
import hmac
import base64
from urllib.parse import quote
import datetime

import pymongo


CLIENT = "mongodb+srv://stefanocarobene:RhUjbD4BE6evldLf@xsensmsg.nyhkxnw.mongodb.net/"

INTERVALLONOISE = 1   #valore minimo 1, il noiseMeter mostr dalla loro applicazione dati ogni secondo
INTERVALLOTHERMAL = 1 #volendo si può fare più lento ma non ha senso
INTERVALLOGARMIN = 60   #valore minimo 60 secondi, i dati di garmin vengono aggiornati ogni minuto quando la nostra applicazione è attiva
INTERVALLOAMBIENTALE = 90 # valore minimo 90 secondi, i dati ambientali vengono aggiornati ogni 90 secondi
INTERVALLOMINIMO = 1 # ogni quanto stampa e magari salva i valori (suggerimento 1 secondo ma può essere cambiato) minimo 0 ma non ha senso
INTERVALLOCAMERA = 1 # ogni quanto fa la foto con la webcam (suggerimento 1 secondo ma può essere cambiato) minimo 0 ma non ha senso

CAPNUMBECMAERA = 0
capnumberTermocamera = 1   #sometimes is 1, se non funziona provare a cambiare il numero della webcam

IDVENDORUSB = 1155
IDPRODUCTUSB = 22352

CONSUMER_KEY = "4abf826a-87c6-434c-a7f0-b65c14fcf3f4"
CONSUMER_SECRET = "BiLzHopVh8h30KlnspZpwVvlierOZXHzFKu"
ACCESS_TOKEN = "3b76468e-b934-45de-a90a-673add971181"
TOKEN_SECRET = "XogfActj8BmA1QVHh3laaklbFxwuXkO52mo"

URL = "http://10.144.230.89:20000/" 



CAPNUMBER = capnumberTermocamera
######### NoiseMeter/main.py
def add(byte_array: array.array, position: int) -> array.array | None:
    if position >= len(byte_array):
        return None
    if (byte_array[position] == 255):
        byte_array[position] = 0
        return add(byte_array, position)
    return byte_array

def noisemeter(dev, endpoint, endpoint2, payload):
    global OLDNUM
    dev.write(endpoint2.bEndpointAddress, payload)
    data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
    
    numero_intero = (int.from_bytes(bytes(data[0:2]), byteorder='big'))/10  # Interpreta i byte come intero (big-endian)

    return numero_intero

######### termocamera/main.py
# la termocamera restituisce quattro diverse immagini, una non ha informazioni, una ha le temperature, una ha le immagini e una riguarda sempre le temperatura ma le mostra con una diversa precisione
# noi prendiamo la prima immagine che mostra le temperature e sommiamo la seconda che restituirà un valore più preciso

def termocamera(cap):
    ret, frame = cap.read()

    if ret == True:
        # Display the resulting frame
        image_array = np.reshape(frame, (2, 192, 256, 2))
        terzo = image_array[0, :, :, 0]
        # cv2.namedWindow('Thermal',cv2.WINDOW_NORMAL)
        #pixel in mezzo
        max_temp = (-float("inf"), 0, 0)
        for i in range(90,170):
            for j in range(50,200):
                hi = image_array[0, i, j, 0]
                lo = image_array[1, i, j, 1]
                lo = lo * 256
                rawtemp = lo + hi
                temp = (rawtemp / 64) - 273.15
                if temp > max_temp[0]:
                    max_temp = (temp, i, j)
        # print(f"Max Temp: {round(max_temp[0], 2)}")
        # Draw a marker at the location of maximum temperature
        # frame_with_marker = cv2.circle(terzo.copy(), (max_temp[2], max_temp[1]), 2, (0, 0, 255), -1)

        # Display the frame with marker
        # cv2.imshow('Thermal', frame_with_marker)
        

    return round(max_temp[0], 2) -3

def termocamera2(cap):

    ret, frame = cap.read()

    if ret == True:
        # Display the resulting frame
        image_array = np.reshape(frame, (2, 192, 256, 2))
        terzo = image_array[0, :, :, 0]
        quarto = image_array[1, :, :, 1]
        hi = terzo[175][100]
        lo = quarto[175][100]
        lo = lo * 256
        rawtemp = lo + hi
        temp = (rawtemp / 64) - 273.15
        temp = round(temp, 2)
        print(f"Temp: {temp}")
    return temp+3

######### Garmin/main.py
# Add your OAuth 1.0 authentication keys here# ci sono dei problemi iniziali di connessione, se non funziona provare dall'orologio a sincronizzare con telefono e da garmic connect developer a fare un po' di richieste e verificare che le metriche siano attive
# l'applicazione mobile connessa al garmin aggiornerà in automatco i dati una volta ogni due giorni, tramite applicazione scritta su automate è possibile aggiornerli ogni minuto "forzando" la connessione
def toda():
    today = datetime.date.today()
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
    global CONSUMER_SECRET
    global CONSUMER_KEY 
    global ACCESS_TOKEN 
    global TOKEN_SECRET 

    method = 'GET'  # or 'POST' if it's a POST request
    oauth_signature = generate_oauth_signature(base_url, method, params, CONSUMER_SECRET, TOKEN_SECRET, CONSUMER_KEY, ACCESS_TOKEN)

    headers = {
        "Authorization": f'OAuth oauth_consumer_key="{CONSUMER_KEY}", '
                         f'oauth_token="{ACCESS_TOKEN}", '
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
def calculate_hrv_stress_score(rr_intervals):
    """
    Calcola l'HRV Stress Score dato un elenco di intervalli RR (battiti cardiaci).

    Args:
        rr_intervals (list): Lista degli intervalli RR in millisecondi.

    Returns:
        float: HRV Stress Score.
    """
    num_intervals = len(rr_intervals)
    rr_avg = sum(rr_intervals) / num_intervals

    # Calcola la somma delle differenze quadrate tra ciascun intervallo RR e la media
    squared_diff_sum = sum((rr - rr_avg) ** 2 for rr in rr_intervals)

    # Calcola la deviazione standard della variabilità RR
    hrv_sdnn = (squared_diff_sum / (num_intervals - 1)) ** 0.5

    # Calcola l'HRV Stress Score normalizzato tra 0 e 100
    hrv_stress_score = (hrv_sdnn / rr_avg) * 100

    return hrv_stress_score

def garming():
    start, end = toda()
    hrt = list(make_api_request(start, end, "dailies")[-1]['timeOffsetHeartRateSamples'].values())[-1]
    pulseox = list(make_api_request(start, end, "pulseOx")[-1]['timeOffsetSpo2Values'].values())[-1]
    
    stress = calculate_hrv_stress_score(list(make_api_request(start, end, "dailies")[-1]["timeOffsetHeartRateSamples"].values())[-20:])
    if stress > 10:
        stress = 10
    jsonFinale = {
        "Heart Rate": hrt,
        "Blood Oxygen Level": f'{pulseox}%',
        "Stress Level": f'{int(stress*10)}%'
    }
    return jsonFinale

######### Ambientale/main.py
# Sostituisci con l'URL effettivo del tuo endpoint API
# assicurarsi che cliccando sul link si possano vedere i dati
def process_line(line):
    metrics_mapping = {
    'Nuvap_Environment_co{sensorID="19602"}': 'Carbon monooxide',
    'Nuvap_Environment_pm1{sensorID="19602"}': 'Particulate pm1',
    'Nuvap_Environment_pm2_5{sensorID="19602"}': 'Particulate pm2_5',
    'Nuvap_Environment_ch4{sensorID="19602"}': 'Methane gas',
    'Nuvap_Environment_pm10{sensorID="19602"}': 'Particulate pm10',
    'Nuvap_Environment_voc{sensorID="19602"}': 'Volatile organic compounds',
    'Nuvap_Environment_temp{sensorID="19602"}': 'Temperature',
    'Nuvap_Environment_hygro{sensorID="19602"}': 'Humidity',
    'Nuvap_Environment_formaldehyde{sensorID="19602"}': 'Formaldehyde',
    'Nuvap_Environment_nox{sensorID="19602"}': 'Oxides of nitrogen',
    'Nuvap_Environment_ozone{sensorID="19602"}': 'Ozone gas',
    'Nuvap_Environment_co2{sensorID="19602"}': 'Carbon dioxide',
    'Nuvap_Environment_q_total{sensorID="19602"}': 'Quality index'
    }
    metric, value = line.split(' ')[0], line.split(' ')[1]
    if metric in metrics_mapping:
        return metrics_mapping[metric], value
    else:
        return None, None
def process_data(data):
    # respon = {'timestamp': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
    respon = {}
    for line in data.splitlines():
        if line.startswith('Nuvap_Environment'):
            metric, value = process_line(line)
            if metric:
                respon[metric] = value
    return respon

def ambientale():
    global URL
    response = requests.get(URL)
    return process_data(response.text)

######### Webcam/main.py
def videopick(video):
    global FACE_CASCADE
    cv2.destroyAllWindows()

    #checking if are getting video feed and using it
    if video.isOpened():  
        _,frame = video.read()
        try:
            #acv2.imshow('video', frame)
            #key=cv2.waitKey(1) 
            # ZOOM 
            frame = cv2.resize(frame,(640,480))
        
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)  
            face=FACE_CASCADE.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=6)
            for x,y,w,h in face:
                    #making a recentangle to show up and detect the face and setting it position and colour
                    img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),1) 
                    # punto centrale volto = (x,y)
                    print("il volto si trova in: "+ str(x) + " "+ str(y))
                   
                    return img
        except cv2.error as e:
            print("errore nella lettura dell'immagine", e)
def analize(img):
    #making a try and except condition in case of any errors
    try:
        try:
            analyze = DeepFace.analyze(img, actions=['emotion'])
            dominant_emotion = analyze[0]['dominant_emotion']
            return dominant_emotion
        except Exception as e:
            print("error: ", e)
            print("problem during analisys..")
            return
    except cv2.error as e:
        print("no face detected, error: ", e)  

def are_you_happy(cap):
    img = videopick(cap)
    expression = analize(img)
    return expression



#main function
def update_data():    
    global CAPNUMBER
    global INTERVALLOTHERMAL
    global INTERVALLOGARMIN
    global INTERVALLOAMBIENTALE
    global INTERVALLONOISE
    global INTERVALLOMINIMO
    global CLIENT
    global INTERVALLOCAMERA
    global IDVENDORUSB
    global IDPRODUCTUSB
    global CAPNUMBECMAERA
    global FACE_CASCADE
    global PPALA
    print("inizio--------------------------------------------------------------------")
    print("inserisci nome esperimento: if empty default is 'datetime': ")
    nome_exp = input()
    if nome_exp:
        nome_exp = nome_exp
    else:
        nome_exp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    misure_corpo = {"height": 1.80, "weight": 80, "age": 25}

    print("inserisci altezza in metri: ")
    altezza = float(input().strip())
    misure_corpo["height"] = altezza if altezza > 0 else 1.80

    print("inserisci peso in kg: ")
    peso = float(input().strip())
    misure_corpo["weight"] = peso if peso > 0 else 80

    print("inserisci età: ")
    eta = int(input().strip())
    misure_corpo["age"] = eta if eta > 0 else 25

    print(misure_corpo)

    socketio.emit('misure_corpo', misure_corpo, namespace='/')
    PPALA =1
    print("inizio whie true--------------------------------------------------------------------")
    # nome_exp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    while True:
        print("Inizio")
        
        ultimoAmbientale = time.time()
        ultimoGarmin = time.time()
        ultimoTermocamera = time.time()
        ultimoNoiseMeter = time.time()
        ultimoPrint = time.time()
        ultimoCamera = time.time()

        face_cascade_name = cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'  
        #processing it for our project
        FACE_CASCADE = cv2.CascadeClassifier()  
        #adding a fallback event
        if not FACE_CASCADE.load(cv2.samples.findFile(face_cascade_name)):  
            print("Error loading xml file")
        capcamera = cv2.VideoCapture(CAPNUMBECMAERA)

        dev: usb.core.Device = usb.core.find(idVendor=IDVENDORUSB, idProduct=IDPRODUCTUSB)
        endpoint = dev[0][(0,0)][0]
        endpoint2 = dev[0][(0,0)][1]
        init = [0 for _ in range(64)]
        init[0] = 179
        payload = add(array.array('B', init), 0)

        client = pymongo.MongoClient(CLIENT)
        db = client["AIRedgio"]
        collection = db[f"dati_{nome_exp}_sensoristica"]

        if folder := "errori":
            if not os.path.exists(folder):
                os.makedirs(folder)
        capo = cv2.VideoCapture(CAPNUMBER)
        capo.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        width = int(capo.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capo.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
        font=cv2.FONT_HERSHEY_SIMPLEX
        temperatura = termocamera(capo)
        dieci = noisemeter(dev, endpoint, endpoint2, payload)
        # print(dieci)
        # break
        dta_garmin = garming()
        retunaDatiAmbientali = ambientale()

        camara = are_you_happy(capcamera)

        print("inizio whie true--------------------------------------------------------------------")
        # while(capo.isOpened()):
        while True:
            
            try:
                timenow = time.time()
                if timenow - ultimoNoiseMeter > INTERVALLONOISE:
                    dieci = noisemeter(dev, endpoint, endpoint2, payload)
                    ultimoNoiseMeter = timenow

                if timenow - ultimoTermocamera > INTERVALLOTHERMAL:
                    temperatura = termocamera(capo)
                    ultimoTermocamera = timenow

                if timenow - ultimoGarmin > INTERVALLOGARMIN:
                    dta_garmin= garming()
                    ultimoGarmin = timenow

                # if timenow - ultimoCamera > INTERVALLOCAMERA:
                #     camara = are_you_happy(capcamera)
                #     print(camara)
                #     ultimoCamera = timenow
                
                if timenow - ultimoAmbientale > INTERVALLOAMBIENTALE:
                    retunaDatiAmbientali = ambientale()
                    ultimoAmbientale = timenow

                if timenow - ultimoPrint > INTERVALLOMINIMO:
                    global html_data
                    documento = {
                        "Date and Time": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        "Worker Temperature": temperatura,
                        "Ambiental Sensor": retunaDatiAmbientali,
                        "Smartwatch": dta_garmin,
                        "Noise Meter": dieci,
                        # "cameraDaTogliere": camara
                    }
                    html_data = {
                        'title': 'AI-Redgio',
                        'header': 'Welcome to the Data Page of AIRedgio',
                        'data_items': documento

                    }

                    # print("html: ", html_data)
                    socketio.emit('update_data', html_data, namespace='/')
                    
                    collection.insert_one(documento)
                    ultimoPrint = timenow
                
                # se freccia a destra socket.io emette un evento se sinistra ne emette un altro
                

                keyPress = cv2.waitKey(3)
                if keyPress == ord('q'):

                    break
                    capture.release()
                    cv2.destroyAllWindows()
            except KeyboardInterrupt:
                break
        print("Vuoi continuare? i - input nome esperimento/ n - no/ qualsiasi altro tasto - si:")
        true = input()
        if true == "n":
            break
        elif true == "i":
            nome_exp = input("inserisci nome esperimento: ")
        


from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
PPALA = 0
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')


html_data = {'title': 'AI-Redgio', 
            'header': 'Welcome to the Data Page of AIRedgio', 
            'data_items': {
                'Date and Time': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
                'Worker Temperature': 0, 
                'Ambiental Sensor': {
                    'Carbon monooxide': '0', 
                    'Particulate pm1': '0', 
                    'Particulate pm2_5': '0', 
                    'Particulate pm10': '0', 
                    'Volatile organic compounds': '0', 
                    'Temperature': '0', 
                    'Humidity': '0', 
                    'Formaldehyde': '0', 
                    'Oxides of nitrogen': '0', 
                    'Ozone gas': '0', 
                    'Carbon dioxide': '0', 
                    'Quality index': '0'
                    }, 
                'Smartwatch': {
                    'Heart Rate': 0, 
                    'Blood Oxygen Level': 0, 
                    'Stress Level': 0
                    }, 
                'Noise Meter': 0, 
                'cameraDaTogliere': None}}

@socketio.on('connect', namespace='/')
def handle_connect():
    emit('update_data', html_data)

def main_task():
    thread = threading.Thread(target=update_data)
    thread.daemon = True
    thread.start()
    socketio.run(app, debug=False, port=5000)

def check():
    global PPALA
    if PPALA == 1:
        user_input = input("Inserisci se scarto: p buono, q scarto: ")
        if user_input == "p":
            socketio.emit('scarto', {"Quality control: ":"good"}, namespace='/')
        elif user_input == "q":
            socketio.emit('scarto', {"Quality control":"broken"}, namespace='/')

import threading
def keyboard_listener():
    # wait till ppala == 1
    while True:
        check()
        

if __name__ == "__main__":
    # Crea un thread per il compito principale
    main_thread = threading.Thread(target=main_task)
    # Crea un thread per l'ascolto della tastiera
    listener_thread = threading.Thread(target=keyboard_listener)

    # Avvia entrambi i thread
    main_thread.start()
    listener_thread.start()

    # Aspetta che il thread dell'ascoltatore della tastiera termini
    listener_thread.join()
    print("Programma terminato.")
