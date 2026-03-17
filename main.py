import random
from copy import copy

print("Hello world!")

SUITS = ["H", "C", "S", "D"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
VALUE = {"A" : 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 10, "Q": 10, "K": 10}
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
        self.scorer = None

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

    # Allow for A23 runs.
    if min_card.rank == "2":
        if cards != [] and cards[0].code == "A" + suit:
            run.insert(0, cards.pop(0))

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
    



# Returns a full unshuffled deck
def deck():
    out = []
    for suit in SUITS:
        for rank in RANKS:
            out.append(Card(rank, suit))
    return out


class Table():
    def __init__(self, players : list, hand_size : int = 0):
        self.players = players
        for player in players:
            player.table = self
        self.hand_size = hand_size
        if hand_size == 0:
            try:
                self.hand_size = HAND_SIZES[len(players)]
            except: 
                raise ValueError("Hand size must be specified for this number of players.")
        self.stock = []
        self.discard = []
        self.melds = []

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
        self.show_melds()
            
        print("")
        
        print(("STOCK   [??]      DISCARD [" + str(self.discard[-1]) + "]").center(90, ' '))
        print("")


    def show_melds(self):
        print("MELDS".center(90, ' '))
        melds_text = []
        for i, meld in enumerate(self.melds):
            if i % 3 == 0:
                melds_text += ['']
            melds_text[i//3] += " " + str(meld) + " "
        for meld_text in melds_text:
            print(meld_text.center(90, " "))


    def new_turn_output(self, cur_player):
        print((" "  + cur_player.name + "'s turn ").center(90, '-'))
        print("")
        self.show_table()
        print("")

    def game_end_output(self):
        print(" GAME END ".center(90, "-"))
        print("")
        self.show_melds()
        print("")

    def final_score_output(self, winner):
        print((winner.name + " WINS").center(90, ' '))
        print("")
        for player in self.players:
            print(player.name + ": " + str(player.score))

    def play(self):

        # Set up stock, players' hands, discard pile
        self.stock = deck()
        random.shuffle(self.stock)

        # Deal each player's hand from the stock
        for p in self.players: 
            hand = []
            for i in range(self.hand_size):
                deal = self.stock.pop()
                deal.scorer = p
                hand.append(deal)
            p.hand = hand
            p.score = 0
            p.out = False
            
        

        # Start the discard pile with one card from the stock
        self.discard = [self.stock.pop()]

        # Start game loop
        player_index = -1 # -1 so that player 0 starts
        while True:
            self.show_all()

            if self.stock == []:
                break 
            
            # Go to next player
            player_index = (player_index + 1) % len(self.players)
            cur_player = self.players[player_index]
            cur_player.sort_hand()

            if cur_player.out:
                break


            # Show state of the game
            self.new_turn_output(cur_player)


            # self.show_all()
            # First, player draws. Method player.draw() returns true if he wants to draw from the discard pile. Otherwise he draws from the stock.
            if cur_player.draw():
                deal = self.discard.pop()
            else:
                deal = self.stock.pop()


            deal.scorer = cur_player
            cur_player.hand += [deal]
                
            # Then, player forms melds.
            self.melds += cur_player.meld()

            # Next lay off.
            cur_player.lay_off(self.melds)
            
            # Discard sequence
            if cur_player.hand == []: # Go out if hand is empty before discarding
                cur_player.out = True
            else:
                self.discard.append(cur_player.discard()) # Discard if hand is not empty
            if cur_player.hand == []: # Also go out if hand is empty after discarding
                cur_player.out = True
    
        self.game_end_output()
        # Score cards from melds
        for meld in self.melds:
            for card in meld.cards:
                card.scorer.score += VALUE[card.rank]

        # Negate score of cards in players' hands
        for player in self.players:
            for card in player.hand:
                player.score -= VALUE[card.rank]

        # Find the maximum score and the winner
        max_score = self.players[0].score
        winner = self.players[0]
        for player in self.players:
            if player.score > max_score:
                max_score = player.score
                winner = player
        
        self.final_score_output(winner)
        
        return winner

        



      
# Base class for CPU + human players
class Player():
    def __init__(self, name : str, hand : list = [], melds : list = [], open_handed = False):
        self.out = False
        self.hand = hand
        self.name = name
        self.table = None
        self.score = 0
    

    def show_hand(self):
        print((self.name + "'s Hand").center(90, " "))
        hand_text = ""
        for card in self.hand:
            hand_text += str(card) + " "
        hand_text = hand_text.removesuffix(" ")
        print(hand_text.center(90, " "))


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

        
    def lay_off(self, melds):
        pass
    
    
    def show_hand(self):
        print((self.name + "'s Hand").center(90, " "))
        hand_text = ""
        for card in self.hand:
            hand_text += str(card) + " "
        hand_text = hand_text.removesuffix(" ")
        print(hand_text.center(90, " "))
    
    
    def discard(self):
        print("Discarding")


class Bot(Player):
    def __init__(self, name : str, hand : list = []):
        super().__init__(name, hand)
    
    def draw(self):
        # We come up with a list of all cards that could be in the stock.
        # Other player's cards are unknown but we know everything in the discard pile.
        # This assumes we are playing with one deck!
        stock = [c.code for c in deck()]
        for c in self.table.discard:
            stock.remove(c.code)
        for meld in self.table.melds:
            for c in meld.cards:
                stock.remove(c.code)
        for c in self.hand:
            stock.remove(c.code)
        
        # We take EV of stock.
        values = {}
        exp_value = 0
        for c in stock:
            exp_value += value(Card(c[0], c[1]), self.hand, self.table.melds)
        exp_value = exp_value/len(stock)

        if value(self.table.discard[-1], self.hand, self.table.melds) >= exp_value:
            print(self.name + " draws from discard.")
            return True

        print(self.name + " draws from stock.")
        return False
    

    def meld(self):
        melds = []
        while True:
            max_meld = []
            for card in self.hand:
                h = copy(self.hand)
                h.remove(card)
                cur_meld = meld_with(card, h)
                if len(cur_meld) > len(max_meld):
                    max_meld = cur_meld
            if lot(max_meld):
                max_meld = Lot(max_meld)
            elif run(max_meld):
                max_meld = Run(max_meld)
            else:
                break
            melds.append(max_meld)
            for card in max_meld.cards:
                self.hand.remove(card)
                print(card.scorer)

        return(melds)

    def lay_off(self, melds):
        while True:
            laid = False
            for meld in melds:
                for card in self.hand:
                    if lot(meld.cards + [card]) or run(meld.cards + [card]):
                        meld.cards += [card]
                        self.hand.remove(card)
            if not laid:
                break
        
    
    def discard(self):
        min_value = 2
        min_card = None
        for card in self.hand:
            h = copy(self.hand)
            h.remove(card)
            c_value = value(card, self.hand, self.table.melds)
            if c_value < min_value:
                min_value = c_value
                min_card = card 
        self.hand.remove(min_card)
        return(min_card)


def value(card, hand, melds):
    # First, if a card can immediately be laid off, its value is 1.
    for meld in melds:
        if lot(meld.cards + [card]) or run(meld.cards + [card]):
            return 1

    # Next, if a card can immediately be melded, its value is 1.
    if len(meld_with(card, hand)) >= 3:
        return 1
    
    # Finally, if a card pairs with another card, its value is 0.5.
    if len(meld_with(card, hand)) == 2:
        return 0.5 
    
    return 0


# Builds the biggest run/lot that we can find which contains the specified card, and cards in hand.
# Returns the biggest run/lot, prioritising runs.
# Doesn't work properly for runs when card is A atm.
def meld_with(card, hand): 
    
    # We use card codes because they're easier to work with.
    codes = [c.code for c in hand]
    lot_codes = [card.code]

    # Built the biggest lot we can.
    for suit in SUITS:
        if card.rank + suit in codes:
            lot_codes += [card.rank + suit]

    # Set up for finding a run.
    run_codes = [card.code]
    suit = card.suit
    index = RANKS.index(card.rank)
    c = index
    # Tick down from the specified card, adding in whatever is found.
    while c >= 0: # -1 possibility allows for A23 runs
        if RANKS[c-1] + suit in codes:
            run_codes += [RANKS[c-1] + suit]
            c -= 1
        else:
            break
    
    # Reset counter and tick up from the specified card, adding in whatever is found.
    c = index
    while c < 12:
        if RANKS[c+1] + suit in codes:
            run_codes += [RANKS[c+1] + suit]
            c += 1
        else:
            break
    
    # Pick the largest meld, prioritising runs.
    meld_codes = run_codes
    if len(run_codes) < len(lot_codes):
        meld_codes = lot_codes
    
    # Convert meld codes into card objects and return.
    meld = [card]
    for c in hand:
        if c.code in meld_codes:
            meld += [c]
    return meld

        





class Human(Player):
    def __init__(self, name : str, hand : list = []):
        super().__init__(name, hand)

    # Choose to draw from either stock or discard. True = discard, False = stock.
    def draw(self):
        self.show_hand()
        ui = input("Draw from discard or stock?\n > ")
        while ui.lower() not in ["d", "s", "discard", "stock"]:
            print("Invalid input.")
            ui = input("Draw from discard or stock?\n > ")
        if ui.lower() in ["discard", "d"]:
            return True
        return False

    
    def meld(self):
        melds = []
        ui = " "
        while ui != '':
            self.show_hand()
            ui = input("Enter cards from your hand to form a meld, e.g. 'KH KC KS'. Or, enter '' to end.\n > ")
            
            # Check that ui codes >2 cards
            ui_valid = True
            codes = ui.split(" ")
            for code in codes:
                if len(code) != 2 or code[0] not in RANKS or code[1] not in SUITS or len(codes) < 3:
                    ui_valid = False
                    break
            if ui == "":
                continue
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
                self.show_hand()
                
            elif run(cards):
                melds.append(Run(cards))
                print("Run added.")
                for card in cards:
                    self.hand.remove(card)
                self.show_hand()
            else:
                print("Set did not form run or lot so was ignored.")
        
        return melds
            

    def lay_off(self, melds):
        ui = ' '
        card = None
        self.show_hand()
        ui = input("Enter a card to lay off. \n > ")

        while ui != '':
            while True:
                for c in self.hand:
                    if c.code == ui.upper():
                        card = c
                if card == None:
                    ui = input("Card not found in hand.\n > ")
                else:
                    break
        
            valid_melds = []
            for meld in melds:
                cards = meld.cards + [card]
                if run(cards) or lot(cards):
                    valid_melds += [meld]

            if len(valid_melds) == 0:
                print("There are no melds you can lay that card off on!")

            else:
                meld_of_choice = 0
                if len(valid_melds) > 1:

                    print(valid_melds)
                    ui = input("Which meld will you lay off on?\n > ")
                    while ui not in [str(i) for i in range(len(valid_melds))]:
                        ui = input("Invalid input, try again.\n > ")
                    meld_of_choice = int(ui)
                
                
                valid_melds[meld_of_choice].cards += [card]
                self.hand.remove(card)

            card = None
            self.show_hand()
            ui = input("Enter a card to lay off. \n > ")


    # Select a card from hand. Remove it from hand. Return it, so that table can add it to discard.
    def discard(self):
        self.show_hand()
        ui = input("Which card will you discard? \n > ")
        while True:
            rank = ui[0].upper()
            suit = ui[1].upper()
            for card in self.hand:
                if card.suit == suit and card.rank == rank:
                    self.hand.remove(card)
                    return card
            ui = input("Couldn't find that card. Try again. \n > ")




player1 = Human("Player 1")
player2 = Human("Player 2")
w = Bot("Wall-E")
e = Bot("Eva")

# my_table = Table([e, w], hand_size=4)



def winrate(players : list, n : int, hand_size = 0):
    wins = {}
    for i in range(len(players)):
        wins[i] = 0

    for j in range(n):
        print(j)
        mytable = Table(players, hand_size = hand_size)
        wins[players.index(mytable.play())] += 1
    
    return wins

print(winrate([e, w], 50))

# mytable = Table([e, w])
# mytable.play()


jd = Card("J", "D")
kd = Card("K", "D")
kh = Card("K", "H")
ts = Card("T", "S")
js = Card("J", "S")
qs = Card("Q", "S")
ks = Card("K", "S")
AS = Card("A", "S")
eights = Card("8", "S")

iid = Card("2", "D")
iiid = Card("3", "D")
ivd = Card("4", "D")
ad = Card("A", "D")


