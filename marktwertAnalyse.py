# encoding=utf8

import sys
import requests
from BeautifulSoup import BeautifulSoup
import re

# Set decoding for getting rid of €-sign
reload(sys)
sys.setdefaultencoding('utf8')

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

min_alter = 17
max_alter = 27
alter_range = max_alter-min_alter+1

# Bisher nur Stärke 0-10
min_staerke = 4
max_staerke = 11
staerke_range = max_staerke-min_staerke+1

# Pos + Alter + 10 Staerken von erster Tabelle + 9 Staerken von zweiter Tabelle
numberOfValues = 21         # TODO: Set value to 21

kadergroesse = 14
kosten_tunier = 375000
kosten_tunier_pro_spieler = 15000
anzahl_tuniere_pro_saision = 4
kosten_trainingslager = 250000
kosten_trainingslager_pro_spieler = 15500
anzahl_trainingslager_pro_saison = 4

kosten_turnier_pro_saison = ((kosten_tunier/kadergroesse) + kosten_tunier_pro_spieler) * anzahl_tuniere_pro_saision
kosten_trainingslager_pro_saison = ((kosten_trainingslager/kadergroesse) + kosten_trainingslager_pro_spieler) * anzahl_trainingslager_pro_saison

number_of_seasons = 1


budget = 4000000

top_n_transfers = 10

von_1_bis_10 = "2_id_0"
von_11_bis_19 = "3_pq_1"
"row3_pq_1_3"
"row3_pq_1_0"
"row2_id_0_1"


staerke_strings = ["2_id_0", "3_pq_1"]
# von 20 bis 28 lohnt nicht!
# von_20_bis_28 = "4_fd_2"

# Define websites
blank_pos_website_11 = "http://www.toolsofm.de/index.php/marktwerte?option=com_grid&gid="
blank_pos_website_22 = "&o_b=id&o_d=ASC&p=0&rpp=20&data_search=pos%7C"
blank_pos_website_33 = "%7Calter%7C%7C&aso=exact&ajax=1"
blank_pos_website_1 = "http://www.toolsofm.de/index.php/marktwerte?option=com_grid&gid=2_id_0&o_b=id&o_d=ASC&p=0&rpp=20&data_search=pos%7C"
blank_pos_website_2 = "%7Calter%7C%7C&aso=exact&ajax=1"
'''
# Initialize matrix with numberOfValues values in x direction
# and alter_range values in y direction
marktwert_matrix = [[0 for x in range(numberOfValues)] for x in range(alter_range)]

# Navigate to website
session = requests.Session()
constructed_website = blank_pos_website_1 + positions[0] + blank_pos_website_2
marktwert_website_response = session.get(constructed_website)
soup = BeautifulSoup(marktwert_website_response.content)
trs = soup.findAll('tr')
'''

'''
def filterTRs(trs):
    "Filter TRs"
    # removing header and footers
    for x in range(0,5):
        del trs[0]
    del trs[-1]
    del trs[-1]
    # remove young players
    for x in range(0,min_alter-17):
        del trs[0]
    # remove old players
    for x in range(0,36-max_alter):
        del trs[-1]

# filterTRs(trs)


def setupMatrix(mW_matrix):
    "Insert values in matrix and filter players with incorrect strength"
    for i in range(0,alter_range):
        for j in range(0,numberOfValues):
            mW_matrix[i][j] = trs[i].findAll('td')[j].text
    # remove players which don't fit strength
    for m in mW_matrix:
        # remove weak players
        for i in range(0,min_staerke-1):
            del m[2]
        # remove strong players
        for j in range(0,10-max_staerke):
            del m[-1]
        # make alter and marktwerte an int
        for x in range(1,len(m)):
            m[x] = int(m[x].replace(".",""))
        # make pos a string
        m[0] = str(m[0])
'''


