import React, { useState, useRef } from "react";
import GameTable from "./components/GameTable";
import { OfflineGameEngine } from "./gameEngine";

const offlineGame = new OfflineGameEngine();

function App() {
  const [playerName, setPlayerName] = useState("");
  const [hasJoined, setHasJoined] = useState(false);
  const [gameState, setGameState] = useState({ players: [], started: false });
  const [log, setLog] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [numBots, setNumBots] = useState(1);
  const [gamePhase, setGamePhase] = useState("setup");
  const nameRef = useRef(null);

  const addLogMessage = (message) => {
    setLog(prev => [...prev, message]);
  };

  const handleGameResponse = (response) => {
    if (response.error) {
      addLogMessage(response.error);
    } else if (response.status) {
      addLogMessage(response.status);
    }
    if (response.players || response.started) {
      setGameState({
        players: response.players || gameState.players,
        started: response.started || gameState.started,
        turn: response.turn,
        top_discard: response.top_discard
      });
    }
  };

  const joinGame = () => {
    if (!inputValue.trim()) return;
    const response = offlineGame.addPlayer(inputValue.trim(), false);
    handleGameResponse(response);
    
    if (!response.error) {
      setPlayerName(inputValue.trim());
      setHasJoined(true);
      setGamePhase("setup");
      
      // Add bot players
      for (let i = 0; i < numBots; i++) {
        const botResponse = offlineGame.addPlayer(`Bot ${i + 1}`, true);
        handleGameResponse(botResponse);
      }
    }
  };

  const startGame = () => {
    const response = offlineGame.startGame();
    handleGameResponse(response);
    if (!response.error) {
      setGamePhase("playing");
    }
  };

  const peekCard = () => {
    const idx = prompt("Which card index to peek (0–3)?");
    if (idx !== null && !isNaN(idx) && idx >= 0 && idx <= 3) {
      const response = offlineGame.peek(playerName, parseInt(idx));
      handleGameResponse(response);
    }
  };

  const drawCard = () => {
    const response = offlineGame.draw();
    handleGameResponse(response);
  };

  const callGandalf = () => {
    addLogMessage("Gandalf called! Game Over!");
    setGamePhase("setup");
    setGameState({ players: [], started: false });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl text-green-500 mb-6">Gandalf Card Game</h1>

      {/* Setup Phase */}
      {!hasJoined && (
        <div className="space-y-4 mb-6">
          <div className="space-x-2">
            <input
              ref={nameRef}
              placeholder="Enter your name"
              className="p-2 text-black rounded"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && joinGame()}
            />
            <button 
              onClick={joinGame} 
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
              disabled={!inputValue.trim()}
            >
              Join Game
            </button>
          </div>
        </div>
      )}

      {/* Game Setup Phase */}
      {hasJoined && gamePhase === "setup" && (
        <div className="space-y-4 mb-6">
          <div className="space-x-2">
            <label className="text-gray-300">Number of Bots:</label>
            <input
              type="number"
              min="1"
              max="3"
              value={numBots}
              onChange={(e) => setNumBots(Math.min(3, Math.max(1, parseInt(e.target.value) || 1)))}
              className="p-2 text-black rounded w-20"
            />
            <button
              onClick={startGame}
              className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 transition-colors"
            >
              Start Game
            </button>
          </div>
        </div>
      )}

      {/* Game Playing Phase */}
      {gamePhase === "playing" && (
        <div className="space-x-2 mb-4">
          <button onClick={drawCard} className="bg-purple-600 px-4 py-2 rounded hover:bg-purple-700 transition-colors">
            Draw
          </button>
          <button onClick={peekCard} className="bg-yellow-600 px-4 py-2 rounded hover:bg-yellow-700 transition-colors">
            Peek
          </button>
          <button onClick={callGandalf} className="bg-red-600 px-4 py-2 rounded hover:bg-red-700 transition-colors">
            Gandalf
          </button>
        </div>
      )}

      <GameTable gameState={gameState} playerName={playerName} />

      <div className="mt-6 text-sm text-gray-400">
        <h2 className="text-lg font-semibold">Game Log</h2>
        <ul className="mt-2">
          {log.slice(-5).map((l, i) => (
            <li key={i}>• {l}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;