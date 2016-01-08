# encoding=utf8

import sys
import requests
from BeautifulSoup import BeautifulSoup, SoupStrainer
import marktwertAnalyse
from Tkinter import *
import ttk
import json
import linecache

# Set decoding for getting rid of €-sign
reload(sys)
sys.setdefaultencoding('utf8')

# AWP Formel: EP*TP*2/(EP+TP)

file_name = "analysis.txt"

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

awp_grenzen = [
    0,
    187,
    359,
    532,
    807,
    1.216,
    1.769,
    2.539,
    3.500,
    4.487,
    5.450,
    6.413,
    7.418,
    8.464,
    9.534,
    10.624,
    11.701,
    12.718,
    13.710,
    14.663,
    15.667,
    16.780,
    17.852,
    18.620,
    19.534,
    20.243,
    20.539,
]

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
    "suchpos1":0,
    "suchpos2":0,
    "suchpos3":0,
    "suchpos4":0,
    "suchpos5":0,
    "suchpos6":0,
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
    "rel_mw_abstand":-30,
    "week":"7;7",
    "woche_von":7,
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
spieler_beobachten_website = "http://v7.www.onlinefussballmanager.de/010_transfer/beobachten.request.php?spielerid="



# Analyse Transfermarkt
# Navigate to transfermarkt
def Navigate_to_website(session, login_website, login_data, dest_website, dest_data):
    login_website_response = session.get(login_website)
    session.post(login_website, data=login_data, headers={"Referer": login_website})
    dest_website_response = session.post(dest_website,data=dest_data)
    return BeautifulSoup(dest_website_response.content)

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
        awp = (eP*tP*2)/(eP+tP)
        bid = bids[counter].replace(".","")
        bid = bid.replace(" ","")
        bid = int(bid.replace("€",""))
        marktwert = str(tableDatas[17].text).replace(".","")
        marktwert = marktwert.replace(" ","")
        marktwert = int(marktwert.replace("€",""))
        gebMWDiff = round((float(bid)/float(marktwert)-1), 3)
        min_ep = (awp_grenzen[staerke] + awp_grenzen[staerke-1])/2
        player = {
            "ID": id,
            "Name": name,
            "Pos": pos,
            "Alter": alter,
            "Staerke": staerke,
            "Erfahrungspunkte": eP,
            "Trainingspunkte": tP,
            "AWP": awp,
            "Gebot": bid,
            "Marktwert": marktwert,
            "GebotMarktWertDiff": gebMWDiff
        }
        counter = counter + 1
        if (eP > min_ep):
            player_database.append(player)

def Bid_on_player(session, player_ID):
    print("Bid on player: " + player_ID)
    constructed_website = spieler_beobachten_website + str(player_ID)
    session.get(constructed_website)


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
        preString = "KäuferGewinn: "
    player_database[x] = preString + str(player_database[x])
    print(player_database[x])
