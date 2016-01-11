# encoding=utf8

import sys
import requests
from BeautifulSoup import BeautifulSoup, SoupStrainer
import marktwertAnalyse
from Tkinter import *
import ttk
import json
import linecache
import matplotlib.pyplot as plt
import math

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




def Add_players_to_database(player_database, trs, player_IDs, bids):
    # Adds all players found by the search to the database
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

# def Change_transfermarkt_suche_data(player_typ):


def Search_in_Transfermarkt(profitable_transfers):
    player_database = []
    suchpos_prestring = "suchpos"
    for p in profitable_transfers:
        # Deselect all positions
        for pos in range(0, len(transfermarkt_suchpositionen)):
            suchpos = suchpos_prestring + str(pos)
            transfermarkt_suche[suchpos] = 0
        # Set position for search
        suchpos_index = transfermarkt_suchpositionen.index(p['Pos'])
        suchpos = suchpos_prestring + str(suchpos_index)
        # Calc properties for search
        min_alter = max_alter = p['Alter']
        alter_range = str(str(min_alter)+";"+str(max_alter))
        budget = marktwertAnalyse.budget
        min_staerke = max_starke = p['Staerke']
        staerke_range = str(str(min_staerke)+";"+str(max_starke))
        rel_mw_abstand = 0
        # Set all other properties for search
        transfermarkt_suche[suchpos] = suchpos_index
        transfermarkt_suche['alt_von'] = min_alter
        transfermarkt_suche['alt_bis'] = max_alter
        transfermarkt_suche['age'] = alter_range
        transfermarkt_suche['max_gebot'] = budget
        transfermarkt_suche['staerke_von'] = min_staerke
        transfermarkt_suche['staerke_bis'] = max_starke
        transfermarkt_suche['strength'] = staerke_range
        transfermarkt_suche['rel_mw_abstand'] = rel_mw_abstand
        # Executes the search with updated data
        session = requests.Session()
        soup = Navigate_to_website(session, main_website, loginData, transfermarkt_website, transfermarkt_suche)
        trs = Get_player_trs(soup)
        player_IDs = Get_player_IDs(trs)
        bids = Get_bids(soup)
        Add_players_to_database(player_database,trs,player_IDs,bids)
    player_database = sorted(player_database, key=lambda k: k['Erfahrungspunkte'])
    player_database.reverse()
    for player in player_database:
        print(player)
    for i in range(0, min(marktwertAnalyse.top_n_transfers, len(player_database))):
        print("Bidding on player " + str(player_database[i]['ID']))
        # Bid_on_player(session, player_database[i]['ID'])

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

def Analyse_realistic_price(session, average_transfersummen, aktueller_spieltag, file, pos, alter, staerke):
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
        average_transfersummen.append(average_price)
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
    marktwert_buy = spieler_dict['Marktwert_buy']
    marktwert_sell = spieler_dict['Marktwert_sell']
    file = open(file_name, 'a')
    print("--------BUY-------")
    file.write("--------BUY-------\n")
    average_transfersummen_buy = []
    transfersumme_average_buy = Analyse_realistic_price(session, average_transfersummen_buy, aktueller_spieltag, file, pos, alter, staerke)
    print("--------SELL-------")
    file.write("--------SELL-------\n")
    average_transfersummen_sell = []
    transfersumme_average_sell = Analyse_realistic_price(session, average_transfersummen_sell, aktueller_spieltag, file, pos, alter + marktwertAnalyse.anz_saison, staerke + marktwertAnalyse.anz_saison)
    real_profit = transfersumme_average_sell - transfersumme_average_buy
    real_profit = real_profit - marktwertAnalyse.Ausgaben_pro_spieler(staerke, marktwertAnalyse.anz_saison)
    spieler = {
        "Pos": pos,
        "Alter": alter,
        "Staerke": staerke,
        "Theoretischer_gewinn": theoretischer_gewinn,
        "Marktwert_buy": marktwert_buy,
        "Marktwert_sell": marktwert_sell,
        "Transfersumme_average_buy": transfersumme_average_buy,
        "Spieltag_average_transfersummen_buy" : average_transfersummen_buy,
        "Transfersumme_average_sell": transfersumme_average_sell,
        "Spieltag_average_transfersummen_sell" : average_transfersummen_sell,
        "Realistischer_gewinn": real_profit
    }
    spieler_json = json.dumps(spieler, ensure_ascii=False)
    print(spieler_json)
    file.write(spieler_json + "\n")
    file.close()
    return spieler

