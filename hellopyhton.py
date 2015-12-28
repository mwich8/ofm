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

transfermarkt_suchpositionen = [
    "alle",     # value: 99
    "TW",       # value: 1
    "LIB",      # value: 2
    "LV",       # ...
    "LMD",
    "RMD",
    "RV",
    "VS",
    "LM",
    "DM",
    "ZM",
    "RM",
    "LS",
    "MS",
    "RS"
]

# order transferlist by ERF(5), TP(6), min_Gebot_first(9),
# max_Gebot_first(7), min_relMW_first(12), max_relMW_first(13)

transfermarkt_suche = {
    "orderby":12,
    "suchpos0":0,
    "suchpos1":1,
    "suchpos2":2,
    "suchpos3":0,
    "suchpos4":0,
    "suchpos5":0,
    "suchpos6":6,
    "suchpos7":0,
    "suchpos8":0,
    "suchpos9":0,
    "suchpos10":0,
    "suchpos11":0,
    "suchpos12":0,
    "suchpos13":0,
    "suchpos14":0,
    "submit2": "Suchen",
    "age":"21;25",
    "alt_von":21,
    "alt_bis":25,
    "max_gebot":300000000,
    "strength":"6;11",
    "staerke_von":6,
    "staerke_bis":11,
    "rel_mw_abstand":-25,
    "week":"6;7",
    "woche_von":6,
    "woche_bis":7,
    "nation":999,
    "suche_gestartet":1
}

# Define websites
main_website = "http://v7.www.onlinefussballmanager.de"
hidden_website = "http://v7.www.onlinefussballmanager.de/head-int.php?spannend=0"
transfermarkt_website = "http://v7.www.onlinefussballmanager.de/010_transfer/transfermarkt.php"
spielerwechsel_website = "http://v7.www.onlinefussballmanager.de/transfer/spielerwechsel.php"
spieler_mitbieten_website = "http://v7.www.onlinefussballmanager.de/010_transfer/transfermarkt.php?aktion=mitbieten&spielerid="

# Analyse Transfermarkt
# Navigate to transfermarkt
session = requests.Session()
main_website_response = session.get(main_website)
session.post(main_website, data=loginData, headers={"Referer": main_website})
transfer_website_response = session.post(transfermarkt_website,data=transfermarkt_suche)
soup = BeautifulSoup(transfer_website_response.content)
divs = soup.findAll('div')
'''
for table in tables:
    print(table)
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
'''

player_database = []

# print(len(divs))

# print(divs[1])

# tables = divs[1].findAll('table')
# print(len(tables))
# print(divs[1])
# new_div = divs[1].findAll('div')
# print(new_div[0])
# new_div = new_div[0].findAll('div', recursive=False)
# transfer_table = new_div[0].findAll('tbody')
gerade_listen_nummern = soup.findAll('tr', attrs={"bgcolor":"#f1f1f2"})
ungerade_listen_nummern = soup.findAll('tr', attrs={"bgcolor":"#dedede"})
# print(len(test)+len(test2))
# print(test[0])

# initialize list
trs = []
for i in range(0,(len(gerade_listen_nummern)+len(ungerade_listen_nummern))):
    trs.append(0)
# add tr at odd row
for g in range(0,len(gerade_listen_nummern)):
    trs[2 * g] = gerade_listen_nummern[g]
# add tr at even row
for u in range(0,len(ungerade_listen_nummern)):
    trs[1 + (2 * u)] = ungerade_listen_nummern[u]

hrefs = []

for tr in trs:
    new_hrefs = tr.findAll('a')
    for n in new_hrefs:
        # print(n)
        hrefs.append(n)
    # print(tr)

player_IDs = []

for i in range(0,len(hrefs)):
    if (i % 3) == 1:
        player_id = str(hrefs[i]['href'])[8:17]
        # print(player_id)
        player_IDs.append(player_id)

'''
for tr in trs:
    tableDatas = tr.findAll('td')
    for td in tableDatas:
        print(td.text)
        print("+++++++++++++++++++++")
    print("---------------")
    print("---------------")
    print("---------------")
'''



# TODO: call "buy"-site, get GEBOT and calc GebMwDiff


counter = 0
for tr in trs:
    tableDatas = tr.findAll('td')
    id = player_IDs[counter]
    name_length = str(tableDatas[5].text).find("Position:")
    name = str(tableDatas[5].text)[:-((len(tableDatas[5].text))-name_length)]
    pos = str(tableDatas[1].text)
    alter = int(str(tableDatas[9].text).split()[0])
    staerke = int(tableDatas[7].text)
    eP = str(tableDatas[13].text).replace(".","")
    tP = str(tableDatas[15].text).replace(".","")
    marktwert = str(tableDatas[17].text).replace(".","")
    marktwert = marktwert.replace(" ","")
    marktwert = marktwert.replace("€","")
    print("ID: ", id)
    print("Name: ", name)
    print("Pos: ", pos)
    print("Alter: ", alter)
    print("Staerke: ", staerke)
    print("Erfahrungspunkte: ", eP)
    print("Trainingspunkte: ", tP)
    print("Gebot: ")
    print("Marktwert: ", marktwert)
    print("GebotMarktWertDiff: ")
    counter = counter + 1


'''
    player = {
        "ID": -1,
        "Name": "NAME",
        "Pos": tableDatas[1].text,
        "Alter": alter,
        "Staerke": tableDatas[7].text,
        "Erfahrungspunkte": tableDatas[13].text,
        "Trainingspunkte": tableDatas[15].text,
        "Gebot": -1,
        "Marktwert": marktwert,
        "GebotMarktWertDiff": -1
    }
'''


'''
    for td in tableDatas:
        print(td.text)
        #print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
    print("----------------------------------------")
'''


#print(tables[1])
'''
transfer_website_response = session.post(transfermarkt_website, data=spielerwechsel_data)
soup = BeautifulSoup(spielerwechsel_website_response.content)
'''


'''
# Analyse Spielerwechsel
# Navigate to spielerwechsel
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
        # Fill Database with Pos, Alter, Staerke and Transfersumme
        for i in range(0,4):
            player_database.append(tableDatas[i+13].text)
        # Insert dummy value for Marktwert and TransferUnterschied
        player_database.append(-1)
        player_database.append(-1)
    if(len(tableDatas) == 20):
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
'''