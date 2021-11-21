#! /usr/bin/env python3

import os
import sys
import random
import math
import time

class BadInputError(Exception):
    pass

class Player:

    def __init__(self, name):
        self.id = None
        self.name = name
        self.type = 'Human'
        self.hand = Hand()
        self.legal_cards = []
        self.wild_cards = []
        self.value_change_cards = []
        self.zero_cards = []
        self.can_skip = False
        self.can_reverse = False
        self.can_draw_two = False
        self.can_draw_four = False
        self.can_value_change = False
        self.drew = False
        self.scroll_max = 0
        self.points = 0
        self.force_draw = 0

    def addCard(self, card):
        self.drew = True
        if self.force_draw > 0:
            self.force_draw -= 1
            self.drew = False
        self.hand.addCard(card)
        
    def beginTurn(self):
        self.drew = False
        
    def didDraw(self):
        return self.drew
        
    def getLegalCards(self, color, value, zero_change=False):
        self.can_skip = False
        self.can_reverse = False
        self.can_draw_two = False
        self.can_draw_four = False
        self.can_value_change = False
        self.can_zero_change = False
        self.legal_cards = []
        self.wild_cards = []
        self.value_change_cards = []
        self.zero_cards = []
        plus_fours = []
        for card in self.hand:
            if card.isWild():
                if card.getValue() == '+4':
                    plus_fours.append(card)
                else:
                    self.wild_cards.append(card)
            elif zero_change and card.isZero():
                self.can_zero = True
                self.zero_cards.append(card)
            elif card.getColor() == color or card.getValue() == value:
                if card.getColor() != color:
                    self.can_value_change = True
                    self.value_change_cards.append(card)
                if card.getValue() == "+2":
                    self.can_draw_two = True
                elif card.getValue() == 'R':
                    self.can_reverse = True
                elif card.getValue() == 'X':
                    self.can_skip = True
                self.legal_cards.append(card)
        if len(self.legal_cards) == 0 and len(plus_fours) > 0:
            self.can_draw_four = True
            self.wild_cards += plus_fours
                
    def getValidCards(self):
        return self.legal_cards
    
    def getAllValidCards(self):
        return self.legal_cards + self.wild_cards + self.zero_cards
                
    def hasLegalCard(self):
        return len(self.legal_cards) > 0
        
    def addPoints(self, amount):
        if (self.points + amount) <= 999999999999999999999:
            self.points += amount
        
    def removeCard(self, index):
        return self.hand.removeCard(index)
    
    def assignID(self, identity):
        self.id = identity

    def getName(self):
        return self.name

    def getID(self):
        return self.id
    
    def getPoints(self):
        return self.points

    def getType(self):
        return self.type

    def getCardNum(self):
        return len(self.hand)

    def getHand(self, scroll_num=0, hide=False):
        return self.hand.show(scroll_num, hide)
    
    def getForceDraws(self):
        return self.force_draw
    
    def addForceDraw(self, num):
        self.force_draw += num
    
    def decreaseForceDraw(self):
        self.force_draw -= 1
        
    def removeForceDraw(self):
        self.force_draw = 0

    def checkCard(self, index):
        return self.hand.getCard(int(index))
    
    def discardHand(self):
        self.hand.discard()
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return '({},{})'.format(self.name, self.points)

class Hand:
    ''''deck' (Deck) : Card's Color (rgby)
       'numberOfCards' (int) : Card's Value (0-9, R, X, W, +2, +4)'''

    def __init__(self, deck=None, number_of_cards=0):
        self.hand = []
        if deck != None:
            self.draw(deck, number_of_cards)

    def __iter__(self):
        return iter(self.hand)

    def __len__(self):
        return len(self.hand)

    def __getitem__(self, item):
        try:
            return self.hand[item]
        except:
            return ''

    def addCard(self, card):
        self.hand.append(card) 
        
    def removeCard(self, index):
        index = int(index)
        if (0 <= index < len(self)):
            return self.hand.pop(index)      

    def discard(self):
        self.hand = []

    def show(self, scrollNum=0, hide=False):
        if scrollNum == -1:
            scrollNum = 0
        output = ''
        num = 0
        header, footer, upper, lower = '', '', '', ''
        header +=   ('\033[97m\u2666--\u2666\033[0m ')
        upper +=    ('\033[97m|<-|\033[0m ')
        lower +=    ('\033[97m|<-|\033[0m ')
        footer +=   ('\033[97m\u2666--\u2666\033[0m ')
        for i in range(10):
            index_num = i+(10*scrollNum)
            if index_num < len(self):
                header += (self[index_num].getRow(0,hide)+' ')
                upper += (self[index_num].getRow(1,hide)+' ')
                lower += (self[index_num].getRow(2,hide)+' ')
                footer += (self[index_num].getRow(3,hide)+' ')
                num += 1
        for j in range(10-num):
            j #unused
            header += ('     ')
            footer += ('     ')
            upper += ('     ')
            lower += ('     ')
        header +=   ('\033[97m\u2666--\u2666\033[0m ')
        upper +=    ('\033[97m|->|\033[0m ')
        lower +=    ('\033[97m|->|\033[0m ')
        footer +=   ('\033[97m\u2666--\u2666\033[0m ')
        output += ('  '+header+'\n  '+upper+'\n  '+lower+'\n  '+footer+'\n\033[97m|-(<)--')
        for k in range(num):
            output += '({})'.format(k)
            output += '--'
        for l in range(10-num):
            l #unused
            output += '-----'
        output += '(>)--|\033[0m\n'
        return output

    def getCard(self, index):
        return self.hand[index]
    
    def indexCard(self, card):
        return self.hand.index(card)