def Input_to_dict(aktueller_spieltag):
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
        "Top_n_transfers": marktwertAnalyse.top_n_transfers,
        "Aktueller_spieltag": aktueller_spieltag
    }
    return input_dict


def Write_Input_to_file(file, aktueller_spieltag):
    input_dict = Input_to_dict(aktueller_spieltag)
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
    return profitable_transfers

def Calculate_x_dimension(number_of_players, plot_y_dimension):
    x_dimension = plot_y_dimension
    number_of_subplots = plot_y_dimension * x_dimension
    while (number_of_subplots < number_of_players):
        x_dimension += 1
        number_of_subplots = plot_y_dimension * x_dimension
    return x_dimension

def Plot_results(aktueller_spieltag):
    aktuelle_spieltags_liste = range(0, aktueller_spieltag + 1)
    # print(aktuelle_spieltags_liste)
    file = open(file_name, 'r')
    spieler_typen = file.readlines()
    file.close()
    spieler_typen = spieler_typen[-marktwertAnalyse.top_n_transfers:]
    number_of_players = len(spieler_typen)
    plot_y_dimension = int(math.sqrt(number_of_players))
    plot_x_dimension = Calculate_x_dimension(number_of_players, plot_y_dimension)
    fig, axes = plt.subplots(nrows=plot_y_dimension, ncols=plot_x_dimension)
    fig.tight_layout()
    # print("Reading file for plotting")
    counter = 1
    for s in spieler_typen:
        s = json.loads(s)
        title = str(s['Pos']) + " Staerke:" + str(s['Staerke'])+ " Alter:" + str(s['Alter'])
        plt.subplot(plot_y_dimension, plot_x_dimension, counter)
        plt.title(title)
        plt.grid(True)
        label = "Marktwert_buy"
        marktwert_buy_list = [s[label]] * len(aktuelle_spieltags_liste)
        # print(marktwert_buy_list)
        plt.plot(aktuelle_spieltags_liste, marktwert_buy_list, 'bo-', label=label)
        label = "Spieltag_average_transfersummen_buy"
        plt.plot(aktuelle_spieltags_liste, s[label], 'bo--', label=label)
        label = "Marktwert_sell"
        marktwert_sell_list = [s[label]] * len(aktuelle_spieltags_liste)
        # print(marktwert_sell_list)
        plt.plot(aktuelle_spieltags_liste, marktwert_sell_list, 'ro-', label=label)
        label = "Spieltag_average_transfersummen_sell"
        plt.plot(aktuelle_spieltags_liste, s[label], 'ro--', label=label)
        counter += 1
        # print(s['Realistischer_gewinn'])
    plt.show()

def Spieltag_already_analysed(aktueller_spieltag):
    file = open(file_name, 'r')
    input_dict = file.readline()
    file.close()
    # print(input_dict)
    input_json = json.loads(input_dict)
    if(input_json["Aktueller_spieltag"] != aktueller_spieltag):
        return False
    else:
        return True