'''
setupMatrix(marktwert_matrix)



# Erzeugt Eintrag für den Spieler wenn der Gewinn positiv ist
for i in range(0,alter_range - number_of_seasons):
    # Get Position
    pos = marktwert_matrix[i][0]
    # Get Alter
    alter = marktwert_matrix[i][1]
    for j in range(2, 3 + staerke_range - number_of_seasons):
        # Get Stärke
        staerke = min_staerke + (j-2)
        if (marktwert_matrix[i+number_of_seasons][j+number_of_seasons] == 0):
            gewinn = -1
        elif (marktwert_matrix[i][j] == 0):
            gewinn = -1
        else:
            einkaufspreis = marktwert_matrix[i][j]
            verkaufspreis = marktwert_matrix[i+number_of_seasons][j+number_of_seasons]
            #print("VP-EP: ", verkaufspreis, einkaufspreis, alter, staerke)
            gewinn = verkaufspreis - einkaufspreis
            gehalt = gehalt_pro_saison[staerke]
            gewinn = gewinn - gehalt - kosten_trainingslager_pro_saison - kosten_turnier_pro_saison
            #print("Gewinn: ", gewinn)
            if (gewinn > 0):
                if (einkaufspreis <= budget):
                    player = [pos, alter, staerke, gewinn]
                    spieler_mit_gewinn.append(player)


# Top Transfers

# Add first top_n_transfers to a new list
top_n_list = []
for x in range(0,top_n_transfers):
    top_n_list.append(spieler_mit_gewinn[x])



# Check other transfers if they make more profit
for i in range(top_n_transfers,len(spieler_mit_gewinn)):
    # Calculate lowest transfer option
    lowest_top_transfer_index = 0
    lowest_top_transfer_summe = top_n_list[lowest_top_transfer_index][3]
    for j in range(1, len(top_n_list)-1):
        if (top_n_list[j][3] < lowest_top_transfer_summe):
            lowest_top_transfer_index = j
            lowest_top_transfer_summe = top_n_list[j][3]
    # print(top_n_list[lowest_top_transfer_index])
    if (spieler_mit_gewinn[i][3] > lowest_top_transfer_summe):
        top_n_list[lowest_top_transfer_index] = spieler_mit_gewinn[i]
    # print(top_n_list[lowest_top_transfer_index])


# Sort Top-List by profit
top_n_list.sort(lambda x, y: cmp(y[3], x[3]))


for s in top_n_list:
    print(s)
'''

def Navigate_to_website(partial_website_1, partial_website_2, partial_website_3, staerke_string, pos):
    session = requests.Session()
    constructed_website = partial_website_1 + staerke_string + partial_website_2 + positions[pos] + partial_website_3
    marktwert_website_response = session.get(constructed_website)
    return BeautifulSoup(marktwert_website_response.content)


