import random
from copy import copy

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


# Returns a full unshuffled deck
def deck():
    out = []
    for suit in SUITS:
        for rank in RANKS:
            out.append(Card(rank, suit))
    return out

# Returns whether cds forms a valid run
def run(cds:list):
    if len(cds) < 3:
        return False
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
        return True
    else:
        return False

# Returns whether cds forms a valid lot
def lot(cds: list):
    if len(cds) < 3:
        return False
    rank = cds[0].rank
    for card in cds:
        if card.rank != rank:
            return False
    return True


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
        if not lot(cards):
            raise ValueError("Attempted to create a Lot from an invalid set of cards.")
        self.cards = cards
        self.is_run = False
        self.is_lot = True


class Run(Meld):
    def __init__(self, cards):
        if not run(cards):
            raise ValueError("Attempted to create a Run from an invalid set of cards.")
        self.cards = cards
        self.is_run = True
        self.is_lot = False
    

class Table():
    def __init__(self, players : list, hand_size : int = 0, output : bool = True, show_hands : bool = False):
        self.players = players
        for player in players:
            player.table = self # Bots need to see melds, discard, seen
        self.hand_size = hand_size
        if hand_size == 0: # Default
            try:
                self.hand_size = HAND_SIZES[len(players)]
            except: 
                raise ValueError("Hand size must be specified for this number of players.")
        self.stock = []
        self.discard = []
        self.melds = []
        self.output = output # Can turn output off for mass testing
        self.seen = [] # Used by bots to estimate contents of stock
        self.show_hands = show_hands # Can show all players' hands for testing

    # Shows all information of table, including stock and all players' hands
    def show_all(self):
        if self.output:
            print("Stock:")
            print(self.stock)

            print("\nDiscard:")
            print(self.discard)

            for p in self.players:
                print("\n" + p.name + "'s hand:")
                print(p.hand)

    # Shows information that should be visible in a normal game
    def show_table(self):
        if self.output:
            self.show_melds()
            print("")            
            print(("STOCK   [??]      DISCARD [" + str(self.discard[-1]) + "]").center(60, ' '))
            print("")


    def show_melds(self):
        if self.output:
            print("MELDS".center(60, ' '))
            melds_text = []
            for i, meld in enumerate(self.melds):
                if i % 3 == 0:
                    melds_text += ['']
                melds_text[i//3] += " " + str(meld) + " "
            for meld_text in melds_text:
                print(meld_text.center(60, " "))

    # Shows header and table info for new turn
    def new_turn_output(self, cur_player):
        if self.output:
            print((" "  + cur_player.name + "'s turn ").center(60, '-'))
            print("")
            self.show_table()
            print("")

    # Shows melds for game end
    def game_end_output(self):
        if self.output:
            print(" GAME END ".center(60, "-"))
            print("")
            self.show_melds()
            print("")

    # Shows scores and winner
    def final_score_output(self, winner):
        if self.output:
            print((winner.name + " WINS").center(60, ' '))
            print("")
            for player in self.players:
                print(player.name + ": " + str(player.score))

    # Game loop
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
        deal = self.stock.pop()
        self.discard = [deal]
        self.seen = [deal]

        # Start game loop
        player_index = -1 # -1 so that player 0 starts
        stalemate_counter = 0 # Fail-safe for bots looping infinitely.
        while True:
            stalemate_counter += 1
            if stalemate_counter >= 10:
                if self.output: print("Stalemate fail-safe triggered.")
                break
            if self.show_hands:
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


            if self.discard != []:
                # First, player draws. Method player.draw() returns true if he wants to draw from the discard pile. Otherwise he draws from the stock.
                if cur_player.draw():
                    deal = self.discard.pop()
                else:
                    deal = self.stock.pop()
                    stalemate_counter = 0
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
                self.seen.append(self.discard[-1])
            if cur_player.hand == []: # Also go out if hand is empty after discarding
                cur_player.out = True

        # Game has ended

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
        print((self.name + "'s Hand").center(60, " "))
        hand_text = ""
        for card in self.hand:
            hand_text += str(card) + " "
        hand_text = hand_text.removesuffix(" ")
        print(hand_text.center(60, " "))


    # Should probably put in errors for these functions? This is just a base class so these methods should never be called.
    def draw(self):
        pass
        
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
        print((self.name + "'s Hand").center(60, " "))
        hand_text = ""
        for card in self.hand:
            hand_text += str(card) + " "
        hand_text = hand_text.removesuffix(" ")
        print(hand_text.center(60, " "))
    
    
    def discard(self):
        pass


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
                
            elif run(cards):
                melds.append(Run(cards))
                print("Run added.")
                for card in cards:
                    self.hand.remove(card)
            else:
                print("Set did not form run or lot so was ignored.")
        
        return melds
            

    def lay_off(self, melds):
        ui = ' '
        card = None
        self.show_hand()
        ui = input("Enter a card to lay off, or '' to pass. \n > ")

        while ui != '':
            valid_input = False
            while True:
                for c in self.hand:
                    if c.code == ui.upper():
                        card = c
                if card == None:
                    ui = input("Card not found in hand, try again.\n > ")
                    break
                else:
                    valid_input = True
                    break
            if not valid_input: 
                continue
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


# A base Bot class which draws & discards based on EV, lays off arbitrarily wherever it can,
# and plays melds with the highest score whenever it can.
class Bot(Player):
    def __init__(self, name : str, hand : list = [], output : bool = True, v_meld = 1, v_strong = 0.5, v_lay = 0.75):
        super().__init__(name, hand)
        self.output = output
        self.meld_value = v_meld
        self.strong_value = v_strong
        self.lay_value = v_lay
    
    def draw(self):
        # We come up with a list of all cards that could be in the stock.
        stock = [c.code for c in deck()]
        for c in self.table.seen:
            if c.code in stock: stock.remove(c.code)
        for meld in self.table.melds:
            for c in meld.cards:
                if c.code in stock: stock.remove(c.code)
        for c in self.hand:
            if c.code in stock: stock.remove(c.code)
        
        # We take EV of stock.
        exp_value = 0
        for c in stock:
            exp_value += self.value(Card(c[0], c[1]), self.hand)
        exp_value = exp_value/len(stock)

        # If value of discard is more than EV of stock, draw from discard.
        if self.value(self.table.discard[-1], self.hand) >= exp_value:
            if self.output:
                print(self.name + " draws from discard.")
            return True
        
        # Else draw from stock.
        if self.output:
            print(self.name + " draws from stock.")
        return False
    

    def meld(self):
        melds = []
        while True:

            # Find the biggest meld by no. of cards
            max_meld = []
            for card in self.hand:
                h = copy(self.hand)
                h.remove(card)
                cur_meld = meld_with(card, h)
                if len(cur_meld) > len(max_meld):
                    max_meld = cur_meld
            
            # Check that meld is valid. 
            # If not, this means a meld of 1 or 2 cards has been found, and there is no valid meld.
            if lot(max_meld):
                max_meld = Lot(max_meld)
            elif run(max_meld):
                max_meld = Run(max_meld)
            else:
                break
            
            # Add meld to list and remove cards from hand
            melds.append(max_meld)
            for card in max_meld.cards:
                self.hand.remove(card)

        return(melds)


    def lay_off(self, melds):
        while True:
            # Loop through hand and lay off all possible cards until a full pass is completed with no lays.
            laid = False
            for meld in melds:
                for card in self.hand:
                    if lot(meld.cards + [card]) or run(meld.cards + [card]):
                        meld.cards += [card]
                        self.hand.remove(card)
            if not laid:
                break
        
    
    def discard(self):
        # Evaluate cards by considering their value if they weren't in hand.
        min_value = 2
        min_card = None
        for card in self.hand:
            # Make a copy of hand without the card.
            h = copy(self.hand)
            h.remove(card)
            # Check value and update min_value, min_card if appropriate.
            c_value = self.value(card, self.hand)
            if c_value < min_value:
                min_value = c_value
                min_card = card 
        # Remove and return the card of minimum value.
        self.hand.remove(min_card)
        return(min_card)
    
    
    def value(self, card, hand):
        # First, if a card can immediately be laid off, its value is 1.
        for meld in self.table.melds:
            if lot(meld.cards + [card]) or run(meld.cards + [card]):
                return self.lay_value

        # Next, if a card can immediately be melded, its value is 1.
        if len(meld_with(card, hand)) >= 3:
            return self.meld_value
        
        # Finally, if a card pairs with another card, its value is 0.5.
        if len(meld_with(card, hand)) == 2:
            return self.strong_value
        
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


def winrate(players : list, rounds : int, hand_size = 0, rotate = True):
    wins = {}
    player_index = copy(players)
    for i in range(len(players)):
        wins[i] = 0

    for r in range(rounds//len(players)):
        for p in players:
            mytable = Table(players, hand_size = hand_size, output = False)
            wins[player_index.index(mytable.play())] += 1
            if rotate:
                players.insert(0, players.pop())
    
    return wins


####### Playing a game

# Human player takes user input for moves.
player1 = Human("Alex") 
# Bot uses value function for moves. 
walle = Bot("Wall-E") 

## If you want to add more bots, create a new bot:
# my_bot = Bot("Bot name").
# Then add it to the list in the table:
# mytable = Table([player1, walle, my_bot]).


# Table object handles game. Turn on show_hands for cheats. Hand size 7 makes the game shorter (default for 2 players is 10).
mytable = Table([player1, walle], show_hands = False, hand_size = 7) 

# Begin the game.
mytable.play()


## Use following code for mass testing.
# b0 = Bot("Bot 0", output = False, v_strong = 0.25)
# b1 = Bot("Bot 1", output = False, v_strong = 0.25)
# b2 = Bot("Bot 2", output = False, v_strong = 0.25)
# b3 = Bot("Bot 3", output = False, v_strong = 0.25)
# b4 = Bot("Bot 4", output = False, v_strong = 0.25)
# print("Running")
# for i in range(6):
#     print(winrate([b0, b1, b2, b3, b4], 1000, rotate = False))