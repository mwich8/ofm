# encoding=utf8

import sys
import requests
from BeautifulSoup import BeautifulSoup
import re

# Set decoding for getting rid of €-sign
reload(sys)
sys.setdefaultencoding('utf8')

# Gehalt von Stärke 0 - 28
gehalt_pro_saison =     [0,
                        12750,
                        16898,
                        21420,
                        27710,
                        36652,
                        53924,
                        75888,
                        111928,
                        152252,
                        225998,
                        325720,
                        488036,
                        737086,
                        1097690,
                        1496102,
                        2158558,
                        2813874,
                        3385006,
                        3951276,
                        4370394,
                        4726000,
                        5050292,
                        5304578,
                        5546488,
                        5750794,
                        5924228,
                        6047308,
                        6160494]

# Pos + Alter + 10 Staerken von erster Tabelle + 9 Staerken von zweiter Tabelle
numberOfValues = 21

# TODO: Change from here
# Change positions
positions = ["TW",
             "LIB",
             "LV",
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
             "RS"]

kadergroesse = 14
anzahl_tuniere_pro_saison = 4
anzahl_trainingslager_pro_saison = 4
# Adjust age
min_alter = 17
max_alter = 28
alter_range = max_alter-min_alter+1

# Bisher nur Stärke 0-19, danach nicht mehr profitable
# Adjust strength
min_staerke = 3
max_staerke = 8
staerke_range = max_staerke-min_staerke+1

anz_saison = 1

budget = 4000000

top_n_transfers = 5
# TODO: Change to here

kosten_tunier = 375000
kosten_tunier_pro_spieler = 15000
kosten_trainingslager = 250000
kosten_trainingslager_pro_spieler = 15500


kosten_turnier_pro_saison = ((kosten_tunier/kadergroesse) + kosten_tunier_pro_spieler) * anzahl_tuniere_pro_saison
kosten_trainingslager_pro_saison = ((kosten_trainingslager/kadergroesse) + kosten_trainingslager_pro_spieler) * anzahl_trainingslager_pro_saison


von_1_bis_10 = "2_id_0"
von_11_bis_19 = "3_pq_1"
"row3_pq_1_3"
"row3_pq_1_0"
"row2_id_0_1"


staerke_strings = ["2_id_0", "3_pq_1"]
# von 20 bis 28 lohnt nicht!
# von_20_bis_28 = "4_fd_2"

# Define websites
blank_pos_website_1 = "http://www.toolsofm.de/index.php/marktwerte?option=com_grid&gid="
blank_pos_website_2 = "&o_b=id&o_d=ASC&p=0&rpp=20&data_search=pos%7C"
blank_pos_website_3 = "%7Calter%7C%7C&aso=exact&ajax=1"

def Navigate_to_website(partial_website_1, partial_website_2, partial_website_3, staerke_string, pos):
    "Navigate to website"
    session = requests.Session()
    constructed_website = partial_website_1 + staerke_string + partial_website_2 + positions[pos] + partial_website_3
    marktwert_website_response = session.get(constructed_website)
    return BeautifulSoup(marktwert_website_response.content)

def Get_TRs_for_strength(soup, staerke_string):
    "Get TRs and filter players which doesn't fit age property"
    trs = []
    for alter in range(0, alter_range):
        alter_index = min_alter - 17 + alter
        row_ID = "row" + staerke_string + "_" + str(alter_index)
        tr = soup.find('tr', attrs={'id':row_ID})
        trs.append(tr)
    return trs

def fill_matrix_with_player_data(marktwert_matrix, staerken_uebrig, pos, trs, staerke_string):
    "Fill matrix with player data"
    for i in range(0,alter_range):
        alter = trs[i].findAll('td')[1].text
        marktwert_matrix[i][0] = positions[pos]
        marktwert_matrix[i][1] = alter
        anzahl_tds_in_row = len(trs[i].findAll('td'))
        if (staerke_string in staerke_strings[0]):
            for j in range(1 + min_staerke, min(4+staerke_range, anzahl_tds_in_row)):
                marktwert_matrix[i].append(trs[i].findAll('td')[j].text)
        else:
            for j in range(2, min(anzahl_tds_in_row, (2 + staerken_uebrig))):
                marktwert_matrix[i].append(trs[i].findAll('td')[j].text)
    anzahl_staerken = (len(trs[i]) - 2)
    diff_niedrige_staerken = min_staerke
    staerken_uebrig = staerken_uebrig - (anzahl_staerken - diff_niedrige_staerken)
    return staerken_uebrig

