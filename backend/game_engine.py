import random

# --- CONFIGURATION ---
USE_JOKERS = False
PENALTY_POINTS = 10
SLAP_PENALTY = 5
MAX_BENCH = 4

CARD_VALUES = {
    "A": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "JOKER": 14
}
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = list(CARD_VALUES.keys())

# --- CARD CLASS ---
class Card:
    def __init__(self, rank, suit=None):
        self.rank = rank
        self.suit = suit
        self.value = CARD_VALUES[rank]

    def __str__(self):
        return f"{self.rank}{self.suit}" if self.suit else self.rank

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank

# --- DECK CLASS ---
class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS if rank != "JOKER"]
        if USE_JOKERS:
            self.cards += [Card("JOKER"), Card("JOKER")]
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            return None
        return self.cards.pop()


# --- PLAYER CLASS ---
class Player:
    def __init__(self, name, is_bot=False):
        self.name = name
        self.is_bot = is_bot
        self.bench = [None] * MAX_BENCH
        self.seen = [False] * MAX_BENCH
        self.score = 0
        self.gandalf = False

    def place_card(self, index, card):
        self.bench[index] = card

    def reveal_card(self, index):
        self.seen[index] = True

    def total(self):
        return sum(card.value for card in self.bench if card)

    def __str__(self):
        bench_str = []
        for i, card in enumerate(self.bench):
            if self.seen[i] or self.is_bot:
                bench_str.append(f"[{card}]")
            else:
                bench_str.append("[?]")
        return f"{self.name}: {' '.join(bench_str)} (Score: {self.score})"