'''


# print ("Spielberechnung" in r2.text | "OFM" in r2.text)

def Search_in_Transfermarkt(profitable_transfers):
    player_database = []
    suchpos_prestring = "suchpos"
    for p in profitable_transfers:
        # print(p)
        for pos in range(0, len(transfermarkt_suchpositionen)):
            suchpos = suchpos_prestring + str(pos)
            transfermarkt_suche[suchpos] = 0
        suchpos_index = transfermarkt_suchpositionen.index(p[0])
        suchpos = suchpos_prestring + str(suchpos_index)
        transfermarkt_suche[suchpos] = suchpos_index
        min_alter = max_alter = p[1]
        alter_range = str(str(min_alter)+";"+str(max_alter))
        budget = marktwertAnalyse.budget
        min_staerke = max_starke = p[2]
        staerke_range = str(str(min_staerke)+";"+str(max_starke))
        rel_mw_abstand = -30
        transfermarkt_suche['alt_von'] = min_alter
        transfermarkt_suche['alt_bis'] = max_alter
        transfermarkt_suche['age'] = alter_range
        transfermarkt_suche['max_gebot'] = budget
        transfermarkt_suche['staerke_von'] = min_staerke
        transfermarkt_suche['staerke_bis'] = max_starke
        transfermarkt_suche['strength'] = staerke_range
        transfermarkt_suche['rel_mw_abstand'] = rel_mw_abstand
        session = requests.Session()
        soup = Navigate_to_website(session, main_website, loginData, transfermarkt_website, transfermarkt_suche)
        trs = Get_player_trs(soup)
        player_IDs = Get_player_IDs(trs)
        bids = Get_bids(soup)
        Fill_player_database(player_database,trs,player_IDs,bids)
    player_database = sorted(player_database, key=lambda k: k['AWP'])
    for player in player_database:
        print(player)
    for i in range(len(player_database)-5, len(player_database)):
        Bid_on_player(session, player_database[i]['ID'])

def Change_spielerwechsel_data(pos, alter, staerke):
    pos_index = transfermarkt_suchpositionen.index(pos)
    spielerwechsel_data['pos'] = pos_index
    spielerwechsel_data['oldFrom'] = alter
    spielerwechsel_data['oldTo'] = alter
    spielerwechsel_data['strengthFrom2'] = staerke
    spielerwechsel_data['strengthTo2'] = staerke

def Get_aktuellen_spieltag(session):
    spielerwechsel_website_response = session.get(spielerwechsel_website)
    soup = BeautifulSoup(spielerwechsel_website_response.content)
    p_tag = soup.find("p", attrs= {"class": "white bold float"})
    aktueller_spieltag = int(re.findall('\d+', str(p_tag.text))[0])
    return aktueller_spieltag

def Analyse_realistic_price(session, aktueller_spieltag, file, pos, alter, staerke):
    Change_spielerwechsel_data(pos, alter, staerke)
    analysis_string = str("Analysing " + str(pos) + " " + str(alter) + " " + str(staerke))
    file.write(analysis_string + "\n")
    print(analysis_string)
    average_price = 0
    gesamt_spielerTyp_summe = 0
    gesamt_spielerTyp_anzahl = 0
    for spieltag in range(0,aktueller_spieltag + 1):
        spielerwechsel_data['spieltag'] = spieltag
        spielerwechsel_website_response = session.post(spielerwechsel_website, data=spielerwechsel_data)
        soup = BeautifulSoup(spielerwechsel_website_response.content)
        tbody = soup.find('tbody')
        tableRows = tbody.findAll('tr', recursive=False)
        spieltag_summe = 0
        spieltag_spieler_anzahl = len(tableRows)
        for tr in tableRows:
            tableDatas = tr.findAll('td', recursive=False)
            transfersumme = str(tableDatas[len(tableDatas)-3].text)
            transfersumme = transfersumme.replace(".","")
            transfersumme = transfersumme.replace(" ","")
            transfersumme = int(transfersumme.replace("€",""))
            spieltag_summe += transfersumme
            # print(transfersumme)
        if (spieltag_spieler_anzahl > 0):
            average_price = str(spieltag_summe/spieltag_spieler_anzahl)
            file.write(average_price + "\n")
            print(average_price)
        else:
            file.write("0" + "\n")
            print("0")
        gesamt_spielerTyp_summe += spieltag_summe
        gesamt_spielerTyp_anzahl += spieltag_spieler_anzahl
    if (gesamt_spielerTyp_anzahl > 0):
        anzahl_string = "Found " + str(gesamt_spielerTyp_anzahl) + " Spieler!"
        file.write(anzahl_string + "\n")
        average_price = gesamt_spielerTyp_summe/gesamt_spielerTyp_anzahl
    return average_price

def Analyse_realistic_profit(session, aktueller_spieltag, spieler_dict):
    "Analyses the realstic profit per profit by scanning Spielerwechsel"
    pos = spieler_dict['Pos']
    alter = spieler_dict['Alter']
    staerke = spieler_dict['Staerke']
    theoretischer_gewinn = spieler_dict['Theoretischer_gewinn']
    marktwert = spieler_dict['Marktwert']
    file = open(file_name, 'a')
    print("--------BUY-------")
    file.write("--------BUY-------\n")
    transfersumme_average_buy = Analyse_realistic_price(session, aktueller_spieltag, file, pos, alter, staerke)
    print("--------SELL-------")
    file.write("--------SELL-------\n")
    transfersumme_average_sell = Analyse_realistic_price(session, aktueller_spieltag, file, pos, alter + marktwertAnalyse.anz_saison, staerke + marktwertAnalyse.anz_saison)
    real_profit = transfersumme_average_sell - transfersumme_average_buy
    real_profit = real_profit - marktwertAnalyse.Ausgaben_pro_spieler(staerke, marktwertAnalyse.anz_saison)
    spieler = {
        "Pos": pos,
        "Alter": alter,
        "Staerke": staerke,
        "Theoretischer_gewinn": theoretischer_gewinn,
        "Marktwert": marktwert,
        "Transfersumme_average_buy": transfersumme_average_buy,
        "Transfersumme_average_sell": transfersumme_average_sell,
        "Realistischer_gewinn": real_profit
    }
    spieler_json = json.dumps(spieler, ensure_ascii=False)
    print(spieler_json)
    file.write(spieler_json + "\n")
    file.close()
    return spieler

def Input_to_dict():
    input_dict = {
        "Positions": marktwertAnalyse.positions,
        "Kadergroesse": marktwertAnalyse.kadergroesse,
        "Anz_T_pro_saison": marktwertAnalyse.anzahl_tuniere_pro_saison,
        "Anz_TL_pro_saison": marktwertAnalyse.anzahl_trainingslager_pro_saison,
        "Min_alter": marktwertAnalyse.min_alter,
        "Max_alter": marktwertAnalyse.max_alter,
        "Min_staerke": marktwertAnalyse.min_staerke,
        "Max_staerke": marktwertAnalyse.max_staerke,
        "Anz_saisons": marktwertAnalyse.anz_saison,
        "Budget": marktwertAnalyse.budget,
        "Top_n_transfers": marktwertAnalyse.top_n_transfers
    }
    return input_dict


def Write_Input_to_file(file):
    input_dict = Input_to_dict()
    input_json = json.dumps(input_dict, ensure_ascii=False)
    file.write(input_json + "\n")

def Compare_JSON_to_input(input_json):
    is_same_input = True
    anz_positions = len(input_json["Positions"])
    for i in range(0, anz_positions):
        if(input_json["Positions"][i] != marktwertAnalyse.positions[i]):
            is_same_input = False
            return is_same_input
    if(input_json["Kadergroesse"] != marktwertAnalyse.kadergroesse):
        is_same_input = False
        return is_same_input
    if(input_json["Anz_T_pro_saison"] != marktwertAnalyse.anzahl_tuniere_pro_saison):
        is_same_input = False
        return is_same_input
    if(input_json["Anz_TL_pro_saison"] != marktwertAnalyse.anzahl_trainingslager_pro_saison):
        is_same_input = False
        return is_same_input
    if(input_json["Min_alter"] != marktwertAnalyse.min_alter):
        is_same_input = False
        return is_same_input
    if(input_json["Max_alter"] != marktwertAnalyse.max_alter):
        is_same_input = False
        return is_same_input
    if(input_json["Min_staerke"] != marktwertAnalyse.min_staerke):
        is_same_input = False
        return is_same_input
    if(input_json["Max_staerke"] != marktwertAnalyse.max_staerke):
        is_same_input = False
        return is_same_input
    if(input_json["Budget"] != marktwertAnalyse.budget):
        is_same_input = False
        return is_same_input
    if(input_json["Top_n_transfers"] != marktwertAnalyse.top_n_transfers):
        is_same_input = False
        return is_same_input
    return is_same_input

def Is_same_input():
    file = open(file_name, 'r')
    input_dict = file.readline()
    file.close()
    # print(input_dict)
    input_json = json.loads(input_dict)
    is_same_input = Compare_JSON_to_input(input_json)
    return is_same_input

def Write_transfers_to_file(file, profitable_transfers):
    for transfer in profitable_transfers:
        transfer_json = json.dumps(transfer, ensure_ascii=False)
        file.write(transfer_json + "\n")
    file.close()

def Read_transfers_from_file():
    profitable_transfers = []
    for i in range(2, marktwertAnalyse.top_n_transfers + 2):
        spieler = linecache.getline(file_name, i)
        spieler_dict = json.loads(spieler)
        profitable_transfers.append(spieler_dict)
        # print(spieler_as_list)
    return profitable_transfers


def main():
    # Get player data from transfermarkt
    # Set values for your search in marktwertAnalyse.
    profitable_transfers = []
    if Is_same_input():
        profitable_transfers = Read_transfers_from_file()
        for p in profitable_transfers:
            print(p)
    else:
        profitable_transfers = marktwertAnalyse.Calculate_top_n_transfers()
    # profitable_transfers = marktwertAnalyse.Calculate_top_n_transfers()
    file = open(file_name, 'w')
    Write_Input_to_file(file)
    Write_transfers_to_file(file, profitable_transfers)
    session = requests.Session()
    session.post(main_website, data=loginData, headers={"Referer": main_website})
    # Delete current analysis
    spieler_dicts = []
    aktueller_spieltag = Get_aktuellen_spieltag(session)
    for p in profitable_transfers:
        spieler = Analyse_realistic_profit(session, aktueller_spieltag, p)
        spieler_dicts.append(spieler)
    spieler_dicts = sorted(spieler_dicts, key=lambda k: k['Realistischer_gewinn'])
    print("Profitablesten Spieler-Typen für Input")
    # spieler_dicts.reverse()
    for s in spieler_dicts:
        print(s)
    # Search_in_Transfermarkt(profitable_transfers)


'''
# TODO: MAKE A GUI