class GameSettings:
    
    player_identities = ('play1','play2','play3','play4')
    computer_names = ('Watson','SkyNet','Hal','Metal Gear')
    
    def __init__(self):
        self.player_staging = []                  #    Where Player Objs Are Stored Before Game Starts
        self.players = {}                        #    ID : Player Obj
        self.num_players = 0
        self.use_color = True 
        self.display_effects = True
        self.hide_computer_hands = True
        self.zero_change = False
        self.computer_simulation = False
        self.main_menu_error = ''
        self.computer_speed = 'normal'
        
    def canAddPlayer(self):
        return (self.num_players < 4)
    
    def canRemovePlayer(self):
        return (self.num_players > 0)
    
    def canBegin(self):
        return (self.num_players > 1)
        
    def addPlayer(self, player):
        self.player_staging.append(player)
        self.num_players += 1
        
    def removePlayer(self, number):
        number -= 1
        del self.player_staging[number]
        self.num_players -= 1
        
    def clearStaging(self):
        self.num_players = 0
        self.player_staging = []
        
    def finalizePlayers(self):
        self.players.clear()
        identity = 0
        for player in self.player_staging:
            player_id = self.player_identities[identity]
            player.assignID(player_id)
            self.players[player_id] = player
            identity += 1
        
    def getPlayerNum(self):
        return self.num_players
    
    def getComputerName(self):
        complete = False
        index = self.num_players
        while not complete:
            name = self.computer_names[index]
            complete = True
            for player in self.player_staging:
                if player.getName() == name:
                    index += 1
                    if index >= len(self.computer_names):
                        index = 0
                        complete = False
            
        return self.computer_names[index]
    
    def getRandomIdentity(self):
        '''For Getting a Random Player for First Turn.'''
        return random.choice(self.players.keys())
    
    def compileMainMenuElements(self):
        def getBlankSpace(word, total):
            return " "*(total-len(word))
        
        def getPlayerBox(player_num, row_num):
            if row_num == 1:
                name = self.player_staging[player_num-1].getName()
                return '{}{}'.format(name, getBlankSpace(name, 29))
            elif row_num == 2:
                points = self.player_staging[player_num-1].getPoints()
                return 'Points: {}{}'.format(points, getBlankSpace(str(points), 21))
                
        self.main_menu_elements= {'play1row1':'No Player                    ','play1row2':'                             ',
                                'play2row1':'No Player                    ',
                                'play2row2':'                             ',
                                'play3row1':'No Player                    ','play3row2':'                             ',
                                'play4row1':'No Player                    ',
                                'play4row2':'                             ', 
                                'play1box':'\033[90m','play2box':'\033[90m','play3box':'\033[90m','play4box':'\033[90m',
                                'beginBox':'\033[90m','addBox':'\033[97m','removeBox':'\033[90m'
                                }
        player_box_key = 'play{}box'
        player_row_key = 'play{}row{}'
        i = 1
        for j in self.player_staging:
            j
            colorCode = ['\033[91m','\033[94m','\033[92m','\033[93m']
            key = player_box_key.format(i)
            self.main_menu_elements[key] = colorCode[i-1]
            self.main_menu_elements[player_row_key.format(i,1)] = getPlayerBox(i, 1)
            self.main_menu_elements[player_row_key.format(i,2)] = getPlayerBox(i, 2)
            i+=1
        if self.canBegin():
            self.main_menu_elements['beginBox'] = '\033[95m'
        if not self.canAddPlayer():
            self.main_menu_elements['addBox'] = '\033[90m'
        if self.canRemovePlayer():
            self.main_menu_elements['removeBox'] = '\033[97m'
            
    def changeComputerSpeed(self):
        if self.computer_speed == 'slow':
            self.computer_speed = 'normal'
        elif self.computer_speed == 'normal':
            self.computer_speed = 'fast'
        elif self.computer_speed == 'fast':
            self.computer_speed = 'slow'
    
    def getMainMenuElements(self):
        return self.main_menu_elements

class Deck:
    ''''shuffle' (bool) : shuffle deck.'''

    colors =     ('red','yellow','green','blue')
    values =     ('0','1','2','3','4','5','6','7','8','9','X','R','+2')
    
    def __init__(self, populate):
        '''Initializes proper deck of 108 Uno Cards.'''
        self.deck = []
        if populate:
            self.populate(True)
            
    def __getitem__(self, index):
        return self.deck[index]
            
    def populate(self, shuffle=True):
        for color in self.colors:
            for value in self.values:
                self.deck.append(Card(color, value))
                if value != '0':
                    self.deck.append(Card(color, value))
        for i in range(4):
            i #unused
            self.deck.append(Card('wild', '+4'))
            self.deck.append(Card('wild', 'W'))
        if shuffle:
            self.shuffle()

    def __iter__(self):
        return iter(self.deck)

    def __len__(self):
        return len(self.deck)

    def draw(self):
        return self.deck.pop()
    
    def place(self, card):
        return self.deck.append(card)
    
    def insert(self, card):
        self.deck.insert(0, card)

    def shuffle(self):
        random.shuffle(self.deck)

class ComputerPlayer(Player):
    
    def __init__(self, name):
        super().__init__(name)
        self.type = 'Computer'
        self.begun = False
        self.colors_in_hand = {'red':0, 'blue':0, 'green':0, 'yellow':0, 'wild':0}
        self.colors_out_hand = {}
        self.current_color = ""
        
    def addCard(self, card):
        Player.addCard(self, card)
        color = card.getColor()
        self.colors_in_hand[color] += 1
        
    def indexCard(self, card_color, card_value):
        for card in self.hand:
            if card.getValue() == card_value:
                if card_value in ('+4', 'W'):
                    return self.hand.indexCard(card)
                else:
                    if card.getColor() == card_color:
                        return self.hand.indexCard(card)
        raise ValueError("Card Cannot Be Found")
        
    def think(self, match):
        card = None
        self.current_color = match.current_color
        current_value = match.current_value
        zero_change_rule = match.zero_change
        two_players = False
        previous_turn_id = match.getNextTurn(True)
        next_turn_id = match.getNextTurn(False)
        previous_player = match.getPlayer(previous_turn_id)
        #nextPlayer = match.getPlayer(nextTurnID)
        if previous_turn_id == next_turn_id:
            two_players = True
            if self.can_skip == False and self.can_reverse == True:
                self.can_skip = True
            self.can_reverse = False
        
        self.getLegalCards(self.current_color, current_value, zero_change_rule)

        ### DRAW CASE ###
        
        if len(self.legal_cards) == 0 and len(self.wild_cards) == 0:
            return "d"
        
        else:
            
            ### NO LEGAL CARD, USE WILD CARD ###
            
            if len(self.legal_cards) == 0:
                
                if zero_change_rule and self.can_zero_change:
                    best_zero_color = self.getBestColor(self.zero_cards)
                    card = self.getCardByColor(self.zero_cards, best_zero_color)
                    
                else:
                    
                    if self.can_draw_four:
                        card = self.getCardByValue(self.wild_cards, "+4")
                        print(card)
                        
                    else:
                        card = random.choice(self.wild_cards)
                
            else:
                
                ### HAS LEGAL CARD ###
                
                if two_players and self.can_skip: #Always play a skip card in a two player game
                    #print("Shed Skip Strategy")
                    card = self.getCardByValue(self.legal_cards,"R", "X")
                    
                if self.can_reverse and previous_player.didDraw():
                    #print("Reverse Strategy")
                    reverse_cards = self.getAllCardsByValue(self.legal_cards, "R")
                    for reverse_card in reverse_cards:
                        if reverse_card.getColor() == self.current_color:
                            card = reverse_card
                    
                if self.can_value_change:
                    # Computer Can Value Change, However, Should it?
                    # Computer Checks to See if Value Change Color is Better Than Current
                    current_color_num = self.colors_in_hand[self.current_color]
                    best_value_change_color = self.getBestColor(self.value_change_cards)
                    if self.colors_in_hand[best_value_change_color] > current_color_num or len(self.value_change_cards) == len(self.legal_cards):
                        card = self.getCardByColor(self.value_change_cards, best_value_change_color)
                    
                    
                if card == None:
                    #print("Random Strategy")
                    card = random.choice(list(set(self.legal_cards) - set(self.value_change_cards)))
            
        color = card.getColor()
        self.colors_in_hand[color] -= 1
        return str(self.indexCard(card.getColor(), card.getValue()))
    
    def getWildColor(self):
        max_key = max(self.colors_in_hand, key=self.colors_in_hand.get)
        if max_key == 'wild':
            return random.choice(('r','g','b','y'))
        else:
            return max_key
        
    def getCardByValue(self, card_list, *values):
        for card in card_list:
            if card.getValue() in values:
                return card
            
    def getAllCardsByValue(self, card_list, *values):
        cards = []
        for card in card_list:
            if card.getValue() in values:
                cards.append(card)
        return cards
    
    def getCardByColor(self, card_list, *colors):
        for card in card_list:
            if card.getColor() in colors:
                return card
    
    def getBestColor(self, card_list):
        best_color = None
        best_color_num = 0
        for card in card_list:
            color = card.getColor()
            if self.colors_in_hand[color] > best_color_num:
                best_color = color
                best_color_num = self.colors_in_hand[color]
        return best_color

