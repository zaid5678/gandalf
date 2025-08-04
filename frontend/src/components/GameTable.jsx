import React from "react";

export default function GameTable({ gameState, playerName }) {
  const { players, turn, top_discard, started } = gameState;

  return (
    <div className="mt-6 bg-gray-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-2">Game Table</h2>
      {started && <p className="text-sm text-green-400">Top of discard: {top_discard}</p>}
      <ul className="mt-4 space-y-2">
        {players.map((p, idx) => (
          <li
            key={idx}
            className={`flex justify-between p-2 rounded-md ${
              p.name === playerName ? "bg-blue-700" : "bg-gray-700"
            }`}
          >
            <span>
              {p.name} {p.name === turn ? "🟢" : ""}
            </span>
            <span>Score: {p.score}</span>
            <span>{p.bench.join(" ")}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
