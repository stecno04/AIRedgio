# AIRedgio, ricezione dati e salvataggio
## Introduzione 
Il progetto europeo è stato sviluppato per la ricezione dei dati da un sensore di rumore, da un sensore ambientale, da uno smartwatch e da una termocamera e il seguente salvataggio su un database MongoDB.

## Prerequisiti
- Python 3.11 (si raccomanda l'uso di un virtual environment)
- Acesso ad un server MongoDB

Per installare le librerie necessarie eseguire il seguente comando:
```bash
pip install -r requirements.txt
```
Al fine di analizzare correttamente i dati è necessario installare libusb.dll dal seguente [link](https://sourceforge.net/projects/libusb/files/libusb-1.0/libusb-1.0.20/libusb-1.0.20.7z/download)
Estrarre i files, copiare il file libusb-1.0.dll in C:/Windows/System32 e inserire in variabili di sistema la seguente variabile: 
```
LIBUSB_1_PATH = C:\Windows\System32\libusb-1.0.dll
```


## Tree
```
.
├── README.md
├── requirements.txt
├── .gitignore
├── main
├── Garmin
    ├── Vari programmi utilizzati per l'analisi dei dati garmin
├── NoiseMeter
    ├── find_port.py -> Programma per trovare la porta seriale del sensore di rumore 
    ├── Vari programmi utilizzati per l'analisi dei dati del sensore di rumore
├── SensoreAmbientale
    ├── Vari programmi utilizzati per l'analisi dei dati del sensore ambientale
├── termocamera
    ├── Vari programmi utilizzati per l'analisi dei dati della 
├── webcam
    ├── Vari programmi utilizzati per l'analisi dei dati della webcam





```

## Utilizzo
### Configurazione
Inserire in riga 26 del file `main/app.py` il link del proprio server MongoDB:

Opzionalmente appena sotto modificare il tempo di attesa tra le varie raccolte dati dai vari sensori.

A riga 38 e 39 ci sono i numeri per le porte seriali del sensore di rumore, al fine di trovare la porta seriale corretta eseguire il programma `NoiseMeter/find_port.py`, l'output varia in base a quanti dispositivi sono collegati al computer; Al fine di trovare quello che interessa a noi, attaccare e staccare il NoiseMeter e ,una volta notata la riga che differisce, modificare i valori delle righe 38 e 39 con i valori ottenuti.

A riga 35/36 è possibile modificare il numero della camera termica e di una eventuale camera che rileva lo stato d'animo della persona (generalmente sono le seguenti: camera termica = 1, camera stato d'animo = 1). Eventualmente e in caso di errori modificare tra 0 e 3.

Tra le righe 41 e 44 è possibile modificare le passwords relative all'API delL'orologio Garmin 

A riga 46 è possibile modificare l'URL del sensore ambientale. 

Tra la riga 73 e 118 ci sono due funzioni che si occupano di ottenere la temperatura. 
La prima funzione analizza i dati centrali della fotocamera e restituisce la temperatura massima all'interno del frame. La seconda funzione restituisce la temperatura del pixel centrale del frame. Una volta scelta la funzione da utilizzare modificare il nome di quella che non si utlizza in termocamera2(cap) e quella da utilizzare in termocamera(cap)



### Esecuzione
Il programma principale è `main/app.py` che si occupa di ricevere i dati dai sensori, salvarli su un database MongoDB e mostrare su Server locale i dati ricevuti.
Per avviare il programma eseguire il seguente comando:
```bash
python main/app.py
```

Durante l'esecuzione del programma da tastiera è possibile scrivere su terminale e successivamente premere invio per mostrare a schermo se il componente è da scartare o non.

## Conclusioni
Il progetto è ancora in sviluppo e verranno aggiunte probabilmente nuove funzionalità in futuro.