def Set_input_values(budget_per_player, min_strength, max_strength, min_age, max_age, top_n_transfers, anz_saisons, anz_turniere_pro_saison, anz_trainingslager_pro_saison):
    try:
        marktwertAnalyse.budget = budget_per_player
        marktwertAnalyse.min_staerke = min_strength
        marktwertAnalyse.max_staerke = max_strength
        marktwertAnalyse.min_alter = min_age
        marktwertAnalyse.max_alter = max_age
        marktwertAnalyse.top_n_transfers = top_n_transfers
        marktwertAnalyse.anz_saison = anz_saisons
        marktwertAnalyse.anzahl_tuniere_pro_saison = anz_turniere_pro_saison
        marktwertAnalyse.anzahl_trainingslager_pro_saison = anz_trainingslager_pro_saison
        main()
        # value = float(budget_per_player)
        # current_status = status["text"] + "Help!"
        # status["text"] = current_status
        # meters.set((0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

def Create_GUI():
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

    top_n_transfers = IntVar()
    anz_saisons = IntVar()

    anz_turniere_pro_saison = IntVar()
    anz_trainingslager_pro_saison = IntVar()

    # Setup
    min_strength_slider = Scale(mainframe, variable = min_strength, from_=1, to=27, orient=HORIZONTAL)
    max_strength_slider = Scale(mainframe, variable = max_strength, from_=1, to=27, orient=HORIZONTAL)

    min_age_slider = Scale(mainframe, variable = min_age, from_=17, to=36, orient=HORIZONTAL)
    max_age_slider = Scale(mainframe, variable = max_age, from_=17, to=36, orient=HORIZONTAL)

    top_n_transfers_slider = Scale(mainframe, variable = top_n_transfers, from_=3, to=20, orient=HORIZONTAL)
    anz_saisons_slider = Scale(mainframe, variable = anz_saisons, from_=1, to=2, orient=HORIZONTAL)

    anz_turniere_pro_saison_slider = Scale(mainframe, variable = anz_turniere_pro_saison, from_=0, to=4, orient=HORIZONTAL)
    anz_trainingslager_pro_saison_slider = Scale(mainframe, variable = anz_trainingslager_pro_saison, from_=0, to=4, orient=HORIZONTAL)

    status = ttk.Label(mainframe, text="")
    status.grid(row=7, columnspan=3, sticky=S)

    # Set default values
    budget_per_player = marktwertAnalyse.budget

    min_strength_slider.set(marktwertAnalyse.min_staerke)
    max_strength_slider.set(marktwertAnalyse.max_staerke)

    min_age_slider.set(marktwertAnalyse.min_alter)
    max_age_slider.set(marktwertAnalyse.max_alter)

    top_n_transfers_slider.set(marktwertAnalyse.top_n_transfers)
    anz_saisons_slider.set(marktwertAnalyse.anz_saison)

    anz_turniere_pro_saison_slider.set(marktwertAnalyse.anzahl_tuniere_pro_saison)
    anz_trainingslager_pro_saison_slider.set(marktwertAnalyse.anzahl_trainingslager_pro_saison)

    # Row 1
    budget_entry = ttk.Entry(mainframe, width=12, textvariable=budget_per_player, justify=RIGHT)
    budget_entry.insert(END, marktwertAnalyse.budget)
    ttk.Label(mainframe, text="Budget per player").grid(column=2, row=1, sticky=E)
    budget_entry.grid(column=3, row=1, sticky=(W, E))
    ttk.Label(mainframe, text="€").grid(column=4, row=1, sticky=W)

    # Row 2
    ttk.Label(mainframe, text="Min. Stärke").grid(column=1, row=2, sticky=(S,E))
    min_strength_slider.grid(column=2, row=2, sticky=W)
    ttk.Label(mainframe, text="Max. Stärke").grid(column=3, row=2, sticky=(S,E))
    max_strength_slider.grid(column=4, row=2, sticky=W)

    # Row 3
    ttk.Label(mainframe, text="Min. Alter").grid(column=1, row=3, sticky=(S,E))
    min_age_slider.grid(column=2, row=3, sticky=W)
    ttk.Label(mainframe, text="Max. Alter").grid(column=3, row=3, sticky=(S,E))
    max_age_slider.grid(column=4, row=3, sticky=W)

    # Row 4
    ttk.Label(mainframe, text="Top n Transfers").grid(column=1, row=4, sticky=(S,E))
    top_n_transfers_slider.grid(column=2, row=4, sticky=W)
    ttk.Label(mainframe, text="Anz. Saisons").grid(column=3, row=4, sticky=(S,E))
    anz_saisons_slider.grid(column=4, row=4, sticky=W)

    # Row 5
    ttk.Label(mainframe, text="Turniere pro Saison").grid(column=1, row=5, sticky=(S,E))
    anz_turniere_pro_saison_slider.grid(column=2, row=5, sticky=W)
    ttk.Label(mainframe, text="Trainingslager pro Saison").grid(column=3, row=5, sticky=(S,E))
    anz_trainingslager_pro_saison_slider.grid(column=4, row=5, sticky=W)

    # Row 6
    ttk.Button(mainframe, text="Calculate players in budget", command= lambda: Set_input_values(budget_per_player, min_strength.get(), max_strength.get(), min_age.get(), max_age.get(), top_n_transfers.get(), anz_saisons.get(), anz_turniere_pro_saison.get(), anz_trainingslager_pro_saison.get())).grid(column=2, columnspan=2, row=6, sticky=S)

    budget_entry.focus()
    # root.bind('<Return>', calculate)

    root.mainloop()