def calculate(*args):
    try:
        value = float(budget_per_player.get())
        current_status = status["text"] + "Help!"
        status["text"] = current_status
        # meters.set((0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

root = Tk()
root.title("Which player to buy?")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

budget_per_player = IntVar()
text = Text(root)
min_strength = IntVar()
max_strength = IntVar()

min_age = IntVar()
max_age = IntVar()

min_strength_slider = Scale( root, variable = min_strength, to=27, orient=HORIZONTAL)
max_strength_slider = Scale( root, variable = max_strength, to=27, orient=HORIZONTAL)

min_age_slider = Scale( root, variable = min_age, to=36, orient=HORIZONTAL)
max_age_slider = Scale( root, variable = max_age, to=36, orient=HORIZONTAL)


budget_entry = ttk.Entry(mainframe, width=12, textvariable=budget_per_player)
budget_entry.grid(column=2, row=1, sticky=(W, E))

status = ttk.Label(mainframe, text="")
status.grid(row=5, columnspan=3, sticky=S)
ttk.Button(mainframe, text="Calculate players in budget", command=calculate).grid(column=2, row=2, sticky=S)

ttk.Label(mainframe, text="Budget per player").grid(column=1, row=1, sticky=E)
ttk.Label(mainframe, text="€").grid(column=3, row=1, sticky=W)

ttk.Label(mainframe, text="Stärke").grid(column=1, row=3, sticky=W)
min_strength_slider.grid(column=2, row=3, sticky=W)
max_strength_slider.grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="Alter").grid(column=1, row=4, sticky=W)
min_age_slider.grid(column=2, row=4, sticky=W)
max_age_slider.grid(column=3, row=4, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

budget_entry.focus()
root.bind('<Return>', calculate)

root.mainloop()
'''


main()
