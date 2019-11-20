from bs4 import BeautifulSoup as bs
import requests



url = requests.get('https://www.xscores.com/basketball/livescores/finished-games')

#'https://www.xscores.com/basketball/livescores/finished-games')

time = []
team_home = []
team_away = []
team_scoreh = []
team_scorea = []

soup = bs(url.text, "html.parser")
#time_lab = soup.find(id='scoreTableDiv').findAll('div',{'class' :'score_ko score_cell'})

def get_data():
    for t in soup.find(id='scoreTableDiv').findAll('div',{'class' :'score_ko score_cell'}):
        time.append(t.text)



    for team_h in soup.find(id='scoreTableDiv').findAll('div',{'class' :'score_home_txt score_cell wrap'}):
        team_home.append(team_h.text)

    for team_a in soup.find(id='scoreTableDiv').findAll('div',{'class' :'score_away_txt score_cell wrap'}):

        team_away.append(team_a.text)

    for team_score1 in soup.find(id='scoreTableDiv').findAll('div',{'class' :'scoreh_ft border_bottom score_cell centerTXT'}):
        team_scoreh.append(team_score1.text)

    for team_score2 in soup.find(id='scoreTableDiv').findAll('div',{'class' :'scorea_ft score_cell centerTXT'}):
        team_scorea.append(team_score2.text)



get_data()