# --- GAME CLASS ---
class GandalfGame:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard_pile = [self.deck.draw()]
        self.current_player = 0
        self.gandalf_called = False
        self.send = lambda player, msg: None

        for p in self.players:
            for i in range(MAX_BENCH):
                p.place_card(i, self.deck.draw())
            self.initial_peek(p)

    def initial_peek(self, player):
        if player.is_bot:
            indexes = random.sample(range(MAX_BENCH), 2)
        else:
            print(f"\n{player.name}, peek at two of your cards (0–3):")
            indexes = []
            while len(indexes) < 2:
                raw = input(f"Card {len(indexes)+1}: ")
                if not raw.isdigit():
                    print("Please enter a number (0–3).")
                    continue
                i = int(raw)
                if not 0 <= i < 4:
                    print("Index out of range. Choose 0, 1, 2 or 3.")
                elif i in indexes:
                    print("You've already chosen this index.")
                else:
                    indexes.append(i)
        for i in indexes:
            player.reveal_card(i)
            if not player.is_bot:
                print(f"Card {i}: {player.bench[i]}")

    def play(self):
        while True:
            player = self.players[self.current_player]
            if player.gandalf:
                self.advance()
                continue

            print("\n" + "-" * 40)
            if self.players[self.current_player].is_bot:
                print("Top of discard pile: [hidden]")
            else:
                print(f"Top of discard pile: {self.discard_pile[-1]}")
            for p in self.players:
                if p == self.players[self.current_player] and not p.is_bot:
                    print(p)
                else:
                    print(f"{p.name}: [hidden] (Score: hidden)")


            if player.is_bot:
                self.bot_turn(player)
            else:
                self.human_turn(player)

            if self.gandalf_called and all(p.gandalf or p == self.players[self.current_player] for p in self.players):
                self.end_round()
                break

            self.advance()

    def human_turn(self, player):
        print(f"\n{player.name}'s turn.")
        options = ["pile", "gandalf"]
        if self.deck.cards:
            options.insert(0, "draw")

        print(f"Available actions: {', '.join(options)}")
        while True:
            options = ["pile", "gandalf"]
            if self.deck.cards:
                options.insert(0, "draw")

            print(f"Available actions: {', '.join(options)}")
            while True:
                cmd = input("Your action: ").strip().lower()
                if cmd not in options:
                    print(f"Invalid action. Choose from: {', '.join(options)}")
                else:
                    break
            if cmd == "draw" and "draw" in options:
                card = self.deck.draw()
                if card:
                    print(f"You drew: {card}")
                    self.choose_draw_action(player, card, from_pile=False)
                else:
                    print("Deck is empty.")
                return
            elif cmd == "pile":
                card = self.discard_pile[-1]
                self.choose_draw_action(player, card, from_pile=True)
                return
            elif cmd == "gandalf":
                player.gandalf = True
                self.gandalf_called = True
                print(f"{player.name} has called Gandalf!")
                return
            else:
                print("Invalid action.")

    def bot_turn(self, player):
        print(f"\n{player.name}'s turn (BOT).")

        if not self.deck.cards:
            print(f"⚠️ Deck is empty. {player.name} must swap from discard pile.")
            card = self.discard_pile[-1]  # internally used, but don't print
            worst_idx = max(
                (i for i in range(MAX_BENCH) if player.bench[i]),
                key=lambda i: player.bench[i].value
            )
            old = player.bench[worst_idx]
            player.place_card(worst_idx, card)
            player.reveal_card(worst_idx)
            self.discard_pile.append(old)
            print(f"{player.name} swapped a card using the discard pile.")
        else:
            card = self.deck.draw()
            print(f"{player.name} drew {card}")

            # If it's a special playable card, consider playing it
            if card.value in [7, 8, 9, 10, 11, 12]:
                if card.value in [7, 8]:  # Look at own card
                    worst_unseen = [
                        i for i in range(MAX_BENCH)
                        if not player.seen[i]
                    ]
                    if worst_unseen:
                        chosen = random.choice(worst_unseen)
                        player.reveal_card(chosen)
                        #print(f"{player.name} used {card} to reveal their card at {chosen}: {player.bench[chosen]}")
                        print(f"{player.name} used {card} to reveal their card at {chosen}")
                    else:
                        print(f"{player.name} plays {card} but all cards already seen.")
                    self.discard_pile.append(card)

                elif card.value in [9, 10]:  # Look at another's card
                    target = self.choose_other(player)
                    idx = random.randint(0, MAX_BENCH - 1)
                    print(f"{player.name} used {card} to peek at {target.name}'s card {idx}: {target.bench[idx]}")
                    self.discard_pile.append(card)

                elif card.value == 11:  # J - Swap one card with opponent
                    target = self.choose_other(player)
                    self_idx = max(
                        range(MAX_BENCH),
                        key=lambda i: player.bench[i].value
                    )
                    opp_idx = random.randint(0, MAX_BENCH - 1)
                    player.bench[self_idx], target.bench[opp_idx] = target.bench[opp_idx], player.bench[self_idx]
                    player.reveal_card(self_idx)
                    print(f"{player.name} used J to swap card {self_idx} with {target.name}'s card {opp_idx}")
                    self.discard_pile.append(card)

                elif card.value == 12:  # Q - Skip next player
                    print(f"{player.name} played Q — next player will be skipped.")
                    self.discard_pile.append(card)
                    self.advance()  # Skip next player

                return  # Special effect ends turn

            # Regular card: decide to play or swap
            if card.value <= 6:
                print(f"{player.name} plays {card} to discard pile.")
                self.discard_pile.append(card)
            else:
                worst_idx = max(
                    (i for i in range(MAX_BENCH) if player.bench[i]),
                    key=lambda i: player.bench[i].value
                )
                old = player.bench[worst_idx]
                player.place_card(worst_idx, card)
                player.reveal_card(worst_idx)
                self.discard_pile.append(old)
                print(f"{player.name} swapped {old} with {card}")

        # Intelligent Gandalf call
        if not self.gandalf_called:
            total = player.total()
            seen_count = sum(player.seen)
            worst_card = max(c.value for c in player.bench if c)

            confidence = 0
            if total <= 10:
                confidence += 1
            if seen_count >= 3:
                confidence += 1
            if worst_card <= 5:
                confidence += 1

            # Scale chance: base 10%, +15% per condition met
            chance = 0.1 + confidence * 0.15
            if random.random() < chance:
                player.gandalf = True
                self.gandalf_called = True
                print(f"{player.name} has confidently called Gandalf!")

    def choose_draw_action(self, player, card, from_pile):
        while True:
            action = input("Type 'swap' or 'play': ").strip().lower()
            if from_pile and action == "play":
                print("You cannot play directly from the discard pile. Only 'swap' is allowed.")
                continue
            if action not in ("swap", "play"):
                print("Invalid action. Please type 'swap' or 'play'.")
                continue
            break  # Valid input reached
        if action == "play":
            self.discard_pile.append(card)
            print(f"🃏 {player.name} plays {card} to the discard pile.")
            self.apply_card_effect(player, card)
            return
        # SWAP logic:
        while True:
            idx_input = input("Swap with which bench card? (0–3): ").strip()
            if not idx_input.isdigit():
                print("Please enter a valid number between 0 and 3.")
                continue
            idx = int(idx_input)
            if not 0 <= idx < 4:
                print("Index out of range. Must be 0, 1, 2, or 3.")
                continue
            break
        old = player.bench[idx]
        player.place_card(idx, card)
        player.reveal_card(idx)
        self.discard_pile.append(old)
        print(f"Swapped out {old} and placed {card} at index {idx}.")

    def apply_card_effect(self, player, card):
        val = card.value
        # ---- 7 or 8: Look at own card ----
        if val in [7, 8]:
            if player.is_bot:
                hidden_indexes = [i for i in range(4) if not player.seen[i]]
                if hidden_indexes:
                    chosen = random.choice(hidden_indexes)
                    player.reveal_card(chosen)
                    print(f"{player.name} used {card} to reveal one of their own cards.")
                else:
                    print(f"{player.name} used {card} but had no unseen cards.")
            else:
                while True:
                    idx_input = input("Choose a bench card to reveal (0–3): ").strip()
                    if not idx_input.isdigit():
                        print("Enter a valid number between 0 and 3.")
                        continue
                    idx = int(idx_input)
                    if not 0 <= idx < 4:
                        print("Index out of range.")
                        continue
                    break
                player.reveal_card(idx)
                print(f"👁️ You revealed card at {idx}: {player.bench[idx]}")
        # ---- 9 or 10: Look at another player's card ----
        elif val in [9, 10]:
            target = self.choose_other(player)
            if player.is_bot:
                print(f"{player.name} used a card to peek at another player's card.")
            else:
                print(f"Available players to peek:")
                others = [p for p in self.players if p != player]
                for i, p in enumerate(others):
                    print(f"{i}: {p.name}")
                while True:
                    choice = input("Select a player number: ").strip()
                    if not choice.isdigit():
                        print("Enter a number.")
                        continue
                    i = int(choice)
                    if not 0 <= i < len(others):
                        print("Invalid choice.")
                        continue
                    break
                target = others[i]
                while True:
                    idx_input = input(f"Which of {target.name}'s cards to peek at (0–3)? ").strip()
                    if not idx_input.isdigit():
                        print("Enter a valid number.")
                        continue
                    idx = int(idx_input)
                    if not 0 <= idx < 4:
                        print("Invalid card index.")
                        continue
                    break
                print(f"👁️ {target.name}'s card at {idx} is: {target.bench[idx]}")
        # ---- J: Swap a card with another player ----
        elif val == 11:
            target = self.choose_other(player)
            if player.is_bot:
                idx_self = max(range(4), key=lambda i: player.bench[i].value)
                idx_other = random.randint(0, 3)
                player.bench[idx_self], target.bench[idx_other] = target.bench[idx_other], player.bench[idx_self]
                player.reveal_card(idx_self)
                print(f"{player.name} swapped a card with another player.")
            else:
                print(f"Available players to swap with:")
                others = [p for p in self.players if p != player]
                for i, p in enumerate(others):
                    print(f"{i}: {p.name}")
                while True:
                    choice = input("Select a player number: ").strip()
                    if not choice.isdigit():
                        print("Enter a number.")
                        continue
                    i = int(choice)
                    if not 0 <= i < len(others):
                        print("Invalid choice.")
                        continue
                    break
                target = others[i]
                while True:
                    idx_self = input("Which of your cards to swap (0–3)? ").strip()
                    if idx_self.isdigit() and 0 <= int(idx_self) < 4:
                        idx_self = int(idx_self)
                        break
                    print("Invalid index.")
                while True:
                    idx_target = input(f"Which of {target.name}'s cards to take (0–3)? ").strip()
                    if idx_target.isdigit() and 0 <= int(idx_target) < 4:
                        idx_target = int(idx_target)
                        break
                    print("Invalid index.")
                player.bench[idx_self], target.bench[idx_target] = target.bench[idx_target], player.bench[idx_self]
                player.reveal_card(idx_self)
                print(f"Swapped your card {idx_self} with {target.name}'s card {idx_target}.")
        # ---- Q: Skip next player ----
        elif val == 12:
            print(f"{player.name} played Q. The next player will be skipped.")
            self.skip_next = True

    def choose_other(self, current):
        others = [p for p in self.players if p != current]
        return random.choice(others)

    def advance(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def end_round(self):
        print("\n=== ROUND END ===")
        for p in self.players:
            print(f"{p.name}: {[str(c) for c in p.bench]} | Total: {p.total()}")

        lowest_total = min(p.total() for p in self.players)
        winners = [p for p in self.players if p.total() == lowest_total]

        for p in self.players:
            if p.gandalf and p not in winners:
                print(f"{p.name} failed as Gandalf.")
                p.score += p.total() + PENALTY_POINTS
            elif p not in winners:
                p.score += p.total()

        print("\nScores:")
        for p in self.players:
            print(f"{p.name}: {p.score}")

# --- MAIN ---
def main():
    print("Welcome to Gandalf - Solo & Multiplayer Card Game")
    try:
        while True:
            total_raw = input("Total number of players (1–6): ")
            if not total_raw.isdigit():
                print("Please enter a number.")
                continue
            total = int(total_raw)
            if not 1 <= total <= 6:
                print("Must be between 1 and 6 players.")
                continue
            break

        while True:
            bots_raw = input(f"Number of bot players (0 to {total - 1}): ")
            if not bots_raw.isdigit():
                print("Please enter a number.")
                continue
            bots = int(bots_raw)
            if not 0 <= bots < total:
                print(f"Bot count must be between 0 and {total - 1}.")
                continue
            break

    except ValueError:
        print("Invalid input.")
        return

    if not (1 <= total <= 6) or not (0 <= bots < total):
        print("Invalid numbers.")
        return

    humans = total - bots
    players = []
    for i in range(humans):
        name = input(f"Enter name for player {i+1}: ")
        players.append(Player(name.strip(), is_bot=False))

    for i in range(bots):
        players.append(Player(f"Bot{i+1}", is_bot=True))

    game = GandalfGame(players)
    game.play()

if __name__ == "__main__":
    main()
