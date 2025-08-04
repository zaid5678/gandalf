export class OfflineGameEngine {
  constructor() {
    this.players = [];
    this.deck = this.createDeck();
    this.discardPile = [];
    this.started = false;
    this.currentTurn = 0;
  }

  createDeck() {
    const deck = [];
    const values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    const suits = ['♠', '♣', '♥', '♦'];
    
    for (let suit of suits) {
      for (let value of values) {
        deck.push(value + suit);
      }
    }
    
    return this.shuffle(deck);
  }

  shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  addPlayer(name, isBot = false) {
    if (this.started) return { error: "Game already started" };
    if (this.players.find(p => p.name === name)) return { error: "Player name taken" };
    
    this.players.push({
      name,
      isBot,
      bench: [],
      seen: [false, false, false, false],
      score: 0
    });
    
    return { status: "Player added", players: this.getGameState().players };
  }

  startGame() {
    if (this.players.length < 2) return { error: "Need at least 2 players" };
    if (this.started) return { error: "Game already started" };
    
    this.started = true;
    this.deck = this.createDeck();
    
    // Deal cards
    for (let player of this.players) {
      player.bench = [this.deck.pop(), this.deck.pop(), this.deck.pop(), this.deck.pop()];
      player.seen = [false, false, false, false];
    }
    
    this.discardPile = [this.deck.pop()];
    return { status: "Game started", ...this.getGameState() };
  }

  draw() {
    if (!this.started) return { error: "Game not started" };
    if (!this.deck.length) return { error: "Deck is empty" };
    
    const card = this.deck.pop();
    return { status: "Card drawn", card, ...this.getGameState() };
  }

  peek(playerName, cardIndex) {
    if (!this.started) return { error: "Game not started" };
    
    const player = this.players.find(p => p.name === playerName);
    if (!player) return { error: "Player not found" };
    
    if (cardIndex < 0 || cardIndex > 3) return { error: "Invalid card index" };
    
    player.seen[cardIndex] = true;
    const card = player.bench[cardIndex];
    
    return { status: `Peeked at card ${cardIndex}: ${card}`, ...this.getGameState() };
  }

  getGameState() {
    return {
      started: this.started,
      players: this.players.map(p => ({
        ...p,
        bench: p.bench.map((card, i) => p.seen[i] ? card : "?")
      })),
      turn: this.started ? this.players[this.currentTurn].name : null,
      top_discard: this.discardPile.length ? this.discardPile[this.discardPile.length - 1] : null
    };
  }
}
