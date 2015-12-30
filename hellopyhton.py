# encoding=utf8

import sys
import requests
import urllib2
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
    # "orderby":12,
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

def main():
    player_database = []
    soup = Navigate_to_website(main_website, loginData, transfermarkt_website, transfermarkt_suche)
    trs = Get_player_trs(soup)
    player_IDs = Get_player_IDs(trs)
    bids = Get_bids(soup)
    Fill_player_database(player_database,trs,player_IDs,bids)
    for player in player_database:
        print(player)

# Analyse Transfermarkt
# Navigate to transfermarkt
def Navigate_to_website(login_website, login_data, dest_website, dest_data):
    session = requests.Session()
    login_website_response = session.get(login_website)
    session.post(login_website, data=login_data, headers={"Referer": login_website})
    dest_website_response = session.post(dest_website,data=dest_data)
    return BeautifulSoup(dest_website_response.content)

'''
session = requests.Session()
main_website_response = session.get(main_website)
session.post(main_website, data=loginData, headers={"Referer": main_website})
transfer_website_response = session.post(transfermarkt_website,data=transfermarkt_suche)
soup = BeautifulSoup(transfer_website_response.content)

player_database = []
'''

def Get_player_trs(soup):
    trs = []
    even_listings = soup.findAll('tr', attrs={"bgcolor":"#f1f1f2"})
    odd_listings = soup.findAll('tr', attrs={"bgcolor":"#dedede"})
    # initialize list
    for i in range(0,(len(even_listings)+len(odd_listings))):
        trs.append(0)
    # add tr at odd row
    for g in range(0,len(even_listings)):
        trs[2 * g] = even_listings[g]
    # add tr at even row
    for u in range(0,len(odd_listings)):
        trs[1 + (2 * u)] = odd_listings[u]
    return trs

'''
gerade_listen_nummern = soup.findAll('tr', attrs={"bgcolor":"#f1f1f2"})
ungerade_listen_nummern = soup.findAll('tr', attrs={"bgcolor":"#dedede"})

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
'''


def Get_player_IDs(trs):
    hrefs = []
    player_IDs = []
    # Find all links in each tr
    for tr in trs:
        new_hrefs = tr.findAll('a')
        for n in new_hrefs:
            hrefs.append(n)
    # extract the ID
    for i in range(0,len(hrefs)):
        if (i % 3) == 1:
            player_id = str(hrefs[i]['href'])[8:17]
            player_IDs.append(player_id)
    return player_IDs

def Get_bids(soup):
    bids = []
    nobrs = soup.findAll('nobr')
    for nobr in nobrs:
        bids.append(nobr.text)
    return bids

'''
hrefs = []

for tr in trs:
    new_hrefs = tr.findAll('a')
    for n in new_hrefs:
        hrefs.append(n)

player_IDs = []

for i in range(0,len(hrefs)):
    if (i % 3) == 1:
        player_id = str(hrefs[i]['href'])[8:17]
        player_IDs.append(player_id)


gebote = []
nobrs = soup.findAll('nobr')
for nobr in nobrs:
    gebote.append(nobr.text)
'''


def Fill_player_database(player_database, trs, player_IDs, bids):
    counter = 0
    for tr in trs:
        tableDatas = tr.findAll('td')
        id = player_IDs[counter]
        name_length = str(tableDatas[5].text).find("Position:")
        name = str(tableDatas[5].text)[:-((len(tableDatas[5].text))-name_length)]
        if (name[-1] == 'P'):
            name = name[:-1]
        elif (name[-1] == 'o'):
            if (name[-2] == 'P'):
                name = name[:-2]
        pos = str(tableDatas[1].text)
        alter = int(str(tableDatas[9].text).split()[0])
        staerke = int(tableDatas[7].text)
        eP = int(str(tableDatas[13].text).replace(".",""))
        tP = int(str(tableDatas[15].text).replace(".",""))
        bid = bids[counter].replace(".","")
        bid = bid.replace(" ","")
        bid = int(bid.replace("€",""))
        marktwert = str(tableDatas[17].text).replace(".","")
        marktwert = marktwert.replace(" ","")
        marktwert = int(marktwert.replace("€",""))
        gebMWDiff = round((float(bid)/float(marktwert)-1), 3)
        player = {
            "ID": id,
            "Name": name,
            "Pos": pos,
            "Alter": alter,
            "Staerke": staerke,
            "Erfahrungspunkte": eP,
            "Trainingspunkte": tP,
            "Gebot": bid,
            "Marktwert": marktwert,
            "GebotMarktWertDiff": gebMWDiff
        }
        counter = counter + 1
        player_database.append(player)

'''
counter = 0
for tr in trs:
    tableDatas = tr.findAll('td')
    id = player_IDs[counter]
    name_length = str(tableDatas[5].text).find("Position:")
    name = str(tableDatas[5].text)[:-((len(tableDatas[5].text))-name_length)]
    if (name[-1] == 'P'):
        name = name[:-1]
    elif (name[-1] == 'o'):
        if (name[-2] == 'P'):
            name = name[:-2]
    pos = str(tableDatas[1].text)
    alter = int(str(tableDatas[9].text).split()[0])
    staerke = int(tableDatas[7].text)
    eP = int(str(tableDatas[13].text).replace(".",""))
    tP = int(str(tableDatas[15].text).replace(".",""))
    gebot = gebote[counter].replace(".","")
    gebot = gebot.replace(" ","")
    gebot = int(gebot.replace("€",""))
    marktwert = str(tableDatas[17].text).replace(".","")
    marktwert = marktwert.replace(" ","")
    marktwert = int(marktwert.replace("€",""))
    gebMWDiff = round((float(gebot)/float(marktwert)-1), 3)
    player = {
        "ID": id,
        "Name": name,
        "Pos": pos,
        "Alter": alter,
        "Staerke": staerke,
        "Erfahrungspunkte": eP,
        "Trainingspunkte": tP,
        "Gebot": gebot,
        "Marktwert": marktwert,
        "GebotMarktWertDiff": gebMWDiff
    }

    counter = counter + 1
    player_database.append(player)
    # print("------------------")
'''


'''
    print("ID: ", id)
    print("Name: ", name)
    print("Pos: ", pos)
    print("Alter: ", alter)
    print("Staerke: ", staerke)
    print("Erfahrungspunkte: ", eP)
    print("Trainingspunkte: ", tP)
    print("Gebot: ", gebot)
    print("Marktwert: ", marktwert)
    print("GebotMarktWertDiff: ",gebMWDiff)
'''

'''
for player in player_database:
    print(player)
'''

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


main()