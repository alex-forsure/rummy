import random

SUITS = ["H", "C", "S", "D"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
HAND_SIZES = {2:10, 3:7, 4:7, 5:6, 6:6}

class Card():
    def __init__(self, suit : str, rank : str):
        if suit not in SUITS:
            raise ValueError("Invalid suit given to card.")
        if rank not in RANKS:
            raise ValueError("Invalid rank given to card.")
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return self.rank + self.suit

# Returns a full unshuffled deck
def deck():
    out = []
    for suit in SUITS:
        for rank in RANKS:
            out.append(Card(suit, rank))
    return out


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

    # Shows all information of table, including stock and all players' hands
    def show_all(self):
        print("Stock:")
        print(self.stock)

        print("\nDiscard:")
        print(self.discard)

        for p in self.players:
            print("\n" + p.name + "'s hand:")
            print(p.hand)


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

        self.show_all()

        # Start game loop
        playing = True
        player_index = -1 # -1 so that player 0 starts
        while playing:
            self.show_all() # At some point must change this so only suitable information is shown

            player_index = (player_index + 1) % len(self.players)
            cur_player = self.players[player_index]
            print("It is " + cur_player.name + "'s turn.")

            # First, player draws. Method player.draw() returns true if he wants to draw from the discard pile. Otherwise he draws from the stock.
            if cur_player.draw():
                cur_player.hand.append(self.discard.pop())
            else:
                cur_player.hand.append(self.stock.pop())

            
            # Finally, player chooses a card to place on the discard pile.
            self.discard.append(cur_player.discard())


      
# Base class for CPU + human players
class Player():
    def __init__(self, name : str, hand : list = [], melds : list = []):
        self.hand = hand
        self.melds = melds
        self.name = name
    
    # Should probably put in errors for these functions? This is just a base class so these methods should never be called.
    def draw(self):
        print("Drawing")
    
    def discard(self):
        print("Discarding")



class Human(Player):
    def __init__(self, name : str, hand : list = [], melds : list = []):
        super().__init__(name, hand, melds)

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
        print("Hand: " + str(self.hand))
        ui = input()
        while True:
            rank = ui[0].upper()
            suit = ui[1].upper()
            for card in self.hand:
                if card.suit == suit and card.rank == rank:
                    self.hand.remove(card)
                    return card
            ui = input("Couldn't find that card. Try again. \n")




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