def Parse_matrix(marktwert_matrix):
    for m in marktwert_matrix:
        # make alter and marktwerte an int
        for x in range(1,len(m)):
            m[x] = int(m[x].replace(".",""))
        # make pos a string
        m[0] = str(m[0])

def Ausgaben_pro_spieler(staerke, anz_saison):
    gehalt = gehalt_pro_saison[staerke]
    if (anz_saison == 2):
        gehalt = gehalt + gehalt_pro_saison[staerke + 1]
    gesamt_trainings_kosten = (kosten_trainingslager_pro_saison * anz_saison) + (kosten_tunier * anz_saison)
    ausgaben = gehalt + gesamt_trainings_kosten
    return ausgaben

def Calculate_profit_per_player(marktwert_matrix):
    spieler_mit_gewinn = []
    for i in range(0, alter_range - anz_saison):
            # Get Position
            pos = marktwert_matrix[i][0]
            # Get Alter
            alter = marktwert_matrix[i][1]
            for j in range(2, 2 + staerke_range - anz_saison):
                # Get Stärke
                staerke = min_staerke + (j-2)
                if (marktwert_matrix[i+anz_saison][j+anz_saison] == 0):
                    gewinn = -1
                elif (marktwert_matrix[i][j] == 0):
                    gewinn = -1
                else:
                    einkaufspreis = marktwert_matrix[i][j]
                    verkaufspreis = marktwert_matrix[i+anz_saison][j+anz_saison]
                    gewinn = verkaufspreis - einkaufspreis
                    gewinn = gewinn - Ausgaben_pro_spieler(staerke, anz_saison)
                    if (gewinn > 0):
                        if (einkaufspreis <= budget):
                            player2 = {
                                "Pos": pos,
                                "Alter": alter,
                                "Staerke": staerke,
                                "Theoretischer_gewinn": gewinn,
                                "Marktwert_buy": einkaufspreis,
                                "Marktwert_sell": verkaufspreis
                            }
                            # player = [pos, alter, staerke, gewinn, einkaufspreis]
                            spieler_mit_gewinn.append(player2)
    return spieler_mit_gewinn

def Add_top_transfers(spieler_mit_gewinn, all_top_transfers):
    "Adds the top transfers per position to the global profit player list"
    # Top Transfers
    # spieler_mit_gewinn.sort(lambda x, y: cmp(y[3], x[3]))
    spieler_mit_gewinn = sorted(spieler_mit_gewinn, key=lambda k: k['Theoretischer_gewinn'])
    # Add first top_n_transfers to a new list
    for x in range(len(spieler_mit_gewinn)-top_n_transfers,len(spieler_mit_gewinn)):
        all_top_transfers.append(spieler_mit_gewinn[x])

def Calculate_overall_top_transfers(all_top_transfers, all_top_transfers_sorted):
    # Sort all top transfers in all selected positions
    # all_top_transfers.sort(lambda x, y: cmp(y[3], x[3]))
    all_top_transfers = sorted(all_top_transfers, key=lambda k: k['Theoretischer_gewinn'])
    # Add first top_n_transfers to the sorted all_top_tranfers_list
    for x in range(len(all_top_transfers)-top_n_transfers,len(all_top_transfers)):
        all_top_transfers_sorted.append(all_top_transfers[x])
        # print(all_top_transfers[x])
    if (len(all_top_transfers_sorted) == 0):
        print("KEINE PROFITABLEN TRANSFERS GEFUNDEN!")
        print("Verfeinere deine Suche...SPAST!")

def Calculate_top_n_transfers():
    all_top_transfers = []
    all_top_transfers_sorted = []
    for pos in range(0,len(positions)):
        marktwert_matrix = [[0 for x in range(2)] for x in range(alter_range)]
        staerken_uebrig = staerke_range
        for staerke_string in staerke_strings:
            soup = Navigate_to_website(blank_pos_website_1, blank_pos_website_2, blank_pos_website_3, staerke_string, pos)
            trs = Get_TRs_for_strength(soup, staerke_string)
            staerken_uebrig = fill_matrix_with_player_data(marktwert_matrix, staerken_uebrig, pos, trs, staerke_string)

        Parse_matrix(marktwert_matrix)
        spieler_mit_gewinn = Calculate_profit_per_player(marktwert_matrix)
        Add_top_transfers(spieler_mit_gewinn, all_top_transfers)
        print("Scanned: " + positions[pos])

    Calculate_overall_top_transfers(all_top_transfers, all_top_transfers_sorted)
    print("Players to buy:")
    print("--------------------------")
    for t in all_top_transfers_sorted:
        print(t)
    print("--------------------------")
    return all_top_transfers_sorted     # for call in ofm transfermarkt-Suche


def main():
    Calculate_top_n_transfers()



# main()