class Card:
    '''
    'suit' (string) : Card's Color (rgby)
    'rank' (string) : Card's Value (0-9, R, X, W, +2, +4)
    '''

    colors = {
        'red'       :   '\033[91m',
        'green'     :   '\033[92m',
        'yellow'    :   '\033[93m',
        'blue'      :   '\033[94m',
        'purple'    :   '\033[95m',
        'cyan'      :   '\033[96m',
        'white'     :   '\033[97m',
        'wild'      :   '',
        'dwild'     :   '',
        'dred'       :   '\033[31m',
        'dgreen'     :   '\033[32m',
        'dyellow'    :   '\033[33m',
        'dblue'      :   '\033[34m',
        'dpurple'    :   '\033[35m',
        'dcyan'      :   '\033[36m',
        'dwhite'     :   '\033[37m',
    }
    
    id_map = {
        'red':'R','blue':'B','green':'G','yellow':'Y','wild':'W',
        '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
        '+2':'+','R':'R','W':'W','+4':'$','X':'X'
    }

    big_nums = {
        "0" : [" .d888b. ","d88P Y88b","888   888","888   888","888   888","888   888","d88P Y88b"," \"Y888P\" "],
        "1" : ["  d888   "," d8888   ","   888   ","   888   ","   888   ","   888   ","   888   "," 8888888 "],
        "2" : [".d8888b. ","d88P  Y88","d8    888","    .d88P",".od888P\" ","d88P\"    ","888\"     ","888888888"],
        "3" : [" .d8888b.","d88P  Y88","     .d88","   8888\" ","     \"Y8b","888    88","Y88b  d88"," \"Y8888P\""],
        "4" : ["    d88b ","   d8P88 ","  d8  88 "," d8   88 ","d8    88 ","888888888","      88 ","      88 "],
        "5" : ["888888888","888      ","888      ","8888888b ","   \"Y88b ","      888","Y88b d88P","\"Y8888P\" "],
        "6" : [" .d888b. ","d88P Y88b","888      ","888d888b ","888P \"Y8b","888   888","Y88b d88b"," \"Y888P\" "],
        "7" : ["888888888","      d8P","     d8P ","    d8P  "," 8888888 ","  d8P    "," d8P     ","d8P      "],
        "8" : [" .d888b. ","d8P   Y8b","Y8b.  d8P"," \"Y8888\" "," .dP\"Yb. ","888   888","Y88b d88P"," \"Y888P\" "],
        "9" : [" .d888b. ","d8P   Y8b","88     88","Y8b.  d88"," \"Y88P888","      888","Y88b d88P"," \"Y888P\" "],
        "X" : ["Y8b   d8P"," Y8b d8P ","  Y8o8P  ","   Y8P   ","   d8b   ","  d888b  "," d8P Y8b ","d8P   Y8b"],
        "W" : ["88     88","88     88","88  o  88","88 d8b 88","88d888b88","88P   Y88","8P     Y8","P       Y"],
        "+2" : ["  db     ","  88     ","C8888D   ","  88 8888","  VP    8","     8888","     8   ","     8888"],
        "+4" : ["  db     ","  88     ","C8888D   ","  88   d ","  VP  d8 ","     d 8 ","    d8888","       8 "],
        "R9" : ["    d88P ","   d88P  ","  d88P   "," d88P    "," Y88b    ","  Y88b   ","   Y88b  ","    Y88b "],
        "R8" : ["   d88P  ","  d88P   "," d88P    ","d88P     ","Y88b     "," Y88b    ","  Y88b   ","   Y88b  "],
        "R7" : ["  d88P  Y"," d88P    ","d88P     ","88P      ","88b      ","Y88b     "," Y88b    ","  Y88b  d"],
        "R6" : [" d88P  Y8","d88P    Y","88P      ","8P       ","8b       ","88b      ","Y88b    d"," Y88b  d8"],
        "R5" : ["d88P  Y88","88P    Y8","8P      Y","P        ","b        ","8b      d","88b    d8","Y88b  d88"],
        "R4" : ["88P  Y88b","8P    Y88","P      Y8","        Y","        d","b      d8","8b    d88","88b  d88P"],
        "R3" : ["8P  Y88b ","P    Y88b","      Y88","       Y8","       d8","      d88","b    d88P","8b  d88P "],
        "R2" : ["P  Y88b  ","    Y88b ","     Y88b","      Y88","      d88","     d88P","    d88P ","b  d88P  "],
        "R1" : ["  Y88b   ","   Y88b  ","    Y88b ","     Y88b","     d88P","    d88P ","   d88P  ","  d88P   "],
        "R0" : [" Y88b    ","  Y88b   ","   Y88b  ","    Y88b ","    d88P ","   d88P  ","  d88P   "," d88P    "],
    }
        

    def __init__(self, color, value):
        '''Initializes Uno Card w/ Color and Value.'''
        self.wild = False       #Is wild card?
        self.zero = False
        self.card_id = '{}{}'.format(self.id_map[color],self.id_map[value])
        self.setColor(color)
        self.setValue(value)
        self.setPoints(value)


    #############################################

    ### -\/-  Retrieve Card Information  -\/- ### 
    
    def __repr__(self):
        return "{},{}".format(self.color, self.value)

    def getBigNum(self, reverse, reverse_seed=0):
        '''Returns list of strings to draw card's value on the pile.'''
        big_nums = []
        color_code = self.color_code
        color_code_dark = self.color_code_dark
        value = self.value
        if value == 'R':
            if not reverse:
                value += str(reverse_seed)
            else:
                value += str(9-reverse_seed)
        for mid in self.big_nums[value]:
            big_nums += ['{}| |{}'.format(color_code,color_code_dark)+mid+'{}| |\033[0m\t'.format(color_code)]
            
        return big_nums

    def getColor(self):
        '''Returns card's color.'''
        return self.color
    
    def getColorCode(self):
        '''Returns card's color code.'''
        return self.color_code

    def getValue(self):
        '''Returns card's value.'''
        return self.value
    
    def getPoints(self):
        '''Returns card's point value.'''
        return self.points
    
    def getRow(self, row_num,hide=False):
        value = self.value
        display_space = self.display_space
        if hide:
            color_code = '\033[97m'
            value = '?'
            display_space = ' '
        else:
            color_code = self.color_code
            if self.isWild():
                if row_num == 0:  
                    color_code = '\033[91m'
                elif row_num == 1:
                    color_code = '\033[93m'
                elif row_num == 2:
                    color_code = '\033[92m'
                elif row_num == 3:
                    color_code = '\033[94m'
        
        if row_num == 0:
            return      '{}\u2666--\u2666\033[0m'.format(color_code)
        elif row_num == 1:
            return      '{}|{}{}|\033[0m'.format(color_code, display_space, value)
        elif row_num == 2:
            if hide:
                return   '{}|? |\033[0m'.format(color_code)
            else:
                return   '{}|  |\033[0m'.format(color_code)
        elif row_num == 3:
            return      '{}\u2666--\u2666\033[0m'.format(color_code)

    #############################################

    ### -\/-  Set Card Information  -\/- ### 
    
    def setColor(self, color):
        '''Sets Card's color and escape code.'''
        if color == 'blue':
            self.color = 'blue'
            self.color_code = self.colors['blue']
            self.color_code_dark = self.colors['dblue']
        elif color == 'red':
            self.color = 'red'
            self.color_code = self.colors['red']
            self.color_code_dark = self.colors['dred']
        elif color == 'yellow':
            self.color = 'yellow'
            self.color_code = self.colors['yellow']
            self.color_code_dark = self.colors['dyellow']
        elif color == 'green':
            self.color = 'green'
            self.color_code = self.colors['green']
            self.color_code_dark = self.colors['dgreen']
        elif color == 'wild':         #No color modification
            self.wild = True
            self.color = 'wild'
            self.color_code_dark = self.colors['dwild']
            self.color_code = self.colors['wild']

    def setValue(self, value):
        if value in ('0','1','2','3','4','5','6','7','8','9','X','R','+2','+4','W'):
            self.value = value
            self.display_space = ' '
            if len(value) == 2:
                self.display_space = ''
            if value == '0':
                self.zero = True
                
    def setPoints(self, value):
        if value in ('0','1','2','3','4','5','6','7','8','9'):
            self.points = int(value)
        elif value in ("W", "+4"):
            self.points = 50
        else:
            self.points = 20


    #############################################

    ### -\/-  Wild Card Methods  -\/- ### 

    def changeColor(self, color):
        '''Changes Card's Color, Intended for Wild Cards.'''
        self.setColor(color)

    def isWild(self):
        '''Returns if card is a wild card.'''
        return self.wild
    
    def isZero(self):
        return self.zero
    
