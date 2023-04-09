import random


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]

    def __init__(self):
        self.cards = []
        for suit in self.suits:
            for rank in self.ranks:
                card = Card(rank, suit)
                self.cards.append(card)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def put(self, card):
        self.cards.append(card)


class Player:
    def __init__(self, name):
        self.cards = []
        self.hand = []
        self.secret = []
        self.score = 0
        self.name = name
        self.pistiCount = 0

    def calScore(self):
        self.cards.extend(self.secret)
        for card in self.cards:
            if card.rank == "Jack":
                self.score += 1
            if card.rank == "10" and card.suit == "Diamonds":
                self.score += 3
            if card.rank == "2" and card.suit == "Clubs":
                self.score += 2
        self.score += self.pistiCount * 10

    def add_card(self, card):
        self.hand.append(card)

    def add_cards(self, cards):
        self.cards.extend(cards)

    def remove_card(self, index):
        return self.hand.pop(int(index) - 1)

    def print_hand(self):
        for card in self.hand:
            print(f"{self.hand.index(card) + 1}:{card.__str__()}")

    def getHand(self):
        hand = ""
        for card in self.hand:
            hand = hand + card.__str__() + ","
        hand = "[" + hand[:-1] + "]"
        return hand

    def getCards(self):
        hand = ""
        for card in self.cards:
            hand = hand + card.__str__() + ","
        for card in self.secret:
            hand = hand + card.__str__() + ","
        hand = "[" + hand[:-1] + "]"
        return hand


def writeToFile(round, playerAI, playerUser, pile, hidden):
    if round == 0:
        filename = "acilis.txt"
    else:
        filename = "tur" + str(round) + ".txt"
    file = open(filename, "w")
    file.write(f"Hand of the User:{playerUser.getHand()}\n")
    file.write(f"Cards of the User:{playerUser.getCards()}\n")
    file.write(f"Hand of the AI:{playerAI.getHand()}\n")
    file.write(f"Cards of the AI:{playerAI.getCards()}\n")
    strPile = ""
    for card in pile:
        strPile = strPile + card.__str__() + ","
    strPile = "[" + strPile[:-1] + "]"
    file.write(f"Current pile:{strPile}\n")
    if len(hidden) > 0:
        strHidden = ""
        for card in hidden:
            strHidden = strHidden + card.__str__() + ","
        strHidden = "[" + strHidden[:-1] + "]"
        file.write(f"Hidden cards in the pile:{strHidden}\n")
    file.close()


def doesTake(lastCard, playedCard):
    if playedCard.rank == "Jack":
        return True
    if lastCard is None:
        return False
    if lastCard.rank == playedCard.rank:
        return True
    return False


def getMove(playerAI, playerUser, pile, round):
    # if computer has a card with same rank as the last open card  it plays the card
    for card in playerAI.hand:
        if (len(pile) == 0):
            break
        if (pile[-1].rank == card.rank):
            return playerAI.hand.index(card)
    # if computer has a Jack it plays the jack it leaves a possibility for Pisti
    for card in playerAI.hand:
        if card.rank == "Jack":
            return playerAI.hand.index(card)

    allKnownCards = []
    allKnownCards.extend(playerUser.cards)
    allKnownCards.extend(playerAI.cards)
    allKnownCards.extend(pile)
    allKnownCards.extend(playerAI.hand)
    if round == 6 and len(playerAI.secret) != 0:
        allKnownCards.extend(playerUser.hand)
    rankCounts = {}
    for rank in Deck.ranks:
        rankCounts[rank] = 0
    for card in allKnownCards:
        rankCounts[card.rank] += 1

    # computer count known cards and plays the card that has the least possibility to be in users hand
    move = 0
    for card in playerAI.hand:
        if rankCounts[card.rank] > rankCounts[playerAI.hand[move].rank]:
            move = playerAI.hand.index(card)
    return move


class Pisti:
    def __init__(self):
        self.deck = Deck()
        self.playerUser = Player("User")
        self.playerAI = Player("AI")
        self.current_player = None
        self.opponent = None
        self.pile = []
        self.hidden = []
        self.round = 0

    def deal_cards(self):
        for i in range(4):
            self.playerUser.add_card(self.deck.deal())
            self.playerAI.add_card(self.deck.deal())

    def play_game(self):

        for i in range(3):
            self.hidden.append(self.deck.deal())
        firstCart = self.deck.deal()
        while firstCart.rank == "Jack":
            self.deck.put(firstCart)
            self.deck.shuffle()
            firstCart = self.deck.deal()
        self.pile.append(firstCart)
        self.deal_cards()
        writeToFile(self.round, self.playerAI, self.playerUser, self.pile, self.hidden)

        while len(self.deck.cards) > 0 or len(self.playerUser.hand) > 0:
            if len(self.playerUser.hand) == 0:
                self.deal_cards()
                self.round += 1
                writeToFile(self.round, self.playerAI, self.playerUser, self.pile, self.hidden)
            print(f"Your turn!")
            if len(self.pile) == 0:
                print("No open card.")
            else:
                print(f"Open card is: {self.pile[-1]}")

            self.playerUser.print_hand()

            move = input()
            while not move.isnumeric() or not (len(self.playerUser.hand) >= int(move) > 0):
                print("Invalid input please try again.")
                self.playerUser.print_hand()
                move = input()
            playedCard = self.playerUser.remove_card(move)
            if len(self.pile) == 0:
                lastCard = None
            else:
                lastCard = self.pile[-1]
            self.pile.append(playedCard)
            if doesTake(lastCard, playedCard):
                print("Pisti")
                if lastCard is not None and lastCard.rank == playedCard.rank and len(self.pile) == 1 and len(
                        self.hidden) == 0:
                    self.playerUser.pistiCount += 1
                self.playerUser.cards.extend(self.pile)
                self.playerUser.secret.extend(self.hidden)
                self.pile = []
                self.hidden = []

            move = getMove(self.playerAI, self.playerUser, self.pile, self.round)
            print(f"Computers move is:{self.playerAI.hand[int(move)]}")
            playedCard = self.playerAI.remove_card(move)
            if len(self.pile) == 0:
                lastCard = None
            else:
                lastCard = self.pile[-1]
            self.pile.append(playedCard)
            if doesTake(lastCard, playedCard):

                if lastCard is not None and lastCard.rank == playedCard.rank and len(self.pile) == 1 and len(
                        self.hidden) == 0:
                    print("Pisti")
                    self.playerAI.pistiCount += 1
                self.playerAI.cards.extend(self.pile)
                self.playerAI.secret.extend(self.hidden)
                self.pile = []
                self.hidden = []

        print("\nGame over!")
        self.playerAI.calScore()
        self.playerUser.calScore()
        if len(self.playerAI.cards) > len(self.playerUser.cards):
            self.playerAI.score += 3
        if len(self.playerAI.cards) < len(self.playerUser.cards):
            self.playerUser.score += 3
        print(f"{self.playerUser.name}: {self.playerUser.score}")
        print(f"{self.playerAI.name}: {self.playerAI.score}")
        if self.playerUser.score > self.playerAI.score:
            print("You win!")
        elif self.playerAI.score > self.playerUser.score:
            print("You lose!")
        else:
            print("It is a tie!")


if __name__ == "__main__":
    game = Pisti()
    game.play_game()
