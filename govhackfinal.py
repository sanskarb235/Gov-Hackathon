import sqlite3
import requests
from datetime import datetime
import random
import requests, time
import http.client
import ssl
import json
import mimetypes

ssl._create_default_https_context = ssl._create_unverified_context
def main():

    conn = sqlite3.connect('telstraapifinal.db')
    c = conn.cursor()

    c.execute(""" CREATE TABLE Telstraapi (
        Firstname text NOT NULL,
        Lastname text NOT NULL,
        Phonenumber text NOT NULL PRIMARY KEY,
       Email text NOT NULL,
        Currentlocation text NOT NULL,
        Emergencycontact integer NOT NULL,
        ProfilePicture blob,
        Voluntering bool NOT NULL
    )""")

    conn.commit()

    conn.close()

def insertBLOB(fname, lname, phoneno, email, loc, emergcont, pic, vol):
    sqliteConnection = sqlite3.connect('telstraapifinal.db')
    cursor = sqliteConnection.cursor()
    print("Connected to SQLite")
    empPhoto = convertToBinaryData(pic)

    cursor.execute("""
   INSERT OR IGNORE INTO Telstraapi (Firstname, Lastname, Phonenumber, Email, Currentlocation, Emergencycontact, ProfilePicture, Voluntering ) VALUES (?,?,?,?,?,?,?,?)""", (fname, lname, phoneno, email, loc, emergcont, empPhoto, vol))
    
    sqliteConnection.commit()
    print("Image and file inserted successfully as a BLOB into a table")
    cursor.close()

def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def messagequery():
    sqliteConnection = sqlite3.connect('telstraapifinal.db')
    cursor = sqliteConnection.cursor()
    rangelat = .1
    rangelongi = .1
    latitute = -37.8076
    longitute = 144.9216
    cursor.execute("SELECT Currentlocation, Phonenumber FROM Telstraapi")
    loc = cursor.fetchall()
    c = []
    longitutelist = {}
    latitutelist = {}
    contactlist ={}
    longlastlist = {}
    f=0
    r=0
    g=0
    
    longlastlist, contactlist = map(list, zip(*loc))
    
    for i in longlastlist:
        a = i.split(",")
        c += [j.split('°',1)[0] for j in a]
    for j in range(len(c)):
        if(j%2==0):
            latitutelist[f] = c[j]
            f+=1
        else:
            longitutelist[r] = c[j]
            r+=1
    
    for u in range(len(latitutelist)):
        lat = float(latitutelist[u])
        longit = float(longitutelist[u])
        if (((latitute-lat) <= rangelat and (latitute-lat) >= 0 and (longitute-longit)<= rangelongi) or ((lat-latitute)<= rangelat and (lat-latitute) >=0 and (longit-longitute)<= rangelongi)):
            sendmes(contactlist[u], "There is a natural disaster coming your way, follow the standard evacuation process")
    cursor.close()
    
