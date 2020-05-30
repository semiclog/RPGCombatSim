# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:25:31 2020

@author: dadaniel
"""

import sqlite3
from RPGGame import Character

conn = sqlite3.connect( 'RPGPoker.db')
c=conn.cursor()


#####
##### Creating a new Team of Adventurers
#####
##### First create a player in the Players table or select an existing one
#####   Require a name that is UNIQUE

def SelectTeam():
    # Get the list of usernames from the database
    c.execute("SELECT PlayerID FROM Players")
    PlayerIDList = c.fetchall()[0][0]
    
    # Select a Username from the list or create a new one
    Username = input("Please enter a new Username from:" + PlayerIDList)
   
    if Username not in PlayerIDList:
        c.execute("INSERT INTO Players (PlayerName) VALUES (Username)")
    return (Username)

def addTeam():
    # Get the list of usernames from the database
    c.execute("SELECT PlayerID FROM Players")
    PlayerIDList = c.fetchall()[0][0]
    
    # Select a Username from the list or create a new one
    Username = input("Please enter a new Username from:" + PlayerIDList)
    print(Username, PlayerIDList)
    if Username in PlayerIDList:
        Username = input("That name is already taken, Please enter a new Username:")
    else:
        c.execute("INSERT INTO Players (PlayerName) VALUES (Username)")

##### Then decide which of the three teams you will be creating
c.execute("SELECT TeamID1 AND TeamID2 AND TeamID3 FROM Players Where PlayerName = Username")
TeamIDs = c.fetchall()[0][0]
print("The teams you already have are " + TeamIDs)
TeamID = input("Which team would you like to replace? 1, 2 or 3?")
if [TeamID] not in [1,2,3]:
    TeamID = input("You must enter 1, 2 or 3?")

c.execute("SELECT PlayerID FROM Players WHERE PlayerName = Username")
PlayerID = c.fetchall()[0][0]
##### Then create a team of enemies and player characters
#####   and insert them into the Characters table with the Team you just created
Characters = [Character("Adventurer" + str(x), 1, "Adventurer") for x in range(5)]
Enemies = [Character("Enemy" + str(x), 1, "Enemy") for x in range(5)]
sqlite_insert_with_param = """INSERT INTO Characters
                          (PlayerID, TeamID, CharacterName, CharacterType, Strength, Speed, Endurance, HitPoints) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
for x in Characters:
    data_tuple = (PlayerID, TeamID, x.name, 'Adventurer',x.power,x.speed,x.endurance,x.hitpoints)
    c.execute(sqlite_insert_with_param,data_tuple)
    #c.execute("INSERT INTO Characters (PlayerID, TeamID, CharacterName, CharacterType, Strength, Speed, Endurance, HitPoints) VALUES (1, 1, x.name, 'Adventurer',x.power,x.speed,x.endurance,x.hitpoints)")
    #c.execute("INSERT INTO Characters VALUES (?,?,?,?,?,?,?,?)", (PlayerID, TeamID, x.name, 'Adventurer',x.power,x.speed,x.endurance,x.hitpoints))
for x in Enemies:
    data_tuple = (PlayerID, TeamID, x.name, 'Enemy',x.power,x.speed,x.endurance,x.hitpoints)
    c.execute(sqlite_insert_with_param,data_tuple)
#    #c.execute("INSERT INTO Characters VALUES (PlayerID, TeamID, x.name, 'Adventurer',x.power,x.speed,x.endurance,x.hitpoints)")
#    c.execute("INSERT INTO Characters VALUES (?,?,?,?,?,?,?,?)", (PlayerID, TeamID, x.name, 'Enemy',x.power,x.speed,x.endurance,x.hitpoints))

conn.commit()
conn.close()