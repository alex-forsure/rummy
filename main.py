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


def deck():
    out = []
    for suit in SUITS:
        for rank in RANKS:
            out.append(Card(suit, rank))
    return out

# Table attributes:
#  Players
#  Stock
#  Discard
#  Placed melds

class Table():
    def __init__(self, players : list, hand_size : int = 0):
        self.players = players
        if hand_size == 0:
            try:
                self.hand_size = HAND_SIZES[len(players)]
            except: 
                raise ValueError("Hand size must be specified for this number of players.")


    def play(self):
        # Set up stock, discard, players' hands
        stock = deck()
        random.shuffle(stock)
        hands = []
        for p in self.players:
            hand = []
            for i in range(self.hand_size):
                hand.append(stock.pop())
            p.hand = hand
        discard = [stock.pop()]
        
        print("Setup complete")
        print("Stock")
        print(stock)

        print("Player1 hand")
        print(self.players[0].hand)

        print("Player2 hand")
        print(self.players[1].hand)

        print("Discard")
        print(discard)



# Superclass for CPU + human players
class Player():
    def __init__(self, hand : list = [], melds : list = []):
        self.hand = hand
        self.melds = melds
    
    def move(self):
        print("Making move")


player1 = Player()
player2 = Player()
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