def volunteeringquery():
    sqliteConnection = sqlite3.connect('telstraapifinal.db')
    cursor = sqliteConnection.cursor()
    cursor.execute("SELECT Firstname, Lastname, Phonenumber, Currentlocation, Voluntering FROM Telstraapi")
    lis = cursor.fetchall()
    contactlist = {}
    firstnamelist = {}
    emailids = {}
    currentloc = {}
    volunteer = {}
    longitutelist = {}
    latitutelist = {}
    c=[]
    r = 0
    f=0
    rangelat = .1
    rangelongi = .1
    firstnamelist, lastnamelist, contactlist, currentloc, volunteer = map(list, zip(*lis))
    affected = {4,6}
    for i in currentloc:
        a = i.split(",")
        c += [j.split('°',1)[0] for j in a]
    for j in range(len(c)):
        if(j%2==0):
            latitutelist[f] = c[j]
            f+=1
        else:
            longitutelist[r] = c[j]
            r+=1
    latitute = float(latitutelist[4])
    longitute = float(longitutelist[4])
    volunteeredlist = {}
    affectedlist = {}
    c=0
    
    
    for v in range(len(volunteer)):
        if(volunteer[v] == 1 and (v not in affected)):
            volunteeredlist[c] = v
            c+=1
    affectedlist = list(affected)

    for v in range(len(volunteer)):
        if(volunteer[v] == 1 and (v not in affected)):
            lat = float(latitutelist[v])
            longit = float(longitutelist[v])
            if (((latitute-lat) <= rangelat and (latitute-lat) >= 0 and (longitute-longit)<= rangelongi) or ((lat-latitute)<= rangelat and (lat-latitute) >=0 and (longit-longitute)<= rangelongi)):
                df = random.choice(affectedlist)
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                curtime = int(current_time[:2])
                link = "https://www.google.com/maps/place/" + latitutelist[df][1:] + "°S+" + longitutelist[df][1:] + "°E/@24.197611,120.7783233,17z/data=!3m1!4b1!4m5!3m4!1s0x0:0x0!8m2!3d24.197611!4d120.780512"
                if(curtime<12 and curtime>=5):
                    mess = "Good Morning" + firstnamelist[v] + lastnamelist[v] + "Thank you so much for choosing to help" + "Affected Person:"+ firstnamelist[df]+ lastnamelist[df] + "Contact:" + contactlist[df]+ "Location:"+link
                    sendmes(contactlist[v], mess)
                elif(curtime>=12 and curtime<17):
                    mess2 = "Good Afternoon ", firstnamelist[v] , lastnamelist[v] , "Thank you so much for choosing to help " , "Affected Person: ", firstnamelist[df], lastnamelist[df] , "Contact:" , contactlist[df], "Location:", link
                    sendmes(contactlist[v], mess2)
                else:
                    mess3 = "Good Evening "+ firstnamelist[v] + " " + lastnamelist[v] +" Thank you so much for choosing to help " + "Affected Person: " + firstnamelist[df] + " " + lastnamelist[df]  + " Contact: " + contactlist[df]+ " Location: "+ link
                    sendmes(contactlist[v], mess3)
        cursor.close()
    
def getoauth():

    url = "https://tapi.telstra.com/v2/oauth/token"

    payload = 'client_id=AXWEOnjlEPwdGu9OWHtrfbA6oCnX3QZT&client_secret=ZmfN4xW9ptSAzcc2&grant_type=client_credentials&scope=NSMS'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    print(response.text.encode('utf8'))
    
def sendmes(phonenumber, messagedata):
    conn = http.client.HTTPSConnection("tapi.telstra.com")
    payload = "{\r\n  \"to\": \"+61469782899\",\r\n  \"body\": \"There is a natural disaster coming your way, follow the standard evacuation process\",\r\n  \"notifyURL\": \"https://2a14a18ff4fa2d7502ca27e4c459e55b.m.pipedream.net\"\r\n}\r\n"
    #payload = str("{\r\n  \"to\": \",", "+61469782899", "\",\r\n  \"body\": \"There is a natural disaster coming your way, follow the standard evacuation process\",\r\n  \"notifyURL\": \"https://2a14a18ff4fa2d7502ca27e4c459e55b.m.pipedream.net\"\r\n}\r\n")
    #print(payload)
    python_obj = json.loads(payload)
    contactif = python_obj["to"]
    contactelse = python_obj["body"]
    c = payload.replace(contactif, phonenumber)
    c = payload.replace(contactelse, messagedata)
    payload = c
    
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 3ryENJPO2nSElO4ffrNECH6wIRj5'
    }
    conn.request("POST", "/v2/messages/sms", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
def Punctuation(string): 
  
    # punctuation marks 
    punctuations = "(),'',"
  
    # traverse the given string and if any punctuation 
    # marks occur replace it with null 
    for x in string.lower(): 
        if x in punctuations: 
            string = string.replace(x, "") 
  
    # Print string without punctuation 
    return(string) 

#getoauth()
messagequery()
print()
volunteeringquery()



