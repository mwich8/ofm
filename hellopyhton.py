# encoding=utf8

import sys
import requests
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re

# Set decoding for getting rid of €-sign
reload(sys)
sys.setdefaultencoding('utf8')

# Set loginData
loginData = {
    "login": "Kalliy",
    "password": "x43x7kfg",
    "LoginButton":"Login",
    "js_activated":1,
    "legacyLoginForm":1
}

player = {
    "Pos": "TW",
    "Alter": 17,
    "Staerke": 1,
    "Transfersumme": -1,
    "Marktwert": -1,
    "TransferUnterschied": -1
}

spielerwechsel_data = {
    "tab":0,
    "orderby":"",
    "pos":"ALL,1,2,3,4,5,6,7,8,9,10,11,12,13,14",
    "oldFrom":17,
    "oldTo":36,
    "showFilter":0,
    "strengthFrom2":1,
    "strengthTo2":27,
    "page":0,
    "spieltag":21
}

# Define websites
main_website = "http://v7.www.onlinefussballmanager.de"
hidden_website = "http://v7.www.onlinefussballmanager.de/head-int.php?spannend=0"
transfermarkt_website = "http://v7.www.onlinefussballmanager.de/010_transfer/transfermarkt.php"
spielerwechsel_website = "http://v7.www.onlinefussballmanager.de/transfer/spielerwechsel.php"


# Navigate to website
session = requests.Session()
main_website_response = session.get(main_website)
session.post(main_website, data=loginData, headers={"Referer": main_website})
hidden_site_response = session.get(hidden_website)
spielerwechsel_website_response = session.post(spielerwechsel_website, data=spielerwechsel_data)
soup = BeautifulSoup(spielerwechsel_website_response.content)

# Fill database
player_database = []
tbody = soup.find('tbody')
tableRows = tbody.findAll('tr')
for tr in tableRows:
    tableDatas = tr.findAll('td')
    if(len(tableDatas) == 19):
        '''
        player["Pos"] = tableDatas[13].text
        player["Alter"] = tableDatas[14].text
        player["Staerke"] = tableDatas[15].text
        player["Transfersumme"] = tableDatas[16].text
        player["Marktwert"] = -1
        player["TransferUnterschied"] = -1
        '''
        # Fill Database with Pos, Alter, Staerke and Transfersumme
        for i in range(0,4):
            player_database.append(tableDatas[i+13].text)
        # Insert dummy value for Marktwert and TransferUnterschied
        player_database.append(-1)
        player_database.append(-1)
    if(len(tableDatas) == 20):
        '''
        player["Pos"] = tableDatas[14].text
        player["Alter"] = tableDatas[15].text
        player["Staerke"] = tableDatas[16].text
        player["Transfersumme"] = tableDatas[17].text
        player["Marktwert"] = -1
        player["TransferUnterschied"] = -1
        '''
        # Fill Database with Pos, Alter, Staerke and Transfersumme
        for i in range(0,4):
            player_database.append(tableDatas[i+14].text)
        # Insert dummy value for Marktwert and TransferUnterschied
        player_database.append(-1)
        player_database.append(-1)


# Set value for transfer, marktwert and difference
elem = soup.findAll('a', {'href':re.compile('/player')})

counter = 0
for e in elem:
    # Get TransferValue and parse it to int
    tS = player_database[counter*6 + 3]
    tS = tS.replace(".","")
    tS = tS.replace(" ","")
    tS = int(tS.replace("€",""))
    player_database[counter*6 + 3] = tS
    # player_database[counter*6 + 3] = "TS: " + str(tS)
    # Get MarktwertValue and parse it to int
    spieler_profil = session.get(main_website + e['href'])
    spieler_profil_soup = BeautifulSoup(spieler_profil.content)
    sP_div = spieler_profil_soup.find('div', {'id':"details_einfach"})
    sP_table = sP_div.findAll('table')[1]
    sP_marktwert_tr = sP_table.findAll('tr')[5]
    sP_marktwert_td = sP_marktwert_tr.findAll('td')[1]
    mW = sP_marktwert_td.text
    mW = mW.replace(".","")
    mW = mW.replace(" ","")
    mW = int(mW.replace("€",""))
    player_database[counter*6 + 4] = mW
    # player_database[counter*6 + 4] = "MW: " + str(mW)
    marktwert_difference = mW -tS
    player_database[counter*6 + 5] = marktwert_difference
    # player_database[counter*6 + 5] = "Gewinn: " + str(marktwert_difference)
    counter = counter + 1

# Make output readable and print it
for x in range(0,len(player_database)):
    preString = ""
    if ((x % 6) == 0):
        preString = "POS: "
    elif ((x % 6) == 1):
        preString = "Alter: "
    elif ((x % 6) == 2):
        preString = "Stärke: "
    elif ((x % 6) == 3):
        preString = "TS: "
    elif ((x % 6) == 4):
        preString = "MW: "
    elif ((x % 6) == 5):
        preString = "Gewinn: "
    player_database[x] = preString + str(player_database[x])
    print(player_database[x])



# print ("Spielberechnung" in r2.text | "OFM" in r2.text)
