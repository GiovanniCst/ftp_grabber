#!/usr/bin/env python
# -*- coding: utf-8 -*

# di Giovanni J. Costantini - www.costantini.pw
# per -redacted-
# procedura Python 3 per il recupero file dati lavanderia da server FTP
# Aprile 2019

import sys
from ftplib import FTP
import os
import datetime
from shutil import copy2
import smtplib
from email.message import EmailMessage

ora = datetime.datetime.now()

# Main configuration
LAUNDRY = "\-redacted-"
FTPSERVER = "ftp.gamba1918.com"
FTPUSER = "-redacted-"
FTPPASSWD = "-redacted-"
FTPDOMAIN = "@-redacted-.com"
FTPBACKUPDIR = "obsolete"
DATAFILE = "-redacted-.xls"
BASEPATH = "C:\-redacted-"
SAVE_DIR = BASEPATH + LAUNDRY + ora.strftime("\%Y-%m-%d")

# Email configuration
EMAIL_ADDRESS = "python@-redacted-.it"
EMAIL_PASSWORD = "-redacted-"
SMTP_SERVER = 'mail.-redacted-.it'
SMTP_PORT = 465


if not os.path.exists(BASEPATH + LAUNDRY + ora.strftime("\%Y-%m-%d")):
    os.makedirs(BASEPATH + LAUNDRY + ora.strftime("\%Y-%m-%d"))


log = open("log.txt", "a+")

LOCALDIR = BASEPATH + LAUNDRY + ora.strftime("\%Y-%m-%d")


def notifySuccess():    
    msg = EmailMessage()
    msg['Subject'] = "Info da procedura recupero file dati lavanderie: " + FTPUSER
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = '-redacted-@gmail.com'
    msg.set_content("Il file dati della lavanderia " + FTPUSER + " è stato recuperato ed è ora disponibile sul server nella cartella:\n\n" + SAVE_DIR + "\n\n per essere lavorato.\n Dovresti riuscire a vedere la cartella sel server dal tuo computer tramite 'Risorse di rete'.\n\nCordialità.\nI sistemi informativi di -redacted-")

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)

def notifyFail():    
    msg = EmailMessage()
    msg['Subject'] = "Alert da procedura recupero file dati lavanderie: " + FTPUSER
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = '-redacted-@gmail.com'
    msg.set_content("Non è stato possibile collegarsi a ftp.-redacted-.com per prelevare il file dati della lavanderia.\n  ")

    with open('log.txt') as f:
        file_data = f.read()
        file_name = f.name

        msg.add_attachment(file_data, filename=file_name)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)


def checkLink():
    """ Check if we can reach the ftp server. """
    """ Dovrei usare popen per evitare l'output in console? """

    linkup = os.system("ping " + FTPSERVER + " -n 1")
    if linkup == 0:
        log.write(str(ora) + ": Link is up, all seems fine \n")
                
        return True
    else:
        log.write(str(ora) + ": Link is down, server unreachable \n")
        
        
        return False


def makeUser(FTPUSER, FTPDOMAIN):
    """ Compose the username. """

    username = FTPUSER + FTPDOMAIN
        
    return username


def ftpLogin(ftp):
    """ logins to the Ftp server. """

    user = makeUser(FTPUSER, FTPDOMAIN)
    ftp.login(user=user, passwd=FTPPASSWD)
  
    return ftp


def recuperaFile(ftp):
    """ collects the data file and deletes it. """

    filename = ora.strftime(("%Y-%m-%d") + '_-redacted-.xls')
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + DATAFILE, localfile.write, 1024)
    ftp.delete(DATAFILE)
    localfile.close()
    
    
    return localfile.name


def archiviaFile(ftp):
    """ stores the data file back to the ftp server, into the specified backup folder. """

    filename = ora.strftime(("%Y-%m-%d") + '_-redacted-.xls')
    ftp.cwd(FTPBACKUPDIR) 
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))



# Se c'e' connettivita' procedi
if checkLink():
    print(FTPSERVER + " is alive, all is fine, I'moving on to the next steps")
    
    # preparo la connettivita' ftp 
    ftp = FTP(FTPSERVER)

    # se il login sul server ha successo
    if ftpLogin(ftp):
        print("Suceessfully connected to " + FTPSERVER)
        log.write(str(ora) + ": Successfully connected to " + FTPSERVER + "\n")
            
           # recupera il file dati della lavanderia dal server ftp
        try:
            file_salvato = recuperaFile(ftp)
            archiviaFile(ftp)
            ftp.close()
            print("Data file successfully recovered")
            log.write(str(ora) + ": " + file_salvato + " was successfully obtained, downloaded and archived, all looks fine. \n")
            
            # e prova a salvarlo localmente sul server Teamsystem
            try:
                copy2(file_salvato, LOCALDIR + "\\" + file_salvato)
                print("Data file successfully saved")
                log.write(str(ora) + ": " + file_salvato + " was successfully copied into " + LOCALDIR + "\n")
                notifySuccess()
            
            # altrimenti notifica il fallimento della copia locale
            except:
                print("Copia fallita")
                log.write(str(ora) + ": Non e' stato possible consegnare il file nella cartella di destinazione\n")
                notifyFail()

        # se il file non c'e', chiudi la connessione
        except:
            ftp.close()
            print("File non presente")
            log.write(str(ora) + ": Data file not available on the Ftp server.\n")
         
# Se non c'e' connettività inutile procedere avanti
else:
    print("Server is not reachable, I'm stopping here")
    log.write(str(ora) + ": Server unreachable, cannot progress with the task.\n")
    notifyFail()

print("Procedura terminata")
log.write(str(ora) + ": --------------- [END OF THIS SESSION LOG] ---------------\n\n")
log.close()
sys.exit()