def Get_profitable_transfers(is_same_input):
    profitable_transfers = []
    if is_same_input:
        profitable_transfers = Read_transfers_from_file()
        for p in profitable_transfers:
            print(p)
    else:
        profitable_transfers = marktwertAnalyse.Calculate_top_n_transfers()
    return profitable_transfers

def Calculate_real_profits(profitable_transfers, session, aktueller_spieltag, is_same_input):
    players_with_real_profit = []
    if (Spieltag_already_analysed(aktueller_spieltag) and is_same_input):
        file = open(file_name, 'r')
        spieler_typen = file.readlines()
        file.close()
        spieler_typen = spieler_typen[-marktwertAnalyse.top_n_transfers:]
        for spieler_typ in spieler_typen:
            spieler_typ_json = json.loads(spieler_typ)
            players_with_real_profit.append(spieler_typ_json)
    else:
        for p in profitable_transfers:
            spieler = Analyse_realistic_profit(session, aktueller_spieltag, p)
            players_with_real_profit.append(spieler)
        players_with_real_profit = sorted(players_with_real_profit, key=lambda k: k['Realistischer_gewinn'])
        players_with_real_profit.reverse()
    return players_with_real_profit

def Write_results_to_file(aktueller_spieltag, profitable_transfers, players_with_real_profit):
    # Delete current analysis
    file = open(file_name, 'w')
    Write_Input_to_file(file, aktueller_spieltag)
    Write_transfers_to_file(file, profitable_transfers)
    file = open(file_name, 'a')
    print("Profitablesten Spieler-Typen für eingegebenen Input")
    file.write("Profitablesten Spieler-Typen für eingegebenen Input\n")
    for s in players_with_real_profit:
        print(s)
        spieler_json = json.dumps(s, ensure_ascii=False)
        file.write(spieler_json + "\n")
    file.close()

def main():
    # Get player data from transfermarkt
    # Set values for your search in marktwertAnalyse.
    is_same_input = Is_same_input()
    profitable_transfers = Get_profitable_transfers(is_same_input)
    session = requests.Session()
    session.post(main_website, data=loginData, headers={"Referer": main_website})
    session = requests.Session()
    session.post(main_website, data=loginData, headers={"Referer": main_website})
    aktueller_spieltag = Get_aktuellen_spieltag(session)
    players_with_real_profit = Calculate_real_profits(profitable_transfers, session, aktueller_spieltag, is_same_input)
    Write_results_to_file(aktueller_spieltag, profitable_transfers, players_with_real_profit)
    # Plot_results(aktueller_spieltag)
    Search_in_Transfermarkt(profitable_transfers)



# TODO: MAKE A GUI


# Create_GUI()




main()
