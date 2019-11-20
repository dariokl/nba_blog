from flask import render_template, url_for, abort, redirect, Blueprint, request, jsonify
from webapp import db
from flask import current_app
import requests
import json
from webapp.users.forms import LoginForm
from webapp.models import Leader, Daily, News, Playerdata, Statistics
from webapp.core.forms import SelectForm
from flask_login import current_user, login_required
from selenium import webdriver
from datetime import datetime, date, timedelta
import time
import praw


core = Blueprint('core',__name__)

@core.route('/')
def index():

    #var since created with datetime for querying the database for last 24 hours
    since = datetime.now() - timedelta(days=1)
    since.strftime('%y%d%m')

    #filtering table Daily with filter .date > since
    day = db.session.query(Daily).filter(Daily.date > since).all()

    return render_template('index.html', day=day)

@core.route('/player')
@login_required
def player_info():

    #One of first views i created it can be used to show historical data of players

    myPlayer = Leader.query.all()
    return render_template('player_info.html', myPlayer=myPlayer)


@core.route('/news')
@login_required
def news():

    #Using the datetime to query table for last 24 hours.
    since = datetime.now() - timedelta(hours=12)
    since.strftime('%y%d%m')

    newsDay = db.session.query(News).filter(News.date > since).all()


    return render_template('playernews.html', newsDay=newsDay)

@core.route('/highlights', methods=["GET", "POST"])
@login_required
def highlights():

    #Using the youtube API i get the last 12 videos that are related to nba !

    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    videos = []

    search_params = {
        'key' : current_app.config['YOUTUBE_API_KEY'],
        'q' : 'nba highlights',
        'part' : 'snippet',
        'maxResults' : 12,
        'type' : 'video'
        }

    r = requests.get(search_url, params=search_params)

    video_ids = []

    rezultat = r.json()['items']


    for rez in rezultat:
        video_ids.append(rez['id']['videoId'])

    video_params = {
            'key' : current_app.config['YOUTUBE_API_KEY'],
            'id' : ','.join(video_ids),
            'part' : 'snippet,contentDetails',
            'maxResults' : 12
        }

    r = requests.get(video_url, params=video_params)
    results = r.json()['items']

    for result in results:
            video_data = {
                'id' : result['id'],
                'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                'thumbnail' : result['snippet']['thumbnails']['high']['url'],

                'title' : result['snippet']['title'],
            }

            videos.append(video_data)



    return render_template('highlights.html', videos=videos)

@core.route('/charts', methods=['GET', 'POST'])
@login_required
def charts():

    #Using Playerdata table to fill the select fields in HTML.

    myPlayer = Playerdata.query.all()
    return render_template('charts.html', myPlayer=myPlayer)


@core.route('/process' , methods=['GET','POST'])
def process():
    """ Setting up processing for charts.js, simply check for values inside the
    'selectFieldone', and 'selectFieldtwo' once i get then i use the values wich
    are esentially the ids of players i query the Statistics table to return jsonify
    data and feed the charts.js"""

    since = datetime.now() - timedelta(hours=20)
    since.strftime('%y%d%m')

    data = request.form['selectFieldone']
    data_two = request.form['selectFieldtwo']

    if data and data_two:
        data = int(data)
        player = Statistics.query.filter_by(players_id=data).filter(Statistics.date > since).first()
        player_two = Statistics.query.filter_by(players_id=data_two).filter(Statistics.date > since).first()


        return jsonify({"player_o": [player.gamesplayed, player.averageMin, player.fgm,
        player.fga, player.fgpct, player.treepm, player.treeatt, player.treepct,
        player.ftm, player.fta, player.ftpct, player.reb, player.ast, player.stl,
        player.blk, player.tov, player.ppg], 'player_t' : [player_two.gamesplayed,
        player_two.averageMin, player_two.fgm,player_two.fga, player_two.fgpct,
        player_two.treepm, player_two.treeatt, player_two.treepct,
        player_two.ftm, player_two.fta, player_two.ftpct, player_two.reb,
        player_two.ast, player_two.stl, player_two.blk, player_two.tov, player_two.ppg],
        'player_onename': player.stats.name, 'player_twoname' : player_two.stats.name,
        'first' : player.stats.pict, 'second' : player_two.stats.pict})


