# backend/game_engine.py

import random

class Card:
    def __init__(self, rank, suit=None):
        self.rank = rank
        self.suit = suit
        self.value = self.card_value(rank)

    def __str__(self):
        return f"{self.rank}{self.suit}" if self.suit else self.rank

    def card_value(self, rank):
        values = {
            "A": 1, "2": 2, "3": 3, "4": 4, "5": 5,
            "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
            "J": 11, "Q": 12, "K": 13
        }
        return values.get(rank, 0)

def generate_deck():
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    deck = [Card(rank, suit) for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

class Player:
    def __init__(self, name):
        self.name = name
        self.bench = []
        self.seen = []
        self.score = 0

    def to_dict(self, hide_cards=True):
        if hide_cards:
            return {"name": self.name, "score": self.score, "bench": ["?" for _ in self.bench]}
        else:
            return {"name": self.name, "score": self.score, "bench": [str(c) for c in self.bench]}

class GandalfGame:
    def __init__(self):
        self.players = []
        self.started = False
        self.current_turn = 0
        self.deck = generate_deck()
        self.discard_pile = []
        self.gandalf_called = False

    def add_player(self, name):
        if self.started:
            return {"error": "Game already started"}
        if any(p.name == name for p in self.players):
            return {"error": "Player already exists"}
        self.players.append(Player(name))
        return {"status": "player_added", "player": name}

    def start(self):
        if self.started:
            return {"error": "Game already started"}
        if len(self.players) < 2:
            return {"error": "Need at least 2 players to start"}

        # Deal 4 cards to each player
        for player in self.players:
            player.bench = [self.deck.pop() for _ in range(4)]
            player.seen = [False, False, False, False]
        self.discard_pile.append(self.deck.pop())
        self.started = True
        return {"status": "game_started", "top_discard": str(self.discard_pile[-1])}

    def get_state(self, player_name=None):
        return {
            "started": self.started,
            "players": [
                p.to_dict(hide_cards=(p.name != player_name))
                for p in self.players
            ],
            "turn": self.players[self.current_turn].name if self.started else None,
            "top_discard": str(self.discard_pile[-1]) if self.discard_pile else None
        }

    def handle_action(self, data):
        action = data.get("move")
        player_name = data.get("player")
        player = next((p for p in self.players if p.name == player_name), None)

        if not player:
            return {"error": "Invalid player"}

        if action == "draw":
            if not self.deck:
                return {"error": "Deck is empty"}
            card = self.deck.pop()
            return {"status": "drawn", "card": str(card)}

        elif action == "peek":
            index = int(data.get("index", -1))
            if 0 <= index < len(player.bench):
                player.seen[index] = True
                return {"status": "peeked", "card": str(player.bench[index]), "index": index}
            else:
                return {"error": "Invalid index"}

        elif action == "swap":
            index = int(data.get("index", -1))
            new_card = data.get("card")
            if not new_card:
                return {"error": "Missing new card"}
            old_card = player.bench[index]
            player.bench[index] = Card(new_card)  # Simplified for demo
            self.discard_pile.append(old_card)
            player.seen[index] = True
            return {"status": "swapped", "index": index, "discarded": str(old_card)}

        elif action == "gandalf":
            self.gandalf_called = True
            return {"status": "gandalf_called", "player": player.name}

        else:
            return {"error": f"Unknown action '{action}'"}