class Match:

    elements_init = {
        ### Names (final) ###
        'P1Name':'           ', 'P2Name':'           ', 'P3Name':'           ', 'P4Name':'           ',
        ### Card Values ### 
        'P1Cards':'           ', 'P2Cards':'           ', 'P3Cards':'           ', 'P4Cards':'           ',
        ### Turn Colors / Hand###
        'P1Turn':'', 'P2Turn':'', 'P3Turn':'', 'P4Turn':'',
        'HName':'\t\t', 'HVisual':'' ,'Hand':'',
        ### Deck ###
        'DNum':'', 'Deck':['','','','','','','','',''],
        'PostDNum':'',
        ### Pile ###
        'uHeader':'\t\t\t\t', 'uMiddle':'   ', 'uLower':'   ',
        'oHeader':'\t\t\t', 'oMiddle':['\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t'],
        ### Messages ###
        'Console':'', 'Error':''
        }
    
    speeds = {'slow':2,'normal':1,'fast':0}
        

    def __init__(self, gs):
        ### Decks ###
        self.deck = Deck(True)
        self.pile = Deck(False)
        
        ### Player Information ###
        self.players = gs.players
        self.turn_list = []
        self.hand_titles =  {'play1':'','play2':'','play3':'','play4':''}
        
        ### Carry Information ###
        self.display_effects = gs.display_effects
        self.hide_computer_hands = gs.hide_computer_hands
        self.zero_change = gs.zero_change
        self.computer_speed = self.speeds[gs.computer_speed]
        self.simulation = gs.computer_simulation

        ### Data ###
        self.hand_position = 0               # For hand displays
        self.draw_amount = 0                 # Used for force draws
        self.passes = 0                     # Keep track of consecutive passes for emergency color change
        self.pass_max = 0                    # Max passes before color change
        self.turn = ''                      # Current turn
        self.event = ''                     # Wild, Reverse, Skip, etc
        self.wild_color_change = ''           # Specifies color to change wild card to
        self.current_color = ''              # Current color
        self.current_value = ''              # Current value
        self.winner_id = ''                  # ID of Player who Won
        self.reverse = False                # Is turn order reversed
        self.turn_complete = False           # Is turn complete
        self.match_complete = False          # Is the Game over?
        self.match_abort = False             # Did the match conclude without a winner?
        self.forced_wild = False             # Force change wild

        ### Initialize Names / Cards / Deck (Assuming New Game) ###
        self.elements = dict(self.elements_init)
        
        key_string_name = 'P{}Name'
        key_string_cards = 'P{}Cards'
        
        for i in self.players:
            self.elements[key_string_name.format(i[-1])] = self.players[i].getName()+(' '*(11-len(self.players[i].getName())))
            self.elements[key_string_cards.format(i[-1])] = '  '+(' '*(3-len(str(self.players[i].getCardNum()))))+str(self.players[i].getCardNum())+' Cards'
            
        self.elements['DNum'] = len(self.deck)
        
        if len(str(len(self.deck))) < 2:
            self.elements['PostDNum'] = '\t'
            
        j = 8
        for i in range(int(math.ceil(len(self.deck)/12))):
            self.elements['Deck'][j] = '='
            j -= 1
                    
        for key in GameSettings.player_identities:
            try:
                self.buildHandString(key)
                self.turn_list += [key]
            except KeyError:
                pass
            
        self.pass_max = len(self.turn_list)
            
    def clearShell(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def begin(self):
        self.elements['Console'] = 'Beginning Game, Press Enter.'
        print(self.drawScreen())
        self.enterBreak()
        self.eventDealCards()
        self.turn = random.choice(self.turn_list)
        self.elements['Console'] = 'First turn will be {}. Press Enter.'.format(self.players[self.turn].getName())
        print(self.drawScreen(True))
        self.enterBreak()
        self.placeCard()
        self.elements['P{}Turn'.format(self.turn[-1])] = '\033[93m'
        if self.event == 'wild':
            self.eventWildCard()
        elif self.event == 'reverse':
            self.eventReverse()
            
    def end(self, gs):
        if not self.match_abort:
            points = 0
            self.elements['P{}Turn'.format(self.turn[-1])] = ''
            self.elements['Console'] = '{} Wins! Press Enter to Begin Point Tally'.format(self.players[self.winner_id].getName())
            print(self.drawScreen())
            self.enterBreak()
            
            for identity in self.turn_list:
                if identity != self.winner_id:
                    self.turn = identity
                    self.elements['HName'] = self.hand_titles[self.turn]
                    self.elements['P{}Turn'.format(self.turn[-1])] = '\033[93m'
                    while self.players[identity].getCardNum() > 0:
                        card = self.players[identity].removeCard(0)
                        points += card.getPoints()
                        self.elements['Console'] = '{} Won {} Points!'.format(self.players[self.winner_id].getName(),points)
                        
                        key_string_cards = 'P{}Cards'
                        self.elements[key_string_cards.format(identity[-1])] = '  '+(' '*(3-len(str(self.players[identity].getCardNum()))))+str(self.players[identity].getCardNum())+' Cards'
                        self.players[identity].maxScroll = math.ceil((self.players[identity].getCardNum() / 10)-1)
                        if self.hand_position > self.players[identity].maxScroll:
                            self.hand_position -= 1
                        self.buildHandVisual(identity)
                        
                        if self.display_effects and not self.simulation:
                            print(self.drawScreen())
                            time.sleep(.1)
                    self.elements['P{}Turn'.format(self.turn[-1])] = ''
                        
            self.players[self.winner_id].addPoints(points)
            self.elements['Console'] = '{} Won {} Points! Press Enter'.format(self.players[self.winner_id].getName(),points)
            print(self.drawScreen())
            self.enterBreak()
        
        gs.clearStaging()
        for identity in self.turn_list:
            self.players[identity].discardHand()
            gs.addPlayer(self.players[identity])
        return gs
        
    def adjustCardAmount(self, player_id):
        key_string_cards = 'P{}Cards'
        self.elements[key_string_cards.format(player_id[-1])] = '  '+(' '*(3-len(str(self.players[player_id].getCardNum()))))+str(self.players[player_id].getCardNum())+' Cards'
        self.players[player_id].maxScroll = math.ceil((self.players[player_id].getCardNum() / 10)-1)
        if self.hand_position > self.players[player_id].maxScroll:
            self.hand_position -= 1
        self.buildHandVisual(player_id)

    def buildHandString(self, player_id):
        player_name = self.players[player_id].getName()
        if len(player_name) < 9:
            self.hand_titles[player_id] = "{}'s Hand\t".format(self.players[player_id].getName())
        else:
            self.hand_titles[player_id] = "{}'s Hand".format(self.players[player_id].getName())

    def buildHandVisual(self, player_id):
        string = '['
        for i in range(self.players[player_id].maxScroll+1):
            if i == self.hand_position:
                string += '|'
            else:
                string += '-'
        string += ']'
        self.elements['HVisual'] = string

    def checkInput(self, player_input):
        if player_input == '':
            return {'valid':False,'entry':player_input}
        if player_input.isnumeric():
            if int(player_input)+(10*self.hand_position) < self.players[self.turn].getCardNum():
                return {'valid':True,'entry':str(int(player_input)+(10*self.hand_position)),'type':'card'}
            else:
                self.elements['Error'] = '{} is not a card.'.format(player_input)
                return {'valid':False,'entry':player_input}
        else:
            player_input = player_input.lower()[0]
            if player_input in ['<','>','u','d','p','q','s']:
                return {'valid':True,'entry':player_input}
            else:
                self.elements['Error'] = '{} is not a valid selection.'.format(player_input)
                return {'valid':False,'entry':player_input}

    def checkColorInput(self, player_input):
        if player_input == '':
            return {'valid':False,'entry':player_input}
        player_input = str(player_input).lower()[0]
        if player_input[0] == 'b':
            return {'valid':True,'entry':'blue'}
        elif player_input[0] == 'r':
            return {'valid':True,'entry':'red'}
        elif player_input[0] == 'g':
            return {'valid':True,'entry':'green'}
        elif player_input[0] == 'y':
            return {'valid':True,'entry':'yellow'}
        return {'valid':False,'entry':player_input}

    def eventDealCards(self):
        if self.display_effects and not self.simulation:
            self.elements['Console'] = 'Dealing Cards...'
        for i in ('play1','play2','play3','play4'):
            if i in self.players:
                for j in range(7):
                    j #unused
                    self.dealCard(i)
                    if self.display_effects and not self.simulation:
                        print(self.drawScreen(True))
                        time.sleep(.1)

    def eventReverse(self):
        if self.display_effects and not self.simulation:
            hide = False
            if self.players[self.turn].getType() == "Computer":
                hide = self.hide_computer_hands
            self.elements['Console'] = "Reverse Card Played! Reversing Turn Order.".format(self.players[self.turn].getName())
            print(self.drawScreen(hide))
            time.sleep(1)
            for i in range(10):
                card_big_nums = self.pile[0].getBigNum(self.reverse,i)
                self.elements['oMiddle'] = card_big_nums
                print(self.drawScreen(hide))
                if self.display_effects and not self.simulation:
                    time.sleep(.1)
        card_big_nums = self.pile[0].getBigNum(self.reverse,9)
        self.elements['oMiddle'] = card_big_nums
        self.reverse = not self.reverse
        self.event = ''
            
    def eventSkip(self):
        if self.display_effects and not self.simulation:
            hide = False
            if self.players[self.turn].getType() == "Computer":
                hide = self.hide_computer_hands
            self.elements['Console'] = "Skip Card Placed! Skipping {}'s Turn.".format(self.players[self.turn].getName())
            print(self.drawScreen(hide))
            time.sleep(1)
            for i in range(2):
                i #unused
                self.elements['P{}Turn'.format(self.turn[-1])] = '\033[91m'
                print(self.drawScreen(hide))
                time.sleep(.3)
                self.elements['P{}Turn'.format(self.turn[-1])] = ''
                print(self.drawScreen(hide))
                time.sleep(.3)
        self.turn_complete = True
        self.event = ''

    def eventWildCard(self):
        hide = False
        if not self.forced_wild:
            if self.players[self.turn].getType() == 'Human':
                self.elements['Console'] = 'Wild Card! Specifiy a Color: (B)lue, (R)ed, (G)reen, (Y)ellow'
                self.elements['Error'] = 'Specifiy A Color'
                print(self.drawScreen())
                player_input = str(input("Color Change: "))
                checked = self.checkColorInput(player_input)
                while not checked['valid']:
                    if checked['entry'] == '<':
                        self.hand_position -= 1
                        if self.hand_position == -1:
                            self.hand_position = self.players[self.turn].maxScroll
                        self.buildHandVisual(self.turn)
                    elif checked['entry'] == '>':
                        self.hand_position += 1
                        if self.hand_position > self.players[self.turn].maxScroll:
                            self.hand_position = 0
                        self.buildHandVisual(self.turn)
                    print(self.drawScreen())
                    player_input = str(input("Color Change: "))
                    checked = self.checkColorInput(player_input)
            else:
                hide = self.hide_computer_hands
                checked = self.checkColorInput(self.players[self.turn].getWildColor())
            self.wild_color_change = checked['entry']
        else:
            self.wild_color_change = self.checkColorInput(random.choice(('r','b','g','y')))['entry']
            self.forced_wild = False
        self.current_color = self.wild_color_change
        self.elements['Error'] = ""
        if self.display_effects and not self.simulation:
            self.elements['Console'] = 'Wild Card! Changing Color.'
            seed = 1
            for i in range(10):
                i #unused
                if seed > 4:
                    seed = 1
                print(self.drawScreen(hide,wild_seed=seed))
                time.sleep(.1)
                seed += 1
        self.pile[0].changeColor(self.wild_color_change)
        self.wild_color_change = ''
        card_big_nums = self.pile[0].getBigNum(self.reverse)
        self.elements['oHeader'] = '{}\u2666\u2666\u2666=========\u2666\u2666\u2666\033[0m\t'.format(self.pile[0].getColorCode())
        self.elements['oMiddle'] = card_big_nums
        self.event = ''
        
    def eventDraw(self):
        self.players[self.turn].addForceDraw(self.draw_amount)
        self.draw_amount = 0
        self.event = ''

    def dealCard(self, player_id):
        
        card = self.deck.draw()
        self.players[player_id].addCard(card)
        
        ### Adjust Hand Visual ###
        self.players[player_id].maxScroll = math.ceil((self.players[player_id].getCardNum() / 10)-1)
        self.hand_position = self.players[player_id].maxScroll
        self.buildHandVisual(player_id)
        
        ### Adjust Player Tile ###
        key_string_cards = 'P{}Cards'
        self.elements[key_string_cards.format(player_id[-1])] = '  '+(' '*(3-len(str(self.players[player_id].getCardNum()))))+str(self.players[player_id].getCardNum())+' Cards'
        
        ### Adjust Deck ###
        self.elements['DNum'] = len(self.deck)
        if len(str(len(self.deck))) < 2:
            self.elements['PostDNum'] = '\t'
        j = 8
        self.elements['Deck'] = [' ',' ',' ',' ',' ',' ',' ',' ', ' ']
        for i in range(math.ceil(len(self.deck)/12)):
            i #unused
            self.elements['Deck'][j] = '='
            j -= 1

    def placeCard(self, card=None):
        if card == None:
            ### Used At Beginning For First Card ###
            card = self.deck.draw()
            self.elements['DNum'] = len(self.deck)
            
        card_color = card.getColorCode()
        card_big_nums = card.getBigNum(self.reverse)
        
        self.current_color = card.getColor()
        self.current_value = card.getValue()
        
        self.pile.insert(card)
        self.elements['oHeader'] = '{}\u2666\u2666\u2666=========\u2666\u2666\u2666\033[0m\t'.format(card_color)
        self.elements['oMiddle'] = card_big_nums
        
        if len(self.pile) > 1:
            previous_card = self.pile[1]
            previous_card_color = previous_card.getColorCode()
            self.elements['uHeader'] = '{}      \u2666\u2666\u2666=========\u2666\u2666\u2666\033[0m\t\t'.format(previous_card_color)
            self.elements['uMiddle'] = '{}| |\033[0m'.format(previous_card_color)
            self.elements['uLower'] = '{}\u2666\u2666\u2666\033[0m'.format(previous_card_color)
            
        if self.current_color == 'wild':
            self.event = 'wild'
        
        if self.current_value == 'X':
            self.event = 'skip'
        elif self.current_value == 'R':
            if len(self.players) > 2:
                self.event = 'reverse'
            else:
                self.event = 'skip'
        elif self.current_value == '+4':
                self.draw_amount = 4
        elif self.current_value == '+2':
                self.draw_amount = 2
        self.passes = 0
                
    def extractCard(self, player_id, index):
        card = self.players[player_id].removeCard(index)
        if self.players[player_id].getCardNum() == 0:
            self.match_complete = True
            self.winner_id = self.turn
        self.adjustCardAmount(player_id)
        return card
    
    def enterBreak(self):
        if not self.simulation:
            str(input())
        return
            
    def nextTurn(self):
        self.turn_complete = False
        self.hand_position = 0
        turn_type = self.players[self.turn].getType()
        self.players[self.turn].beginTurn()
        ### Prepare Hand Visuals ###
        
        self.elements['HName'] = self.hand_titles[self.turn]
        self.buildHandVisual(self.turn)
        
        if self.event == 'skip':
            self.eventSkip()
        elif self.draw_amount > 0:
            self.eventDraw()
        
        while not self.turn_complete:
            if turn_type == 'Human':
                self.players[self.turn].getLegalCards(self.current_color, self.current_value, self.zero_change)
                if len(self.deck) > 0:
                    self.elements['Console'] = 'Select a card, (D)raw, or (P)ause.'
                else:
                    self.players[self.turn].removeForceDraw()
                    self.elements['Console'] = 'Select a card, (D)raw, (P)ause, or Pas(s).'
                if self.players[self.turn].getForceDraws() > 0:
                    self.elements['Error'] = 'Draw Card Played! Draw {} cards.'.format(self.players[self.turn].getForceDraws())
                print(self.drawScreen())
                player_input = str(input("\033[97mSelection: \033[92m"))
                checked = self.checkInput(player_input)
                while not checked['valid']:
                    print(self.drawScreen())
                    player_input = str(input("\033[97mSelection: \033[92m"))
                    checked = self.checkInput(player_input)
    
                player_input = checked['entry']
                
                if player_input == '<':
                    self.hand_position -= 1
                    if self.hand_position == -1:
                        self.hand_position = self.players[self.turn].maxScroll
                    self.buildHandVisual(self.turn)
                elif player_input == '>':
                    self.hand_position += 1
                    if self.hand_position > self.players[self.turn].maxScroll:
                        self.hand_position = 0
                    self.buildHandVisual(self.turn)
                elif player_input == 'd':
                    if len(self.deck) > 0:
                        self.elements['Error'] = ''
                        self.dealCard(self.turn)
                    else:
                        self.elements['Error'] = "Cannot Draw. Deck is Empty"
                elif player_input == 'p':
                    pause_output = self.pauseScreen()
                    if pause_output == 'quit':
                        self.match_complete = True
                        self.turn_complete = True
                        self.winner_id = 'play1'
                        self.match_abort = True
                elif player_input == 's':
                    if len(self.deck) > 0:
                        self.elements['Error'] = "Cannot pass until Deck is empty."
                    elif len(self.players[self.turn].getAllValidCards()) > 0:
                        self.elements['Error'] = "Cannot pass while having playable cards."
                    else:
                        self.turn_complete = True
                        self.passes += 1
                        if self.passes == self.pass_max:
                            self.forced_wild = True
                            self.event = 'wild'
                            self.passes = 0
                elif player_input.isnumeric():
                    if self.players[self.turn].getForceDraws() == 0:
                        card_check = self.players[self.turn].checkCard(player_input)
                        if card_check in self.players[self.turn].getAllValidCards():
                            card = self.extractCard(self.turn, player_input)
                            self.placeCard(card)
                            self.elements['Error'] = ""
                            self.turn_complete = True
                        else:
                            self.elements['Error'] = "Card Doesn't Match The Color {} or Value {}!".format(self.current_color, self.current_value)
                    else:
                        pass
                    
            elif turn_type == 'Computer':
                self.elements['Console'] = '{}\'s Turn'.format(self.players[self.turn].getName())
                print(self.drawScreen(self.hide_computer_hands))
                if not self.simulation:
                    time.sleep(self.computer_speed)
                #str(input())
                while (True):
                    if self.display_effects and not self.simulation:
                        time.sleep(.2)
                    if self.players[self.turn].getForceDraws() > 0 and len(self.deck) > 0:
                        card_index = 'd'
                    else:
                        card_index = self.players[self.turn].think(self)
                    if card_index.isnumeric():
                        card = self.extractCard(self.turn, int(card_index))
                        if card.getColor() != self.current_color:
                            self.resetDrawBool()
                        self.placeCard(card)
                        self.turn_complete = True
                        break
                    else:
                        if card_index == 'd':
                            if len(self.deck) > 0:
                                self.dealCard(self.turn)
                                print(self.drawScreen(self.hide_computer_hands))
                            else:
                                self.turn_complete = True
                                self.players[self.turn].removeForceDraw()
                                self.passes += 1
                                if self.passes == self.pass_max:
                                    self.forced_wild = True
                                    self.event = 'wild'
                                    self.passes = 0
                                break
                
            ### DECODE INPUT ###
                
        if self.event == 'reverse':
            self.eventReverse()
        elif self.event == 'wild':
            self.eventWildCard()
            
        # Clear Current Turn
        self.elements['P{}Turn'.format(self.turn[-1])] = ''
        # Prepare Next Turn
        self.turn = self.getNextTurn()
        self.elements['P{}Turn'.format(self.turn[-1])] = '\033[93m'

    def drawScreen(self, hide=False, wild_seed=0):
        if self.simulation:
            return ''
        color_combos = {
            1 : ['\033[91m','\033[93m','\033[92m','\033[94m'],
            2 : ['\033[94m','\033[91m','\033[93m','\033[92m'],
            3 : ['\033[92m','\033[94m','\033[91m','\033[93m'],
            4 : ['\033[93m','\033[92m','\033[94m','\033[91m'] }
        current_turn = self.turn
        if current_turn == '':
            current_turn = self.turn_list[-1]
            hide = True
        if wild_seed != 0:
            color_mod = color_combos[wild_seed]
        else:
            color_mod = ['','','','']

        self.clearShell()
        screenout = ''
        screenout += '\t\t\033[94m      || ||\033[92m ||\ ||  \033[91m// \\\\\n\033[0m'
        screenout += '\t\t\033[94m      || ||\033[92m ||\\\|| \033[91m((   ))\n\033[0m'
        screenout += '\t\t\033[94m      \\\ //\033[92m || \|| \033[91m \\\ //\n\033[0m'
        screenout += '\033[97m===============================================================\n'
        screenout += '\033[93m{}\033[0m\n'.format(self.elements['Console'])
        screenout += '\033[97m===============================================================\n'
        screenout += '\t\t\t\t\t\t'     +        ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P1Turn'])
        screenout += '\033[97mDeck:\t\t'        +       '{}'.format(self.elements['uHeader'])       +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P1Turn'],self.elements['P1Name'])
        screenout += '\033[97m{} Cards'.format(self.elements['DNum'])       +       '{}'.format(self.elements['PostDNum'])+'\t'     +       '{}'.format(self.elements['uHeader'])       +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P1Turn'],self.elements['P1Cards'])
        screenout += '\t\t      '       +      '{}'.format(self.elements['uMiddle'])        +       '\033[97m{}{}'.format(color_mod[0],self.elements['oHeader'])     +      ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P1Turn'])
        screenout += '\033[97m  _+_ \t\t      '     +       '{}'.format(self.elements['uMiddle'])                                                                                                   +       '\033[97m{}{}'.format(color_mod[1],self.elements['oHeader'])         +       ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P2Turn'])                                                                                  
        screenout += '\033[97m | '      +       '\033[92m{}\033[0m'.format(self.elements['Deck'][0])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uMiddle'])       +       '\033[97m{}{}'.format(color_mod[2],self.elements['oMiddle'][0])      +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P2Turn'],self.elements['P2Name'])
        screenout += '\033[97m | '      +       '\033[92m{}\033[0m'.format(self.elements['Deck'][1])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uMiddle'])       +       '\033[97m{}{}'.format(color_mod[3],self.elements['oMiddle'][1])      +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P2Turn'],self.elements['P2Cards'])
        screenout += '\033[97m | '      +       '\033[92m{}\033[0m'.format(self.elements['Deck'][2])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uMiddle'])       +       '\033[97m{}{}'.format(color_mod[0],self.elements['oMiddle'][2])      +       ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P2Turn'])
        screenout += '\033[97m | '      +       '\033[93m{}\033[0m'.format(self.elements['Deck'][3])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uMiddle'])       +       '\033[97m{}{}'.format(color_mod[1],self.elements['oMiddle'][3])      +       ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P3Turn'])
        screenout += '\033[97m | '      +       '\033[93m{}\033[0m'.format(self.elements['Deck'][4])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uMiddle'])       +       '\033[97m{}{}'.format(color_mod[2],self.elements['oMiddle'][4])      +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P3Turn'],self.elements['P3Name'])
        screenout += '\033[97m | '      +       '\033[93m{}\033[0m'.format(self.elements['Deck'][5])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uMiddle'])       +       '\033[97m{}{}'.format(color_mod[3],self.elements['oMiddle'][5])      +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P3Turn'],self.elements['P3Cards'])
        screenout += '\033[97m | '      +       '\033[91m{}\033[0m'.format(self.elements['Deck'][6])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uLower'])        +       '\033[97m{}{}'.format(color_mod[0],self.elements['oMiddle'][6])      +       ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P3Turn'])
        screenout += '\033[97m | '      +       '\033[91m{}\033[0m'.format(self.elements['Deck'][7])        +       '\033[97m |\t\t      '      +       '{}'.format(self.elements['uLower'])        +       '\033[97m{}{}'.format(color_mod[1],self.elements['oMiddle'][7])      +       ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P4Turn'])
        screenout += '\033[97m |_'      +     '\033[91m{}\033[0m'.format(self.elements['Deck'][8])          +        '\033[97m_|\t\t         '                                                      +      '\033[97m{}{}'.format(color_mod[2],self.elements['oHeader'])          +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P4Turn'],self.elements['P4Name'])
        screenout += '\033[97m\t\t         '    +                                                                                                                                                                   '\033[97m{}{}'.format(color_mod[3],self.elements['oHeader'])         +       ' \033[97m{}|{}|\033[0m\n'.format(self.elements['P4Turn'],self.elements['P4Cards'])
        screenout += '\t\t\t\t\t\t'     +       ' \033[97m{}\u2666-----------\u2666\033[0m\n'.format(self.elements['P4Turn'])
        screenout += "\033[97m{}".format(self.elements['HName'])        +       "\t\t\t\t {}\n".format(self.elements['HVisual'])
        screenout += '\033[97m===============================================================\n'
        screenout += self.players[current_turn].getHand(self.hand_position,hide)
        screenout += '\033[91m{}\033[0m'.format(self.elements['Error'])
        return screenout
    
    def pauseScreen(self):
        while True:
            self.clearShell()
            print('\n\t\t\tPause')
            print('\n\t\t1. Resume')
            print('\t\t2. Quit')
            
            selection = str(input('\nSelection: ')).upper()
            while selection not in ['1', '2']:
                print('\nSelection Invalid')
                selection = str(input('\nSelection: ')).upper()
                
            if selection == '1' or "":
                return ""
                
            elif selection == '2':
                return "quit"
                
    
    def isComplete(self):
        return self.match_complete
    
    def next(self):
        self.turn = self.getNextTurn()
    
    def getNextTurn(self, force_reverse=False):
        if force_reverse:
            reverse = not self.reverse
        else:
            reverse = self.reverse
        current_index = self.turn_list.index(self.turn)
        if not reverse:
            if (current_index + 1) == len(self.turn_list):
                return self.turn_list[0]
            else:
                return self.turn_list[current_index+1]
        else:
            if current_index == 0:
                return self.turn_list[len(self.turn_list) - 1]
            else:
                return self.turn_list[current_index-1]
            
    def getPlayer(self, player_id):
        return self.players[player_id]
    
    def resetDrawBool(self):
        for identity in self.players:
            self.players[identity].drew = False

