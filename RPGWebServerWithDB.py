# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 20:23:42 2019
https://pythonspot.com/login-authentication-with-flask/
https://realpython.com/introduction-to-flask-part-2-creating-a-login-page/
@author: semiclog
"""
#from flask import Flask
from flask import Flask, flash, redirect, render_template, url_for, request, session, g, jsonify, make_response
import json
import plotly
import plotly.graph_objs as go
import RPGGame #This runs the Poker functions
import RPGGameDB #Character function from this module is used in the createplayer and createteams functions
import sqlite3
import random
import datetime
import math

app = Flask(__name__)
app.secret_key = "my precious"
app.database = "RPGPoker.db"

def DatabaseBattleUpdate(PlayerCardList, EnemyCardList, CharacterIdList):
    #Create Battle entry, Battle_Character entries, and Attacks entries

    #Create Battle entry
    conn = sqlite3.connect('RPGPoker.db')
    c=conn.cursor()
    c.execute('''INSERT INTO Battles
        (Date)
        VALUES(?)''',(datetime.datetime.now(),))
    conn.commit()
    conn.close()

    #Get the BattleID we just entered
    g.db = connect_db()
    cur = g.db.execute('''SELECT max(BattleID) FROM Battles''')
    BattleID = cur.fetchone()[0]
    print('BattleID')
    print(BattleID)
    g.db.close()

    #Create Attacks entries
    for attack in range(len(PlayerCardList[0].enduranceList)):
        for adventurer in PlayerCardList+EnemyCardList:
            RoundID = math.ceil((attack+1)/len(adventurer.enduranceList))
            conn = sqlite3.connect('RPGPoker.db')
            c=conn.cursor()
            c.execute('''INSERT INTO Attacks
            (BattleID, RoundID, AttackID,
              CharacterID, CharacterType, OpponentID,
              CharacterEnduranceEnd, CharacterHitPointsEnd)
            VALUES(?,?,?,?,?,?,?,?)''',
            (BattleID, RoundID, attack, adventurer.CharacterId,adventurer.CharacterType,
            adventurer.attackEnemyList[0][attack],
            adventurer.enduranceList[0][attack], adventurer.hitpointsList[0][attack]))
            conn.commit()
            for adventurer in PlayerCardList+EnemyCardList:
                RoundID = math.ceil((attack+1)/len(adventurer.enduranceList))
                conn = sqlite3.connect('RPGPoker.db')
                c=conn.cursor()
                c.execute('''INSERT INTO Attacks
                (BattleID, RoundID, AttackID,
                  CharacterID, CharacterType, OpponentID,
                  CharacterEnduranceEnd, CharacterHitPointsEnd)
                VALUES(?,?,?,?,?,?,?,?)''',
                (BattleID, RoundID, attack, adventurer.CharacterId,adventurer.CharacterType,
                adventurer.attackEnemyList[0][attack],
                adventurer.enduranceList[0][attack], adventurer.hitpointsList[0][attack]))
                conn.commit()
                conn.close()

        #Update Character XP, Level, Survivals, defeats
        for adventurer in PlayerCardList:
            conn = sqlite3.connect('RPGPoker.db')
            c=conn.cursor()
            c.execute('''Update Characters
            set XP = ?, Level = ?, Survivals = ?, Defeats = ?
            where CharacterId = ?''',(adventurer.experiencepoints,adventurer.experiencepoints//1000,
            adventurer.survivals,adventurer.defeats,adventurer.CharacterId))
            conn.commit()
            conn.close()

def GameDB(PlayerList, EnemyList):
    RPGGameDB.Combat(PlayerList, EnemyList)



    return #

def Game(PlayerList=False, EnemyList=False):
    #When the function is called, Player and Enemy Lists are created and the Combat takes place
    #Everything else here is just formatting to send the data to the RPGPoker web page

    #Player and Enemy Lists are supplied if a logged in player initiates a battle
    if PlayerList and EnemyList:
        RPGGame.Combat(PlayerList, EnemyList)

    #Player and Enemy Lists are created in the RPGGame.Game function
        #for RPGPoker with non perpetual adventurers and enemies
    else:
        Game1=RPGGame.Game()
        PlayerList = Game1.PlayerList[0].PlayerCardList
        EnemyList = Game1.PlayerList[0].EnemyCardList
        RPGGame.Combat(PlayerList, EnemyList)

    # PRINTING the STATS
    PrintPlayerStats = RPGGame.CardOutput(PlayerList)
    PrintEnemyStats = RPGGame.CardOutput(EnemyList)

    # GRAPHING the STATS
    xaxis=["Strength","Speed","Endurance","HitPpoints","ArmorClass","Luck","Rating"]
    markertype=['circle','square','diamond', 'triangle-up', 'star', 'cross-thin']
    markercolor=['red','blue','yellow','purple','orange']
    markersize=[18, 16, 14, 12, 10]

    statsdataPlayer = []
    for i, Card in enumerate(PlayerList):
        statsdataPlayer.append(
            go.Scatter(x=xaxis, y=RPGGame.ExtractStats(Card), name=Card.name,
            opacity=0.75,
            mode='markers',
            #visible='legendonly', this sort of works but not what I want
            marker=dict(
                symbol=markertype[i],
                color=markercolor[i],
                size=markersize[i]),
            ))
    statsdataEnemy = []
    for i, Card in enumerate(EnemyList):
        statsdataEnemy.append(
            go.Scatter(x=xaxis, y=RPGGame.ExtractStats(Card), name=Card.name,
            opacity=0.75,
            mode='markers',
            marker=dict(
                symbol=markertype[i],
                color=markercolor[i],
                size=markersize[i]),
            ))
    # Edit the layout
    # I think I will eventually be forced to use this reference
        #https://stackoverflow.com/questions/51010402/html-css-plotly-plot-size
    statslayout = go.Layout(
        #title=ListName,
        #plot_bgcolor = '#ff0000',
        #paper_bgcolor = '#aacccc',
        paper_bgcolor = 'rgb(136, 185, 229)',
        autosize=True,
        #width=600,
        height=300,
        #xaxis_title='Stats',
        #yaxis_title='Value',
        yaxis=dict(dtick=1,range=[2,19]),
        scene = dict(
            yaxis=dict(range=[2,19])),
        grid = dict(columns=2, rows=1),
        legend=dict(x=0.5,y=1, orientation='v'),
        margin= dict(l= 30,r= 30,b= 60,t= 30,pad= 0))

    statsfig1 = dict(data=statsdataPlayer, layout=statslayout)
    statsfig2 = dict(data=statsdataEnemy, layout=statslayout)
    #I could create graphJSON variables with 2,3,4,5 characters and send them all in a list
    #then I could just set a button to change which dataset to plot
    #this is definitely the wrong way to do it.
    #I should be able to send all of it and then parse it on the javascript side
    graphJSON1 = json.dumps(statsfig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(statsfig2, cls=plotly.utils.PlotlyJSONEncoder)
    #print(graphJSON1)

    # GRAPHING the COMBAT
    xcombataxis=list(range(len(PlayerList[0].hitpointsList[0])))

    combathitpointdataPlayer = []
    for i, Card in enumerate(PlayerList):
        combathitpointdataPlayer.append(
            go.Scatter(x=xcombataxis, y=Card.hitpointsList[0], name=Card.name,
            mode='lines',
            line=dict(
                color='blue',
                width=2
            )))
    combathitpointdataEnemy = []
    for i, Card in enumerate(EnemyList):

        combathitpointdataEnemy.append(
            go.Scatter(x=xcombataxis, y=Card.hitpointsList[0], name=Card.name,
            mode='lines',
            line=dict(
                color='red',
                width=2
            )))

    combatendurancedataPlayer = []
    for i, Card in enumerate(PlayerList):
        combatendurancedataPlayer.append(
            go.Scatter(x=xcombataxis, y=Card.enduranceList[0], name=Card.name,
            mode='lines',
            line=dict(
                color='blue',
                width=2
            )))
    combatendurancedataEnemy = []
    for i, Card in enumerate(EnemyList):
        combatendurancedataEnemy.append(
            go.Scatter(x=xcombataxis, y=Card.enduranceList[0], name=Card.name,
            mode='lines',
            line=dict(
                color='red',
                width=2
            )))
    # Edit the layout
    # I think I will eventually be forced to use this reference
        #https://stackoverflow.com/questions/51010402/html-css-plotly-plot-size
    combatlayout = go.Layout(
        #title=ListName,
        #plot_bgcolor = '#ff0000',
        #paper_bgcolor = '#aacccc',
        paper_bgcolor = 'rgb(136, 185, 229)',
        autosize=True,
        #width=600,
        height=300,
        #xaxis_title='Stats',
        #yaxis_title='Value',
        yaxis=dict(dtick=1,range=[0,19]),
        scene = dict(
            yaxis=dict(range=[0,19])),
        grid = dict(columns=2, rows=1),
        legend=dict(x=0.5,y=1, orientation='v'),
        margin= dict(l= 30,r= 30,b= 60,t= 30,pad= 0))

    combathitpointfig = dict(
            data=combathitpointdataPlayer+combathitpointdataEnemy,
            layout=combatlayout)
    combatendurancefig = dict(
            data=combatendurancedataPlayer+combatendurancedataEnemy,
            layout=combatlayout)
    #I could create graphJSON variables with 2,3,4,5 characters and send them all in a list
    #then I could just set a button to change which dataset to plot
    #this is definitely the wrong way to do it.
    #I should be able to send all of it and then parse it on the javascript side
    graphJSONcombathitpoints = json.dumps(combathitpointfig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSONcombatendurance = json.dumps(combatendurancefig, cls=plotly.utils.PlotlyJSONEncoder)

    #Sending the Raw Lists instead of the formatted graphs and text
    PlayerHitPointsList=[x.hitpointsList[0] for x in PlayerList]
    PlayerEnduranceList=[x.enduranceList for x in PlayerList]
    PlayerAttackEnemyList=[x.attackEnemyList for x in PlayerList]
    PlayerNameList=[x.name for x in PlayerList]
    EnemyHitPointsList=[x.hitpointsList[0] for x in EnemyList]
    EnemyEnduranceList=[x.enduranceList for x in EnemyList]
    EnemyAttackEnemyList=[x.attackEnemyList for x in EnemyList]
    EnemyNameList=[x.name for x in EnemyList]
    HitPointsList = PlayerHitPointsList + EnemyHitPointsList
    EnduranceList=PlayerEnduranceList + EnemyEnduranceList
    AttackEnemyList=PlayerAttackEnemyList + EnemyAttackEnemyList
    NameList=PlayerNameList+EnemyNameList


    return [statsdataPlayer, statsdataEnemy, statslayout,
            graphJSON1, graphJSON2,
            graphJSONcombathitpoints,graphJSONcombatendurance,
            PrintPlayerStats, PrintEnemyStats,
            HitPointsList, EnduranceList, AttackEnemyList, NameList,
            xcombataxis]


@app.route('/home')
def home():
    g.db = connect_db()
    cur = g.db.execute('SELECT PlayerID, PlayerName, PlayerPassword FROM Players')
    login = [dict(IDs=row[0], Names=row[1], Passwords=row[2]) for row in cur.fetchall()]
    usernames = [x['Names'] for x in login]
    passwords = [x['Passwords'] for x in login]
    g.db.close()
    return render_template('RPGhomeDB.html', usernames=usernames, passwords=passwords)

@app.route('/login', methods=['GET', 'POST'])
def login():
    g.db = connect_db()
    cur = g.db.execute('SELECT PlayerName, PlayerPassword FROM Players')
    login = [dict(Names=row[0], Passwords=row[1]) for row in cur.fetchall()]
    usernames = [x['Names'] for x in login]
    passwords = [x['Passwords'] for x in login]
    g.db.close()
    error = None
    if request.method == 'POST':
        #if request.form['username'] not in usernames and request.form['password'] not in passwords:
        #    error = 'Invalid credentials.  Please try again.'
        if dict(Names=request.form['username'], Passwords=request.form['password']) not in login:
            error = 'Invalid credentials.  Please try again.'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were just logged in!')
            return redirect(url_for('players'))
        #logintry = dict(Names=request.form['username'], Passwords=request.form['password'])

    return render_template('RPGGameLogin.html', error=error, login=login)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('home'))

@app.route('/createplayer', methods=['GET', 'POST'])
def createplayer():
    g.db = connect_db()
    cur = g.db.execute('SELECT PlayerName, PlayerPassword FROM Players')
    login = [dict(Names=row[0], Passwords=row[1]) for row in cur.fetchall()]
    usernames = [x['Names'] for x in login]
    g.db.close()
    error = None
    if request.method == 'POST':
        if dict(Names=request.form['username']) in usernames:
            error = 'That username is already taken.  Please try again.'
        else:
            #Insert Player
            conn = sqlite3.connect('RPGPoker.db')
            c=conn.cursor()
            c.execute('INSERT INTO Players (PlayerName, PlayerPassword) VALUES (?,?)', (request.form['username'], request.form['password']))
            conn.commit()
            conn.close()

            #Get the PlayerID of the added Player
            #for team in teamlist:
            g.db = connect_db()
            cur = g.db.execute('SELECT PlayerID FROM Players WHERE PlayerName = (?)', (request.form['username'],))
            PlayerID = cur.fetchone()[0]
            g.db.close()

            #Insert 10 Adveturers into Charcters table referencing the PlayerID
            #Parameter 2 is CharacterID which is a holdover from initial coding of the Poker game
            #I need to figure out how to get rid of it.
            PlayerCardList = [RPGGame.Character("Adventurer" + str(x), 1, "Adventurer") for x in range(10)]
            conn = sqlite3.connect('RPGPoker.db')
            c=conn.cursor()
            for adventurer in PlayerCardList:
                c.execute('''INSERT INTO Characters
                (PlayerID, CharacterName, CharacterType,
                Strength, Speed, Endurance,
                Luck, Range, Hitpoints,
                ArmorClass, XP, Level,
                Survivals, Defeats)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (PlayerID, adventurer.name,adventurer.CharacterType,
                 adventurer.strength,adventurer.speed,adventurer.endurance,
                 adventurer.luck,adventurer.range,adventurer.hitpoints,
                 adventurer.armorclass,adventurer.experiencepoints,adventurer.level,
                 adventurer.survivals,adventurer.defeats))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))
    return render_template('RPGCreatePlayer.html', error=error)

@app.route('/players')
def players():
    if session:
        sessionname=session['username']
        g.db = connect_db()
        statlistdict=[]
        cur = g.db.execute('''SELECT PlayerName, CharacterName, CharacterType,
                                     Strength, Speed, Endurance, Hitpoints, Level, XP, CharacterID
                       FROM Characters
                       INNER JOIN Players ON Players.PlayerID=Characters.PlayerID
                       WHERE PlayerName = (?) AND
                       CharacterType = (?)''', (sessionname,'Adventurer'))
        statlistdict.append([dict(PlayerID=row[0], CharacterName=row[1],
                           CharacterType=row[2], Strength=row[3], Speed=row[4],
                           Endurance=row[5], HitPoints=row[6], Level=row[7], XP=row[8],
                           CharacterID=row[9]) for row in cur.fetchall()])
        g.db.close()
        return render_template('RPGPlayersDB.html', statlistdict=statlistdict)
    else: return redirect(url_for('login'))

@app.route('/details')
def details():
   return render_template('RPGdetails.html')

@app.route('/EnemyStats')
def RPGEnemyStats():
    g.db = connect_db()
    statlistdict=[]
    cur = g.db.execute('''SELECT CharacterName, Strength, Speed, Endurance, Hitpoints FROM Enemies''')
    statlistdict.append([dict(CharacterName=row[0], Strength=row[1], Speed=row[2],
                           Endurance=row[3], HitPoints=row[4]) for row in cur.fetchall()])
    sortedstatlistdict = sorted(statlistdict[0], key=lambda k:(k['Strength']+k['Speed']+k['Endurance'])/3)
    namelist = [x['CharacterName'] for x in sortedstatlistdict]
    strengthlist = [x['Strength'] for x in sortedstatlistdict]
    speedlist = [x['Speed'] for x in sortedstatlistdict]
    endurancelist = [x['Endurance'] for x in sortedstatlistdict]
    xaxis=list(range(len(sortedstatlistdict)))
    g.db.close()
    return render_template('RPGEnemyStats.html', sortedstatlistdict=sortedstatlistdict, namelist=namelist, strengthlist=strengthlist, speedlist=speedlist, endurancelist=endurancelist, xaxis=xaxis)

@app.route('/RPGPoker')
def RPGPoker():
    (statsdataPlayer,statsdataEnemy,statslayout,
    graphJSON1,graphJSON2,
    graphJSONcombathitpoints,graphJSONcombatendurance,
    PrintPlayerStats, PrintEnemyStats,
    HitPointsList, EnduranceList, AttackEnemyList, NameList,
    xcombataxis) = Game()
    return render_template('RPGPoker.html',
                               statsdataPlayer=statsdataPlayer,
                               statsdataEnemy=statsdataEnemy,
                               statslayout=statslayout,
                               graphJSON1=graphJSON1,
                               graphJSON2=graphJSON2,
                               graphJSONcombathitpoints=graphJSONcombathitpoints,
                               graphJSONcombatendurance=graphJSONcombatendurance,
                               PrintPlayerStats=PrintPlayerStats,
                               PrintEnemyStats=PrintEnemyStats,
                               HitPointsList=HitPointsList,
                               EnduranceList=EnduranceList,
                               xcombataxis=xcombataxis)

@app.route('/accept_new_stats', methods=['POST'])
def accept_new_stats():
    req = request.get_json()
    res = make_response(jsonify({"message": "JSON recieved" }), 200)

    conn = sqlite3.connect('RPGPoker.db')
    c=conn.cursor()
    c.execute('''UPDATE Characters
              SET Strength = ?, Speed = ?, Endurance = ?
              WHERE CharacterID = ?''', (req['strength'], req['speed'], req['endurance'], req['characterid'] ))
    conn.commit()
    conn.close()

    return res

@app.route('/battle/<characterid>')
def battle(characterid):
    #Grab the selected character from the database and put into a list of character objects

    #The existing combat system inputs a list of Character objects and a list of Enemy objects
    #So I need to get the data I put in the database into new Character Objects

    #Get the Character data from the database and put in a list of object(s)
    g.db = connect_db()
    PlayerCardList=[]
    statlistdict = []
    enemystatlistdict = []
    #Technically I need to be able to send multiple characters but I don't know how to manage that list yet
    #So this only grabs the single characterid and puts it in an object for the Game
    cur = g.db.execute('''SELECT PlayerID, CharacterName, CharacterType,
                Strength, Speed, Endurance,
                Luck, Range, Hitpoints,
                ArmorClass, XP, Level,
                Survivals, Defeats, CharacterID
                FROM Characters
                WHERE CharacterID = (?)''', (characterid))
    statlistdict.append([dict(PlayerID=row[0], CharacterName=row[1], CharacterType=row[2],
                   Strength=row[3], Speed=row[4], Endurance=row[5],
                   Luck=row[6], Range=row[7], HitPoints=row[8],
                   ArmorClass=row[9], XP=row[10], Level=row[11],
                   Survivals=row[12], Defeats = row[13], CharacterID=row[14]) for row in cur.fetchall()])
    #this is setup for a list of characters though I only have one at the moment
    for character in statlistdict:
        PlayerCardList.append(RPGGame.LoadCharacter(character[0]['CharacterName'], character[0]['CharacterID'],character[0]['CharacterType'],
                character[0]['Strength'], character[0]['Speed'], character[0]['Endurance'],
                character[0]['Luck'], character[0]['Range'], character[0]['HitPoints'],
                character[0]['ArmorClass'], character[0]['XP'], character[0]['Level'],
                character[0]['Survivals'], character[0]['Defeats']))
    g.db.close()

    #Get a random enemy from the database and put in a list of object(s)
    g.db = connect_db()
    EnemyCardList=[]
    EnemyId = random.randint(0,499)
    cur = g.db.execute('''SELECT CharacterName, CharacterType,
                Strength, Speed, Endurance,
                Luck, Range, Hitpoints,
                ArmorClass, XP, Level,
                Survivals, Defeats, CharacterID
                FROM Enemies
                WHERE CharacterID = (?)''', (EnemyId,))
    enemystatlistdict.append([dict(CharacterName=row[0], CharacterType=row[1],
                   Strength=row[2], Speed=row[3], Endurance=row[4],
                   Luck=row[5], Range=row[6], HitPoints=row[7],
                   ArmorClass=row[8], XP=row[9], Level=row[10],
                   Survivals=row[11], Defeats=row[12], CharacterID=row[13]) for row in cur.fetchall()])
    for character in enemystatlistdict:
        EnemyCardList.append(RPGGame.LoadCharacter(character[0]['CharacterName'],  character[0]['CharacterID'],character[0]['CharacterType'],
                character[0]['Strength'], character[0]['Speed'], character[0]['Endurance'],
                character[0]['Luck'], character[0]['Range'], character[0]['HitPoints'],
                character[0]['ArmorClass'], character[0]['XP'], character[0]['Level'],
                character[0]['Survivals'], character[0]['Defeats']))
    g.db.close()

    #Run the combat
    (statsdataPlayer,statsdataEnemy,statslayout,
    graphJSON1,graphJSON2,
    graphJSONcombathitpoints,graphJSONcombatendurance,
    PrintPlayerStats, PrintEnemyStats,
    HitPointsList, EnduranceList, AttackEnemyList, NameList,
    xcombataxis) = Game(PlayerCardList, EnemyCardList)

    #The CharacterIDs come from the database as opposed to the PlayerCardList object
    #They are defined in this function
    CharacterIDList = [characterid, EnemyId]

    #put battle/attack data back into the database
    DatabaseBattleUpdate(PlayerCardList, EnemyCardList, CharacterIDList)

    #Send the results to the web page
    return render_template('RPGBattleSettings.html',
                           statlistdict=statlistdict,
                           enemystatlistdict=enemystatlistdict,
                           statsdataPlayer=statsdataPlayer,
                           statsdataEnemy=statsdataEnemy,
                           statslayout=statslayout,
                           graphJSON1=graphJSON1,
                           graphJSON2=graphJSON2,
                           graphJSONcombathitpoints=graphJSONcombathitpoints,
                           graphJSONcombatendurance=graphJSONcombatendurance,
                           PrintPlayerStats=PrintPlayerStats,
                           PrintEnemyStats=PrintEnemyStats,
                           HitPointsList=HitPointsList,
                           EnduranceList=EnduranceList,
                           AttackEnemyList=AttackEnemyList,
                           NameList=NameList,
                           xcombataxis=xcombataxis,
                           CharacterIDList=CharacterIDList)

@app.route('/battle_settings', methods=['POST'])
def battle_settings():

    if request.method == 'POST':
        req = request.get_json()
        res = make_response(jsonify({"message": "JSON recieved" }), 200)
        print('request' + req)
        return res
    else:
        g.db = connect_db()
        statlistdict=[]
        cur = g.db.execute('''SELECT PlayerID, CharacterName, CharacterType,
                    Strength, Speed, Endurance, Hitpoints, Level, XP, CharacterID
                    FROM Characters
                    WHERE CharacterID = (?)''', (req['characterid']))
        statlistdict.append([dict(PlayerID=row[0], CharacterName=row[1],
                       CharacterType=row[2], Strength=row[3], Speed=row[4],
                       Endurance=row[5], HitPoints=row[6], Level=row[7], XP=row[8],
                       CharacterID=row[9]) for row in cur.fetchall()])
        cur = g.db.execute('''SELECT CharacterName, CharacterType,
                    Strength, Speed, Endurance, Hitpoints, Level, XP
                    FROM Enemies
                    ORDER BY RANDOM()
                    LIMIT 1''')
        statlistdict.append([dict(PlayerID='SPAWN', CharacterName=row[0],
                       CharacterType=row[1], Strength=row[2], Speed=row[3],
                       Endurance=row[4], HitPoints=row[5], Level=row[6], XP=row[7])
                        for row in cur.fetchall()])
        g.db.close()
        return render_template('RPGBattleSettings.html', statlistdict=statlistdict)

def connect_db():
    return sqlite3.connect(app.database)

if __name__ == '__main__':
#Or disable the reloader if you want to call app.run from Jupyter.
    app.run()
