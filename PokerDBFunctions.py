# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 20:55:44 2020

@author: emdan
"""

import sqlite3, RPGGameDB, itertools

def checkTables():
    conn = sqlite3.connect( 'RPGPoker.db')
    c=conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(c.fetchall())
    conn.commit()
    conn.close()

def checkColumns():
    conn = sqlite3.connect( 'RPGPoker.db')
    c=conn.cursor()
    c.execute("PRAGMA table_info(Enemies)")
    print(c.fetchall())
    conn.commit()
    conn.close()

def insertRows():
    #c.execute("INSERT INTO Players (PlayerName, PlayerPassword) VALUES ('Username1', 'Password1')")
    c.execute("INSERT INTO Players (PlayerName, PlayerPassword) VALUES (?, ?)", (test1, test2))

def checkRowsInTable(table):
    tablename = table
    conn = sqlite3.connect( 'RPGPoker.db')
    c=conn.cursor()
    c.execute("SELECT * FROM %s" % (tablename))
    print(c.fetchall())
    conn.commit()
    conn.close()

def checkRows():
    conn = sqlite3.connect( 'RPGPoker.db')
    c=conn.cursor()
    c.execute("SELECT PlayerID, PlayerName FROM Players")
    #c.execute("SELECT PlayerName, PlayerPassword FROM Players")
    print(c.fetchall())
    conn.commit()
    conn.close()

def dropTables():
    conn = sqlite3.connect( 'RPGPoker.db')
    c=conn.cursor()
    c.execute("DROP Table IF EXISTS Players")
    c.execute("DROP Table IF EXISTS Characters")
    #c.execute("DROP Table IF EXISTS Enemies")
    c.execute("DROP Table IF EXISTS Battles")
    c.execute("DROP Table IF EXISTS Attacks")
    conn.commit()
    conn.close()

def createTables():
    conn = sqlite3.connect( 'RPGPoker.db')
    c=conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS Players(
                PlayerID INTEGER PRIMARY KEY,
                PlayerName TEXT NOT NULL UNIQUE,
                PlayerPassword TEXT NOT NULL)""")

    c.execute('''CREATE TABLE IF NOT EXISTS Characters(
              CharacterID   INTEGER  NOT NULL,
              PlayerID       INTEGER  NOT NULL,
              CharacterName  TEXT NOT NULL,
              CharacterType  TEXT NOT NULL,
              Strength       INTEGER  NOT NULL,
              Speed          INTEGER  NOT NULL,
              Endurance      INTEGER  NOT NULL,
              Luck           INTEGER  NOT NULL,
              Range          INTEGER  NOT NULL,
              HitPoints      INTEGER  NOT NULL,
              ArmorClass     INTEGER  NOT NULL,
              XP             INTEGER  DEFAULT 0,
              Level          INTEGER  DEFAULT 1,
              Survivals      INTEGER  DEFAULT 0,
              Defeats        INTEGER  DEFAULT 0,
              PRIMARY KEY (CharacterID),
              FOREIGN KEY (PlayerID) REFERENCES PlayerID(Players))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Enemies(
              CharacterID   INTEGER  NOT NULL,
              CharacterName  TEXT NOT NULL,
              CharacterType  TEXT NOT NULL,
              Strength       INTEGER  NOT NULL,
              Speed          INTEGER  NOT NULL,
              Endurance      INTEGER  NOT NULL,
              Luck           INTEGER  NOT NULL,
              Range          INTEGER  NOT NULL,
              HitPoints      INTEGER  NOT NULL,
              ArmorClass     INTEGER  NOT NULL,
              XP             INTEGER  DEFAULT 0,
              Level          INTEGER  DEFAULT 1,
              Survivals      INTEGER  DEFAULT 0,
              Defeats        INTEGER  DEFAULT 0,
              PRIMARY KEY (CharacterID))''')

    #Date is UnixTime "YYYY-MM-DD HH:MM:SS.SSS"
    c.execute('''CREATE TABLE IF NOT EXISTS Battles(
              BattleID   INTEGER  NOT NULL,
              Date       TEXT NOT NULL,
              PRIMARY KEY (BattleID))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Attacks(
              BattleID   INTEGER  NOT NULL,
              RoundID    INTEGER NOT NULL,
              AttackID   INTEGER NOT NULL,
              CharacterID     INTEGER  NOT NULL,
              CharacterType    TEXT NOT NULL,
              OpponentID   INTEGER NOT NULL,
              CharacterEnduranceEnd   INTEGER NOT NULL,
              CharacterHitPointsEnd   INTEGER NOT NULL,
              PRIMARY KEY (AttackID),
              FOREIGN KEY (BattleID) REFERENCES BattleID(Battles),
              FOREIGN KEY (CharacterID) REFERENCES CharacterID(Characters))''')

    conn.commit()
    conn.close()

def enemySetup():
    EnemyCardList = [RPGGameDB.Character("Enemy" + str(x), "Enemy") for x in range(500)]
    conn = sqlite3.connect('RPGPoker.db')
    c=conn.cursor()
    for enemy in EnemyCardList:
        c.execute('''INSERT INTO Enemies
                (CharacterName, CharacterType,
                Strength, Speed, Endurance,
                Luck, Range, Hitpoints,
                ArmorClass, XP, Level,
                Survivals, Defeats)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (enemy.name,enemy.CharacterType,
                 enemy.strength,enemy.speed,enemy.endurance,
                 enemy.luck,enemy.range,enemy.hitpoints,
                 enemy.armorclass,enemy.experiencepoints,enemy.level,
                 enemy.survivals,enemy.defeats))
    conn.commit()
    conn.close

def enemyStats():
    #there are only 720 possibilities if I use the standard array
    #and only 120 if I only require the 3 main attributes from the standard array
    #print (len(list(itertools.permutations([8,10,12,13,14,15], 3))))
    #if I allow all of the possible values for 3 main attributes I get an array of 3360
    print (len(list(itertools.permutations([3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18], 3))))

if __name__ == '__main__':
    #checkTables()
    checkColumns()
    #checkRows()
    #checkRowsInTable("Characters")
    #checkColumns()
    #dropTables()
    #createTables()
    #enemySetup()
    #enemyStats()