def Uno(debugging=False):

    ###MENUS###
    
    def clearShell():
        os.system('cls' if os.name == 'nt' else 'clear')

    def mainMenu():
        sys.stdout.write("\x1b[8;32;63t")
        sys.stdout.flush()
        gs = GameSettings()
        
        while True:
 
            print(drawMainMenu(gs))
            
            selection = str(input('\033[97mSelection: \033[92m'))
            while selection not in ['1', '2', '3', '4', '5']:
                gs.main_menu_error = "Invalid Selection"
                print(drawMainMenu(gs))
                selection = str(input('\033[97mSelection: \033[92m'))
                
            if selection == '1':
                if gs.canBegin():
                    gs.main_menu_error = ""
                    gs.finalizePlayers()
                    gs = playMatch(gs)
                else:
                    gs.main_menu_error = "Two Players Required to Begin"

            elif selection == '2':
                if gs.canAddPlayer():
                    gs.main_menu_error = ""
                    gs = addPlayer(gs)
                else:
                    gs.main_menu_error = "Max Number of Players Reached"
                    
            elif selection == '3':
                if gs.canAddPlayer():
                    gs.main_menu_error = ""
                    gs = addComputer(gs)
                else:
                    gs.main_menu_error = "Max Number of Players Reached"

            elif selection == '4':
                if gs.canRemovePlayer():
                    gs.main_menu_error = ""
                    gs = removePlayer(gs)
                else:
                    gs.main_menu_error = "No Players to Remove"

            elif selection == '5':
                gs.main_menu_error = ""
                gs = settingsMenu(gs)

            else:
                raise BadInputError('Data Provided Has No Function')
            
    def playMatch(gs):
        for i in range(1):
            i
            m = Match(gs)
            m.begin()
            while (not m.isComplete()):
                m.nextTurn()
            gs = m.end(gs)
        return gs
            
    def addPlayer(gs):
        colors = ['\033[91m','\033[94m', '\033[92m', '\033[93m']
        name_okay = False
        player_num = gs.getPlayerNum() + 1
        color_index = player_num - 1
        message = "\033[97mPlease Enter Player {}'s Name: {}".format(player_num, colors[color_index])
        
        while not name_okay:
            print(drawMainMenu(gs))
            name = str(input(message)).title()
            if len(name) > 11:
                gs.main_menu_error = "Name Must Be 11 Characters or Less!"
            elif len(name) == 0:
                gs.main_menu_error = ""
                return gs
            else:
                name_okay = True
                for player in gs.player_staging:
                    if player.getName() == name:
                        name_okay = False
                if name_okay == False or name in GameSettings.computer_names:
                    gs.main_menu_error = "Name Cannot Match Another Player's Name!"
                        
        p = Player(name)
        gs.addPlayer(p)
        gs.main_menu_error = ""
        
        return gs
    
    def addComputer(gs):
        name = gs.getComputerName()
        c = ComputerPlayer(name)
        gs.addPlayer(c)
        
        return gs
    
    def removePlayer(gs):
        sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=32, cols=63))
        sys.stdout.flush()
        clearShell()
        
        complete = False
        player_num = gs.getPlayerNum()
        message = "\033[97mPlease Enter Player Number to Remove: \033[91m".format(player_num)
        
        while (not complete):
            print(drawMainMenu(gs))
            number = str(input(message)) 
            if len(number) == 0:
                gs.main_menu_error = ""
                return gs
            try:
                number = int(number)
                if 0 < number <= player_num:
                    complete = True
                else:
                    gs.main_menu_error = "Invalid Player Number!"
            except:
                gs.main_menu_error = "Please Enter the Player Number, not Name!"
        
        gs.main_menu_error = ""
        gs.removePlayer(number)
        return gs
    
    def settingsMenu(gs):
        while True:
            sys.stdout.write("\x1b[8;32;63t")
            sys.stdout.flush()
            clearShell()
            print('\n\t\tSettings')
            print('\n\t1. Draw Effects\t\t\t{}'.format(gs.display_effects))
            print('\t2. Hide Computer Hands\t\t{}'.format(gs.hide_computer_hands))
            print('\t3. Computer Speed\t\t{}'.format(gs.computer_speed.title()))
            #print('\t4. Zero Card Changes Color\t{}'.format(gs.zeroChange))
            #print('\t5. Run Simulations\t\t{}'.format(gs.computerSimulation))
            print('\n\tA. Exit')
            
            selection = str(input('\nSelection: ')).upper()
            while selection not in ('1', '2', '3', '4', '5', 'A', ''):
                print('\nSelection Invalid')
                selection = str(input('\nSelection: ')).upper()
                
            if selection == '1':
                gs.display_effects = not gs.display_effects
                
            elif selection == '2':
                gs.hide_computer_hands = not gs.hide_computer_hands
                
            elif selection == '3':
                gs.changeComputerSpeed()
                '''
            elif selection == '4':
                gs.zeroChange = not gs.zeroChange
                
            elif selection == '5':
                gs.computerSimulation = not gs.computerSimulation
                '''
            elif selection == 'A' or selection == '' or selection in ('4','5'):
                return gs
    
    def drawMainMenu(gs):
        clearShell()
        gs.compileMainMenuElements()
        menu_elements = gs.getMainMenuElements()
        screenout = ''
        screenout += '\t\t\033[94m      || ||\033[92m ||\ ||  \033[91m// \\\\\n\033[0m'
        screenout += '\t\t\033[94m      || ||\033[92m ||\\\|| \033[91m((   ))\n\033[0m'
        screenout += '\t\t\033[94m      \\\ //\033[92m || \|| \033[91m \\\ //\n\033[0m'
        screenout += '\033[97m===============================================================\033[0m\n'
        screenout += "{}1-----------------------------1\033[0m {}2-----------------------------2\033[0m\n".format(menu_elements['play1box'],menu_elements['play2box'])
        screenout += "{}|{}|\033[0m {}|{}|\033[0m\n".format(menu_elements['play1box'],menu_elements['play1row1'],menu_elements['play2box'],menu_elements['play2row1'])
        screenout += "{}|{}|\033[0m {}|{}|\033[0m\n".format(menu_elements['play1box'],menu_elements['play1row2'],menu_elements['play2box'],menu_elements['play2row2'])
        screenout += "{}1-----------------------------1\033[0m {}2-----------------------------2\033[0m\n".format(menu_elements['play1box'],menu_elements['play2box'])
        screenout += "{}3-----------------------------3\033[0m {}4-----------------------------4\033[0m\n".format(menu_elements['play3box'],menu_elements['play4box'])
        screenout += "{}|{}|\033[0m {}|{}|\033[0m\n".format(menu_elements['play3box'],menu_elements['play3row1'],menu_elements['play4box'],menu_elements['play4row1'])
        screenout += "{}|{}|\033[0m {}|{}|\033[0m\n".format(menu_elements['play3box'],menu_elements['play3row2'],menu_elements['play4box'],menu_elements['play4row2'])
        screenout += "{}3-----------------------------3\033[0m {}4-----------------------------4\033[0m\n".format(menu_elements['play3box'],menu_elements['play4box'])
        screenout += "\033[97m===============================================================\033[0m\n"
        screenout += "  {}\u2666---------------------------\u2666\033[0m \u2666===========================\u2666\n".format(menu_elements['beginBox'])
        screenout += "  {}|1.       Begin Match       |\033[0m |        High Scores        |\n".format(menu_elements['beginBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m \u2666---------------------------\u2666\n".format(menu_elements['beginBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m |                           |\n".format(menu_elements['addBox'])
        screenout += "  {}|2.       Add Player        |\033[0m |                           |\n".format(menu_elements['addBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m |                           |\n".format(menu_elements['addBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m |                           |\n".format(menu_elements['addBox'])
        screenout += "  {}|3.      Add Computer       |\033[0m |                           |\n".format(menu_elements['addBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m |                           |\n".format(menu_elements['addBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m |                           |\n".format(menu_elements['removeBox'])
        screenout += "  {}|4.      Remove Player      |\033[0m |                           |\n".format(menu_elements['removeBox'])
        screenout += "  {}\u2666---------------------------\u2666\033[0m |                           |\n".format(menu_elements['removeBox'])
        screenout += "  \033[97m\u2666---------------------------\u2666\033[0m |                           |\n"
        screenout += "  \033[97m|5.        Settings         |\033[0m |                           |\n"
        screenout += "  \033[97m\u2666---------------------------\u2666\033[0m \u2666===========================\u2666\n"
        screenout += "\033[97m===============================================================\033[0m\n"
        screenout += '\033[91m{}\033[0m'.format(gs.main_menu_error)
        return screenout
    
    mainMenu()
            
if __name__ == "__main__":
    Uno()
        
