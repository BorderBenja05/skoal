##script to listen for GCN Notices and save them as xml's
import subprocess
import GCN_utils as GCN
from gcn_kafka import Consumer
import os
import time
from pathlib import Path
import csv


GCN_DIR = Path(__file__).parent.absolute()


# Connect as a consumer (client "TURBO_Kafka")
# Warning: don't share the client secret with others.
consumer = Consumer(client_id='2vvouktibnc9ghg1e3ppbd4n96',
                    client_secret='1peni3v9agalojvv48i5lmnpunjs5645rtig354hjfnnp02i2bl1')


# Subscribe to topics and receive Ground_Positions
consumer.subscribe(['gcn.classic.voevent.FERMI_GBM_GND_POS',
                    'gcn.classic.voevent.FERMI_LAT_MONITOR',
                    'gcn.classic.voevent.FERMI_LAT_POS_TEST',
                    'gcn.classic.voevent.FERMI_GBM_POS_TEST',
                    'gcn.classic.voevent.LVC_COUNTERPART',
                    'gcn.classic.voevent.LVC_INITIAL',
                    'gcn.classic.voevent.LVC_PRELIMINARY'])


# Create the output directorys if it doesn't exist
if not os.path.exists(f"{GCN_DIR}/FERMI_Notices"):
    os.makedirs(f"{GCN_DIR}/FERMI_Notices")

if not os.path.exists(f"{GCN_DIR}/LVC_Notices"):
    os.makedirs(f"{GCN_DIR}/LVC_Notices")



while True:
    for message in consumer.consume(timeout=1):
        if message.error():
            print(message.error())
            continue
        
        # Constructing the file name using topic and offset
        filename = f'{message.topic()}_{message.offset()}.xml'
        dirname = f'{message.topic()}_{message.offset()}'

        
        # Make directory
        if message.topic() == "gcn.classic.voevent.FERMI_GBM_GND_POS" or message.topic() == "gcn.classic.voevent.FERMI_LAT_MONITOR" or message.topic() == "gcn.classic.voevent.FERMI_LAT_POS_TEST" or message.topic() == "gcn.classic.voevent.FERMI_GBM_POS_TEST":
            file_path = f'{GCN_DIR}/FERMI_Notices/{dirname}'
        if message.topic() == "gcn.classic.voevent.LVC_COUNTERPART" or message.topic() == "gcn.classic.voevent.LVC_INITIAL" or message.topic() == "gcn.classic.voevent.LVC_PRELIMINARY":
            file_path = f'{GCN_DIR}/LVC_Notices/{dirname}'
            os.makedirs(file_path)


        # Write message to XML file
        open(f'{file_path}/{filename}', "wb").write(message.value())

        # Grab GraceID / Event name
        event = GCN.getEvent(f'{file_path}/{filename}')
        
        if message.topic() == "gcn.classic.voevent.LVC_COUNTERPART" or message.topic() == "gcn.classic.voevent.LVC_INITIAL" or message.topic() == "gcn.classic.voevent.LVC_PRELIMINARY":
            # Runs gwemopt to get schedule
            os.system(f'gwemopt-run -e {event} --doTiles -t RASA11 -o {file_path}/ --tilesType moc --doSchedule')
        
        if message.topic() == "gcn.classic.voevent.FERMI_GBM_GND_POS" or message.topic() == "gcn.classic.voevent.FERMI_LAT_MONITOR" or message.topic() == "gcn.classic.voevent.FERMI_LAT_POS_TEST" or message.topic() == "gcn.classic.voevent.FERMI_GBM_POS_TEST":
            # Grabs FK5 coords and prints them if the error is small enough for a oneshot
            ra,dec,error = GCN.getFERMICoordinates(f'{file_path}/{filename}') 
            if error < 2:
                print(f"FERMI notice {message.offset()} at FK5 Coords, ra:{ra} dec:{dec}",f"Error radius:{error}")

                # Writing to CSV
                with open('coordinates.csv', 'w', newline='') as csvfile:
                    fieldnames = ['RA', 'Dec', 'Error']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Write the header
                    writer.writeheader()

                    # Write the coordinates
                    writer.writerow({'RA': ra, 'Dec': dec, 'Error': error})