def main():
    all_top_transfers = []
    all_top_transfers_sorted = []
    for pos in range(0,len(positions)):
        marktwert_matrix = [[0 for x in range(2)] for x in range(alter_range)]
        spieler_mit_gewinn = []
        top_n_list = []
        staerken_uebrig = staerke_range
        # Navigate to website
        for staerke_string in staerke_strings:
            new_soup = Navigate_to_website(blank_pos_website_11, blank_pos_website_22, blank_pos_website_33, staerke_string, pos)
            # Filter players which doesn't fit age property
            trs = []
            for alter in range(0, alter_range):
                alter_index = min_alter - 17 + alter
                row_ID = "row" + staerke_string + "_" + str(alter_index)
                tr = new_soup.find('tr', attrs={'id':row_ID})
                trs.append(tr)
            # Fill matrix witch player data
            for i in range(0,alter_range):
                position = trs[i].findAll('td')[0].text
                alter = trs[i].findAll('td')[1].text
                marktwert_matrix[i][0] = position
                marktwert_matrix[i][1] = alter
                anzahl_tds_in_row = len(trs[i].findAll('td'))
                if (staerke_string in staerke_strings[0]):
                    for j in range(1 + min_staerke, min(4+staerke_range, anzahl_tds_in_row)):
                        marktwert_matrix[i].append(trs[i].findAll('td')[j].text)
                else:
                    for j in range(2, min(anzahl_tds_in_row, (2 + staerken_uebrig))):
                        marktwert_matrix[i].append(trs[i].findAll('td')[j].text)
            anzahl_staerken = (len(trs[i]) - 2)
            # print("Anzahl Stärken: ", anzahl_staerken)
            diff_niedrige_staerken = min_staerke
            staerken_uebrig = staerken_uebrig - (anzahl_staerken - diff_niedrige_staerken)

        for m in marktwert_matrix:
            # make alter and marktwerte an int
            for x in range(1,len(m)):
                m[x] = int(m[x].replace(".",""))
            # make pos a string
            m[0] = str(m[0])


        for i in range(0, alter_range - number_of_seasons):
            # Get Position
            pos = marktwert_matrix[i][0]
            # Get Alter
            alter = marktwert_matrix[i][1]
            for j in range(2, 2 + staerke_range - number_of_seasons):
                # Get Stärke
                staerke = min_staerke + (j-2)
                if (marktwert_matrix[i+number_of_seasons][j+number_of_seasons] == 0):
                    gewinn = -1
                elif (marktwert_matrix[i][j] == 0):
                    gewinn = -1
                else:
                    einkaufspreis = marktwert_matrix[i][j]
                    verkaufspreis = marktwert_matrix[i+number_of_seasons][j+number_of_seasons]
                    gewinn = verkaufspreis - einkaufspreis
                    gehalt = gehalt_pro_saison[staerke]
                    gewinn = gewinn - gehalt - kosten_trainingslager_pro_saison - kosten_turnier_pro_saison
                    if (gewinn > 0):
                        if (einkaufspreis <= budget):
                            player = [pos, alter, staerke, gewinn]
                            spieler_mit_gewinn.append(player)
        # Top Transfers
        spieler_mit_gewinn.sort(lambda x, y: cmp(y[3], x[3]))
        # Add first top_n_transfers to a new list
        for x in range(0,top_n_transfers):
            top_n_list.append(spieler_mit_gewinn[x])
        for t in top_n_list:
            all_top_transfers.append(t)
        print("Scanned: " + pos)
    all_top_transfers.sort(lambda x, y: cmp(y[3], x[3]))
    for x in range(0, top_n_transfers):
        all_top_transfers_sorted.append(all_top_transfers[x])
        print(all_top_transfers[x])


    '''
    # make alter and marktwerte an int
    for x in range(0, len(marktwert_matrix)):
        for y in range(1,len(marktwert_matrix[x])):
            marktwert_matrix[x][y] = int(marktwert_matrix[x][y].replace(".",""))
        # make pos a string
        marktwert_matrix[x][0] = str(marktwert_matrix[x][0])
        print(marktwert_matrix[x])
    '''

    '''
        session = requests.Session()
        constructed_website = blank_pos_website_1 + positions[pos] + blank_pos_website_2
        marktwert_website_response = session.get(constructed_website)
        soup = BeautifulSoup(marktwert_website_response.content)
        trs = soup.findAll('tr')
        # soup.prettify()

        for x in range(0,5):
            del trs[0]
        del trs[-1]
        del trs[-1]
        # remove young players
        for x in range(0,min_alter-17):
            del trs[0]
        # remove old players
        for x in range(0,36-max_alter):
            del trs[-1]

        for i in range(0,alter_range):
            for j in range(0,numberOfValues):
                marktwert_matrix[i][j] = trs[i].findAll('td')[j].text
        # remove players which don't fit strength
        for m in marktwert_matrix:
            # remove weak players
            for i in range(0,min_staerke-1):
                del m[2]
            # remove strong players
            for j in range(0,10-max_staerke):
                del m[-1]
            # make alter and marktwerte an int
            for x in range(1,len(m)):
                m[x] = int(m[x].replace(".",""))
            # make pos a string
            m[0] = str(m[0])

        # Erzeugt Eintrag für den Spieler wenn der Gewinn positiv ist
        for i in range(0,alter_range - number_of_seasons):
            # Get Position
            pos = marktwert_matrix[i][0]
            # Get Alter
            alter = marktwert_matrix[i][1]
            for j in range(2, 3 + staerke_range - number_of_seasons):
                # Get Stärke
                staerke = min_staerke + (j-2)
                if (marktwert_matrix[i+number_of_seasons][j+number_of_seasons] == 0):
                    gewinn = -1
                elif (marktwert_matrix[i][j] == 0):
                    gewinn = -1
                else:
                    einkaufspreis = marktwert_matrix[i][j]
                    verkaufspreis = marktwert_matrix[i+number_of_seasons][j+number_of_seasons]
                    #print("VP-EP: ", verkaufspreis, einkaufspreis, alter, staerke)
                    gewinn = verkaufspreis - einkaufspreis
                    gehalt = gehalt_pro_saison[staerke]
                    gewinn = gewinn - gehalt - kosten_trainingslager_pro_saison - kosten_turnier_pro_saison
                    #print("Gewinn: ", gewinn)
                    if (gewinn > 0):
                        if (einkaufspreis <= budget):
                            player = [pos, alter, staerke, gewinn]
                            spieler_mit_gewinn.append(player)

        # Top Transfers

        # Add first top_n_transfers to a new list
        top_n_list = []
        for x in range(0,top_n_transfers):
            top_n_list.append(spieler_mit_gewinn[x])

        # Check other transfers if they make more profit
        for i in range(top_n_transfers,len(spieler_mit_gewinn)):
            # Calculate lowest transfer option
            lowest_top_transfer_index = 0
            lowest_top_transfer_summe = top_n_list[lowest_top_transfer_index][3]
            for j in range(1, len(top_n_list)-1):
                if (top_n_list[j][3] < lowest_top_transfer_summe):
                    lowest_top_transfer_index = j
                    lowest_top_transfer_summe = top_n_list[j][3]
            # print(top_n_list[lowest_top_transfer_index])
            if (spieler_mit_gewinn[i][3] > lowest_top_transfer_summe):
                top_n_list[lowest_top_transfer_index] = spieler_mit_gewinn[i]
            # print(top_n_list[lowest_top_transfer_index])

        # Sort Top-List by profit
        top_n_list.sort(lambda x, y: cmp(y[3], x[3]))

        for s in top_n_list:
            all_top_transfers.append(s)
            # print(s)
    '''


main()

'''
all_top_transfers.sort(lambda x, y: cmp(y[3], x[3]))

for t in range(0,top_n_transfers):
    print(all_top_transfers[t])
'''