@core.route('/update')
@login_required
def update():
    """ Using selenium to scrape of scores every day from nba.com , i know its
    a great way to feed your website due to fact that small HTML changes can break
    down the script"""

    browser = webdriver.Chrome('C:\\Users\\User\\Desktop\\chromedriver')

    browser.get('https://www.nba.com/scores#/')


    full_scores = browser.find_elements_by_xpath('//span[@class="current_score"]')
    team_names =  browser.find_elements_by_xpath('//div[@class="score-tile__team-name"]')
    score_img = browser.find_elements_by_tag_name('img')

    #Using bulk session to import whole object!
    score_list = []
    for score, team, img in zip(full_scores, team_names, score_img):
        score_list.append({
            'name': team.text,
            'score': score.text,
            'link': img.get_attribute('src'),
        })

    db.session.bulk_insert_mappings(Daily, score_list, return_defaults=True)
    db.session.commit()

    browser.close()

    return redirect(url_for('core.index'))


@core.route('/newsupdate')
@login_required
def news_update():
    browser = webdriver.Chrome('C:\\Users\\User\\Desktop\\chromedriver')

    browser.get('https://www.rotoworld.com/sports/nba/basketball')


    links = []
    player_name = browser.find_elements_by_xpath('//div[@class="player-news-article__profile"]')
    titles_text = browser.find_elements_by_xpath('//div[@class="player-news-article__title"]')
    text = browser.find_elements_by_xpath('//div[@class="player-news-article__summary"]')
    images = browser.find_elements_by_tag_name('img')



    for img in images:
        links.append(img.get_attribute('src'))

    links2= links[1:]
    news_list = []
    for title, heading, article, links in zip(titles_text, player_name, text, links2[1::2]):
        news_list.append({
            'title': title.text,
            'heading': heading.text,
            'article': article.text,
            'pic' : links
        })

    db.session.bulk_insert_mappings(News, news_list, return_defaults=True)
    db.session.commit()

    browser.close()

    return redirect(url_for('core.news'))

@core.route('/playersupdate', methods=["GET"])
@login_required
def players_update():

    request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'stats.nba.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    url = 'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season=2019-20&SeasonType=Regular+Season&StatCategory=PTS'
    response = requests.get(url, headers = request_headers)
    stat = response.json()
    results = stat['resultSet']
    need = results['rowSet']
    #The json format was bit weird but i had to loop over ['rowSet'] to get the data i wanted

    for item in need:
        # I have already set up Playerdata table with player names and json_ids
        player = db.session.query(Playerdata).filter_by(json_id=item[0]).first()

        #If there is a player i just update the Statistics table that i have relationship with
        if player:
            new = Statistics(
            players_id = player.id,
            team = item[3],
            gamesplayed=item[4],
            averageMin=item[5],
            fgm=item[6],
            fga=item[7],
            fgpct=item[8],
            treepm=item[9],
            treeatt=item[10],
            treepct=item[11],
            ftm=item[12],
            fta=item[13],
            ftpct=item[14],
            oreb=item[15],
            dreb=item[16],
            reb=item[17],
            ast=item[18],
            stl=item[19],
            blk=item[20],
            tov=item[21],
            ppg=item[22])

            db.session.add(new)
        #Add a new player to Playerdata table if some new player enters the league
        if not player:
            create = Playerdata(
            name=item[2],
            json_id=item[0]
            )

            db.session.add(create)

        db.session.commit()


    return redirect(url_for('core.index'))

@core.route('/currentyear', methods=['GET', 'POST'])
@login_required
def current_year():

    form = SelectForm()

    since = datetime.now() - timedelta(days=1)
    since.strftime('%y%d%m')

    page = request.args.get('page', 1, type=int)
    today = db.session.query(Statistics).filter(Statistics.date > since).paginate(page=page, per_page=30)

    #If i person decide to search for a player by his name
    if request.method == 'POST' and  form.validate_on_submit():
        one1 = Playerdata.query.filter_by(name=form.select1.data).first()
        #I take the name from form and query the table and return that players id to view core.one
        return redirect(url_for('core.one', one1=one1.id))

    return render_template('playertoday.html', today=today, form=form)

@core.route('/one/<one1>', methods=["POST", "GET"])
@login_required
def one(one1):
    """ Taking the one1 var that contains players_id and i query the tables to
    create a view with all players data , and also used reddit to get 3 reddit
    posts regarding the selected players name"""

    since = datetime.now() - timedelta(days=1)
    since.strftime('%y%d%m')

    redditname= Playerdata.query.filter_by(id=one1).first()

    player = Statistics.query.filter_by(players_id=one1).filter(Statistics.date > since).first()



    reddit = praw.Reddit(client_id = 'xrMJ4ISHc6wfNQ',
                     client_secret = 't7xBmyP7x0OLYTgxz-MsvXyyq24',
                     user_agent = 'nba_blog')

    subreddit = reddit.subreddit('nba')
    hot_nba = subreddit.search(redditname.name, limit=3)

    titles = []


    for a in hot_nba:
        titles.append({
        'title' : a.title,
        'text' : a.selftext,
        'link' : a.url
        })

    return render_template('one.html', player=player, titles=titles)
