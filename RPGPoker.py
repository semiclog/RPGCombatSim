# -*- coding: utf-8 -*-
"""
This was originally copied from RPGStats_Object_NoDecks_2 
    (same as the Dec 24 copy of the _1 version on Google Drive)
I just wanted a copy in the Flask folder for importing and possibly modifying
"""

import random
import copy
#import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot

class Game:
    
    def __init__(self, NumberOfPlayers = 2, NumberOfBattles = 5, NumberOfCards = 5):
        self.NumberOfPlayers = NumberOfPlayers
        self.NumberOfBattles = NumberOfBattles
        self.NumberOfCards = NumberOfCards
        self.EnemyCardList = [Character("Enemy" + str(x), 0, "Enemy") for x in range(NumberOfCards)]
        #Initialize the adventurer and enemy hands
        self.PlayerList = []
        #self.P0 = Player(0,NumberOfCards)
        #self.P1 = Player(1,NumberOfCards)
        #self.PlayerList.append(self.P0)
        #self.PlayerList.append(self.P1)
        #for some reason this loop overwrites the PlayerCards in Player0 with those from Player1
        for x in range(NumberOfPlayers):
            self.PlayerList.append(Player(x, NumberOfCards, self.EnemyCardList))
        #I want access to all the Cards in a single list
        self.AllCardList = [y for x in 
                            ([x.PlayerCardList for x in self.PlayerList] + [x.EnemyCardList for x in self.PlayerList])
                            for y in x]
        self.Score = [0] * NumberOfPlayers
        
    def UpdateScore(self, PlayerNumber, HitPointTotal):
        if HitPointTotal > 1:
            self.Score[PlayerNumber] += 1
#Class for Players
class Player:
    
    def __init__(self, Id, NumberOfCards, EnemyCardList):
        self.IdNumber = Id
        #self.PlayerCardList = [Character("Player" + str(Id) + "_Adventurer" + str(x), Id, "Adventurer") for x in range(NumberOfCards)]
        self.PlayerCardList = [Character("Adventurer" + str(x), Id, "Adventurer") for x in range(NumberOfCards)]
        self.experiencePoints = [0]
        self.EnemyCardList = copy.deepcopy(EnemyCardList)
        #self.EnemyCardList = [Character("Enemy" + str(x), 0, "Enemy") for x in range(NumberOfCards)]
        
    
