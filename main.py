# TO DO (QOL):
    # Turn dividers
    # Show hand after drawing
    # Auto-sort player's hand
    # Colour code cards
    # Allow QKA runs

import random
from copy import copy


SUITS = ["H", "C", "S", "D"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
HAND_SIZES = {2:10, 3:7, 4:7, 5:6, 6:6}


class Card():
    def __init__(self, rank : str, suit : str):
        if suit not in SUITS:
            raise ValueError("Invalid suit given to card.")
        if rank not in RANKS:
            raise ValueError("Invalid rank given to card.")
        self.suit = suit
        self.rank = rank
        self.code = self.rank + self.suit

    def __repr__(self):
        return self.code


def run(cds:list):
    if len(cds) < 3:
        return None
    
    cards = copy(cds)
    
    # Find card of minimal rank.
    min_card = cards[0]
    for card in cards:
        if RANKS.index(card.rank) < RANKS.index(min_card.rank):
            min_card = card
    
    # Start off the run with the minimal card.
    suit = min_card.suit
    run = [min_card]
    cards.remove(min_card)
    c = RANKS.index(min_card.rank)
    i = 1
    # Iterate over next ranks until K is reached or a suit-matching card is not found.
    while i < 13:
        next_found = False
        for card in cards:
            if card.suit == suit and RANKS.index(card.rank) == c + i:
                run.append(card)
                cards.remove(card)
                next_found = True
                i += 1
        if not next_found:
            break
    # If all cards were used in forming the run, the given set was a valid run. Otherwise it was not.
    if cards == []:
        return run
    else:
        return None


def lot(cds: list):
    if len(cds) < 3:
        return None
    rank = cds[0].rank
    for card in cds:
        if card.rank != rank:
            return None
    return cds


class Meld():
    def __init__(self):
        pass

    def __repr__(self):
        out = "["
        for card in self.cards:
            out += str(card)
            out += " "
        out = out.removesuffix(" ")
        out += "]"
        return out


class Lot(Meld):
    def __init__(self, cards):
        if lot(cards) == None:
            raise ValueError("Attempted to create a Lot from an invalid set of cards.")
        self.cards = cards
        self.is_run = False
        self.is_lot = True
    
    def set_next(self, pool:list):
        out = []
        for card in pool:
            new = self.cards + [card]
            if lot(new) != None:
                out += [card]
        self.next = out


class Run(Meld):
    def __init__(self, cards):
        if run(cards) == None:
            raise ValueError("Attempted to create a Run from an invalid set of cards.")
        self.cards = run(cards)
        self.is_run = True
        self.is_lot = False
        
    def set_next(self, pool:list):
        out = []
        for card in pool:
            new = self.cards + [card]
            if run(new) != None:
                out += [card]
        self.next = out
    
        


# Class Meld
# Meld object stores:
    # Cards in meld
    # Is set/run
    # Viable additions

# Cards store scoring player

# Playing melds
    # table calls on player to play melds
    # player returns a list of meld objects with setup complete



kh = Card("K", "H")
kd = Card("K", "D")
ks = Card("K", "S")
qs = Card("Q", "S")
js = Card("J", "S")
jd = Card("J", "D")
ts = Card("T", "S")
eights = Card("8", "S")

mylot = Lot([kh, kd, ks])
print(mylot)



# Returns a full unshuffled deck
def deck():
    out = []
    for suit in SUITS:
        for rank in RANKS:
            out.append(Card(rank, suit))
    return out

mymeld = Lot([kh, kd, ks])

class Table():
    def __init__(self, players : list, hand_size : int = 0):
        self.players = players
        if hand_size == 0:
            try:
                self.hand_size = HAND_SIZES[len(players)]
            except: 
                raise ValueError("Hand size must be specified for this number of players.")
        self.stock = []
        self.discard = []
        self.melds = [mymeld, mymeld, mymeld, mymeld]

    # Shows all information of table, including stock and all players' hands
    def show_all(self):
        print("Stock:")
        print(self.stock)

        print("\nDiscard:")
        print(self.discard)

        for p in self.players:
            print("\n" + p.name + "'s hand:")
            print(p.hand)

    def show_table(self):
        print("MELDS".center(90, ' '))
        melds_text = []
        for i, meld in enumerate(self.melds):
            if i % 3 == 0:
                melds_text += ['']
            melds_text[i//3] += " " + str(meld) + " "
        for meld_text in melds_text:
            print(meld_text.center(90, " "))
            
        print("")
        
        print(("STOCK   [??]      DISCARD [" + str(self.discard[-1]) + "]").center(90, ' '))
        print("")


    def show_hand(self, player):
        print((player.name + "'s Hand").center(90, " "))
        hand_text = ""
        for card in player.hand:
            hand_text += str(card) + " "
        hand_text = hand_text.removesuffix(" ")
        print(hand_text.center(90, " "))

    def play(self):
        # Set up stock, players' hands, discard pile
        self.stock = deck()
        random.shuffle(self.stock)
        for p in self.players:
            hand = []
            for i in range(self.hand_size):
                hand.append(self.stock.pop())
            p.hand = hand
        self.discard = [self.stock.pop()]

        # Start game loop
        playing = True
        player_index = -1 # -1 so that player 0 starts
        while playing:

            # Go to next player
            player_index = (player_index + 1) % len(self.players)
            cur_player = self.players[player_index]
            
            # Show state of the game
            print((" "  + cur_player.name + "'s turn ").center(90, '-'))
            print("")
            self.show_table()
            if cur_player.show_hand:
                self.show_hand(cur_player)
            print("")

            # First, player draws. Method player.draw() returns true if he wants to draw from the discard pile. Otherwise he draws from the stock.
            if cur_player.draw():
                cur_player.hand.append(self.discard.pop())
            else:
                cur_player.hand.append(self.stock.pop())
                
            if cur_player.show_hand:
                self.show_hand(cur_player)
                    
            # Then, player forms melds.
            self.melds += cur_player.meld()
            
            if cur_player.show_hand:
                self.show_hand(cur_player)
            
            # Finally, player chooses a card to place on the discard pile.
            self.discard.append(cur_player.discard())


      
# Base class for CPU + human players
class Player():
    def __init__(self, name : str, hand : list = [], melds : list = [], show_hand = False):
        self.hand = hand
        self.melds = melds
        self.name = name
        self.show_hand = show_hand
    
    # Should probably put in errors for these functions? This is just a base class so these methods should never be called.
    def draw(self):
        print("Drawing")
        
    def sort_hand(self):
        new_hand = []
        for suit in SUITS:
            for rank in RANKS:
                for card in self.hand:
                    if card.code == rank + suit:
                        new_hand.append(card)
        self.hand = new_hand
                    
    
    def discard(self):
        print("Discarding")



class Human(Player):
    def __init__(self, name : str, hand : list = [], melds : list = []):
        super().__init__(name, hand, melds)
        self.show_hand = True

    # Choose to draw from either stock or discard. True = discard, False = stock.
    def draw(self):
        ui = input("Draw from discard or stock?")
        while ui.lower() not in ["d", "s", "discard", "stock"]:
            print("Invalid input.")
            ui = input("Draw from discard or stock?")
        if ui.lower() in ["discard", "d"]:
            return True
        return False

    # Select a card from hand. Remove it from hand. Return it, so that table can add it to discard.
    def discard(self):
        print("Name a card to discard from your hand.")
        ui = input()
        while True:
            rank = ui[0].upper()
            suit = ui[1].upper()
            for card in self.hand:
                if card.suit == suit and card.rank == rank:
                    self.hand.remove(card)
                    return card
            ui = input("Couldn't find that card. Try again. \n")
    
    def meld(self):
        melds = []
        ui = " "
        while ui != '':
            ui = input("Enter cards from your hand to form a meld, e.g. 'KH KC KS'. Or, enter '' to end.")
            
            # Check that ui codes >2 cards
            ui_valid = True
            codes = ui.split(" ")
            for code in codes:
                if len(code) != 2 or code[0] not in RANKS or code[1] not in SUITS or len(codes) < 3:
                    ui_valid = False
                    break
            if not ui_valid:
                print("Invalid input.")
                continue
            
            # Check that cards exist in player hand, translate from codes to cards.
            cards = []
            for code in codes:
                card_found = False
                for card in self.hand:
                    if card.code == code:
                        card_found = True
                        cards.append(card)
                        break
                if not card_found:
                    ui_valid = False
            if not ui_valid:
                print("Entered a card not found in hand.")
                continue
            
            if lot(cards):
                melds.append(Lot(cards))
                print("Lot added.")
                for card in cards:
                    self.hand.remove(card)
            elif run(cards):
                melds.append(Run(cards))
                print("Run added.")
                for card in cards:
                    self.hand.remove(card)
            else:
                print("Set did not form run or lot so was ignored.")
        
        return melds
            



player1 = Human("Player 1")
player2 = Human("Player 2")
my_table = Table([player1, player2])

my_table.play()


# while playing
#   for player
#     take player's move

# moves:
#  draw from discard or stock
#  play melds, lay off
#  discard 1 card
# Represent move as tuple (draw, [melds], discard)