#Class for Characters
#Initianting a character creates strength, Speed, Endurance, HitPoints, Range and Luck stats with a given name
#The stats are calculated with a "4d6 drop the lowest" method
class Character:
    def __init__(self, name, CharacterType):
        self.name = name
        self.CharacterType = CharacterType
        self.strength = CharacterRoll()
        self.speed = CharacterRoll()
        self.endurance = CharacterRoll()
        self.enduranceListTemp=[]    #This lets me track endurance during the combat of each battle
        self.enduranceList=[]    #This lets me track endurance for plotting later
        self.enduranceStart = self.endurance  #this lets me reset endurance after a battle
        self.range = CharacterRoll()
        self.luck = CharacterRoll()
        self.hitpoints = self.endurance//3 + self.luck//3 + CharacterRoll()//3
        self.hitpointsStart = self.hitpoints  #this lets me reset hit points after a battle
        self.hitpointsListTemp=[]    #This lets me track hitpoints during the combat of each battle
        self.hitpointsList=[]    #This lets me track hitpoints for plotting later
        self.armorclass = self.speed//3 + self.luck//3 + CharacterRoll()/3
        self.experiencePoints = 0
        self.survivalRate = [0,0]
        self.statList = [self.strength,self.speed,self.endurance,self.hitpoints,self.luck,self.armorclass]
        self.rating = int(sum(self.statList)//len(self.statList))
        #self.rating = ((len([x for x in self.statList if x > 5])*1)+
        #               (len([x for x in self.statList if x > 8])*2)+
        #               (len([x for x in self.statList if x > 14])*3)+
        #               (len([x for x in self.statList if x > 17])*4))

def CharacterRoll():
    statlistd6=[random.randint(1,6), random.randint(1,6), random.randint(1,6), random.randint(1,6)]
    return sum(statlistd6)-min(statlistd6)
    
#not setup yet
def Deal(PlayerCardLists, EnemyCardLists):
    return

#calculate damage
def DamageRoll(Character):
    return Character.strength//6 + Character.speed//6 + Character.endurance//6 + Character.luck//6
    
#Run the combat for each Player
def Combat(PlayerCardList, EnemyCardList, PrintOn=False):
    combatList = PlayerCardList + EnemyCardList

    #Sort both adventuerers and enemies by speed so the combatants can fight in that order
    #I don't know how python sorts identical numbers
    combatList.sort(key = lambda Character: Character.speed, reverse=True)

    #Initiate the stats list for this round
    for x in combatList:
        x.endurance = x.enduranceStart
        x.hitpoints = x.hitpointsStart
        x.enduranceListTemp = [x.enduranceStart]
        x.hitpointsListTemp = [x.hitpointsStart]
    
    RoundNumber = 1
    #loop through combat until all the adventurers or all the enemies have 0 hit points
    while (sum(PlayerCharacter.hitpoints for PlayerCharacter in PlayerCardList) > 0 and 
           sum(EnemyCharacter.hitpoints for EnemyCharacter in EnemyCardList) > 0):
        if PrintOn:
            print("\nRound" + str(RoundNumber) + " Starts\n" + 
              "Starting HitPoints - " + PrintHitPoints(PlayerCardList, EnemyCardList) + "\n" +
              "Starting Endurance - " + PrintEndurance(PlayerCardList, EnemyCardList) + "\n")
        #each characters attack a random character from the opposing list
        for Character in combatList:
            #only attack if the character is conscious
            if Character.hitpoints > 0:
                #only attack if the character has enough endurance
                if Character.endurance > 3:
                    #This first loop is if the Character is from the Player (ie. fight an enemy)
                    #Only fight if there are concious enemies to be fought
                    if Character in PlayerCardList:
                        if sum(x.hitpoints for x in EnemyCardList) > 0:
                            fightEnemy = random.sample([x for x in EnemyCardList if x.hitpoints > 0],1)[0]
                            if Character.hitpoints > 0 and Character.endurance > 0: #and armor class check succeeds
                                fightEnemy.hitpoints = max((fightEnemy.hitpoints - DamageRoll(Character)),0)
                                if fightEnemy.hitpoints == 0:
                                    fightEnemy.endurance = 0
                                if PrintOn:
                                    PrintCombat(Character, fightEnemy, combatList, PlayerCardList, EnemyCardList)
                                Character.endurance = max(Character.endurance-4,0)
                                Character.experiencePoints += 1
                    #This second loop is if the Character is from the Enemy (ie. fight an adventurer)
                    #Only fight if there are concious adventurers to be fought
                    elif sum(x.hitpoints for x in PlayerCardList) > 0:
                        fightEnemy = random.sample([x for x in PlayerCardList if x.hitpoints > 0],1)[0] 
                        if Character.hitpoints > 0 and Character.endurance > 0: #and armor class check succeeds
                            fightEnemy.hitpoints = max((fightEnemy.hitpoints - DamageRoll(Character)),0)
                            if fightEnemy.hitpoints == 0:
                                fightEnemy.endurance = 0
                            if PrintOn:
                                PrintCombat(Character, fightEnemy, combatList, PlayerCardList, EnemyCardList)
                            Character.endurance = max(Character.endurance-4,0)
                else:
                    if PrintOn:
                        PrintCombat(Character, fightEnemy, combatList, PlayerCardList, EnemyCardList)
            else:
                if PrintOn:
                    PrintCombat(Character, fightEnemy, combatList, PlayerCardList, EnemyCardList)
            RoundNumber += 1
            #everyone with hitpoints recovers 2 endurance each round
            #otherwise endurance goes to 0
            if Character.hitpoints > 0:
                Character.endurance += 1
            #Append the new stats list for this round
            for x in combatList:
                x.enduranceListTemp.append(x.endurance)
                x.hitpointsListTemp.append(x.hitpoints)
            #At then end of each characters attack, check to see if there is a winner
            if sum(x.hitpoints for x in EnemyCardList) == 0:
                print("\nThe Adventuers have won!!\n")
                break
            elif sum(x.hitpoints for x in PlayerCardList) == 0:
                print("\nThe Enemies have won!!\n")
                break
    #Append the battle stat list to each Character 
    for x in combatList:
        x.enduranceList.append(x.enduranceListTemp)
        x.hitpointsList.append(x.hitpointsListTemp)
        # Update survival rates for each character
        if x.hitpoints > 0:
            x.survivalRate[0] += 1
        else:
            x.survivalRate[1] += 1
    #Game1.UpdateScore(PlayerNumber, sum(Character.hitpoints for Character in PlayerCardList))

def PrintCombat(Character, fightEnemy, combatList, PlayerCardList, EnemyCardList):
    if Character.hitpoints == 0:
        print(("     " + Character.name + " has no hitpoints and cannot attack - ").ljust(54," ") +
              PrintHitPoints(PlayerCardList, EnemyCardList))
    elif Character.endurance <= 3:
        print(("     " + Character.name + " is exhausted and cannot attack -").ljust(54," ") + 
              PrintHitPoints(PlayerCardList, EnemyCardList))
    else:
        print("     " + Character.name + " attacked " + fightEnemy.name + 
          " for " + str(DamageRoll(Character)) + "pts of damage - " + PrintHitPoints(PlayerCardList, EnemyCardList))

def ExtractStats(Card):
    StatList = [Card.strength,Card.speed,Card.enduranceStart,Card.hitpointsStart,Card.armorclass,Card.luck,Card.rating]
    return StatList

def PrintHitPoints(PlayerCardList, EnemyCardList):
    return (("P" + str([x.hitpoints for x in PlayerCardList])).ljust(21, " ") + 
          (" E" + str([x.hitpoints for x in EnemyCardList])).ljust(21, " "))

def PrintEndurance(PlayerCardList, EnemyCardList):
    return (("P" + str([x.endurance for x in PlayerCardList])).ljust(21, " ") + 
          (" E" + str([x.endurance for x in EnemyCardList])).ljust(21, " "))

def PrintCards(CardList):
    for x in CardList:
        print(x.name.ljust(14,'_') + "_" + str(x.rating).rjust(2,' ') + "_" +
             "P: " + str(x.strength).rjust(2,' ') + " / " +
             "S: " + str(x.speed).rjust(2,' ') + " / " +
             "E: " + str(x.endurance).rjust(2,' ') + " / " +
             #"R: " + str(x.range).rjust(2,' ') + " / " +
             "L: " + str(x.luck).rjust(2,' ') + " / " +
             "HP: " + str(x.hitpoints).rjust(2,' '))

def CardOutput(CardList):
    Output = []
    for x in CardList:
        Output.append(x.name.ljust(14,'_') + "_" + str(x.rating).rjust(2,' ') + "_" +
             "P: " + str(x.strength).rjust(2,' ') + " / " +
             "S: " + str(x.speed).rjust(2,' ') + " / " +
             "E: " + str(x.enduranceStart).rjust(2,' ') + " / " +
             #"R: " + str(x.range).rjust(2,' ') + " / " +
             "L: " + str(x.luck).rjust(2,' ') + " / " +
             "HP: " + str(x.hitpointsStart).rjust(2,' '))
    return Output

def PlotStats(CardList,ListName):
    xaxis=["Strength","Speed","Endurance","HitPpoints","ArmorClass","Luck","Rating"]
    markertype=['circle','square','diamond', 'triangle-up', 'star', 'cross-thin']
    markercolor=['red','blue','yellow','purple','orange']
    markersize=[18, 16, 14, 12, 10]       
    fig = go.Figure()
    for i, Card in enumerate(CardList):
        fig.add_trace(
            go.Scatter(x=xaxis, y=ExtractStats(Card), name=Card.name,
            opacity=0.75,
            mode='markers',
            marker=dict(
                symbol=markertype[i],
                color=markercolor[i],
                size=markersize[i]),
            line=dict(
                color='MediumPurple',
                width=2
            )))
    # Edit the layout
    fig.update_layout(title=ListName,
        width=400,
        height=500,
        xaxis_title='Stats',
        yaxis_title='Value')
    fig.update_yaxes(range=[2,19])
    fig.show()

def PlotStats1(Player,ListName):
    xaxis=["Strength","Speed","Endurance","HitPpoints","ArmorClass","Luck","Rating"]
    markertype=['circle','square','diamond', 'triangle-up', 'star', 'cross-thin']
    markercolor=['red','blue','yellow','purple','orange']
    markersize=[18, 16, 14, 12, 10]       
    fig = make_subplots(rows=1, cols=2)
    for i, Card in enumerate(Player.PlayerCardList):
        fig.add_trace(
            go.Scatter(x=xaxis, y=ExtractStats(Card), name=Card.name,
            opacity=0.75,
            mode='markers',
            marker=dict(
                symbol=markertype[i],
                color=markercolor[i],
                size=markersize[i]),
            line=dict(
                color='MediumPurple',
                width=2
            )), row=1, col=1)
        
    for i, Card in enumerate(Player.EnemyCardList):
        fig.add_trace(
            go.Scatter(x=xaxis, y=ExtractStats(Card), name=Card.name,
            opacity=0.75,
            mode='markers',
            marker=dict(
                symbol=markertype[i],
                color=markercolor[i],
                size=markersize[i]),
            line=dict(
                color='MediumPurple',
                width=2
            )), row=1, col=2)
        
    # Edit the layout
    fig.update_layout(title=ListName,
        width=800,
        height=400,
        xaxis_title='Stats',
        yaxis_title='Stat Value')
    fig.update_yaxes(range=[2,19], dtick=1)
    fig.show()
    #required to show plots in Spyder
    #plot(fig)
    
def PlotCombat(Player, ListName):
    x = list(range(len(Player.PlayerCardList[0].hitpointsList[0])))
    fig = make_subplots(rows=1,cols=2)
    for Card in Player.PlayerCardList:
        fig.add_trace(
            go.Scatter(x=x, y=Card.hitpointsList[0], name=Card.name, 
            mode='lines',
            line=dict(
                color='blue',
                width=2
            )),row=1,col=1)
    for Card in Player.EnemyCardList:
        fig.add_trace(
            go.Scatter(x=x, y=Card.hitpointsList[0], name=Card.name, 
            mode='lines',
            line=dict(
                color='red',
                width=2
            )),row=1,col=1)
    for Card in Player.PlayerCardList:
        fig.add_trace(
            go.Scatter(x=x, y=Card.enduranceList[0], name=Card.name, 
            mode='lines',
            line=dict(
                color='blue',
                width=2
            )),row=1,col=2)
    for Card in Player.EnemyCardList:
        fig.add_trace(
            go.Scatter(x=x, y=Card.enduranceList[0], name=Card.name, 
            mode='lines',
            line=dict(
                color='red',
                width=2
            )),row=1,col=2)
    # Edit the layout
    fig.update_layout(title=ListName,
        width=800,
        height=400,
        xaxis_title='Battle Round',
        yaxis_title='HitPoints and Endurance')
    fig.update_yaxes(range=[0,19], dtick = 1)
    fig.show()
    #required to show plots in Spyder
    #plot(fig)

if __name__ == '__main__':
    Game1 = Game()
    PlotStats1(Game1.PlayerList[0], "Player" + str(Game1.PlayerList[0].IdNumber))
    
    #PlotStats(Game1.PlayerList[0].EnemyCardList, "Enemy")
    
    #for x in range(Game1.NumberOfBattles):
    #    Combat([x.PlayerCardList for x in Game1.PlayerList], [x.EnemyCardList for x in Game1.PlayerList], Game1.NumberOfCards, Game1.NumberOfCards)
    #    print(Game1.Score)
    
    Combat(Game1.PlayerList[0].PlayerCardList, Game1.PlayerList[0].EnemyCardList)
    
    PlotCombat(Game1.PlayerList[0], "Player" + str(Game1.PlayerList[0].IdNumber))    