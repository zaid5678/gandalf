import React, { useState, useEffect } from 'react';

const socket = new WebSocket("ws://localhost:8000/ws/game123");

export default function App() {
  const [messages, setMessages] = useState([]);
  const [name, setName] = useState("");

  useEffect(() => {
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };
  }, []);

  const createPlayer = () => {
    socket.send(JSON.stringify({ action: "create_player", name }));
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-4">Gandalf.io</h1>
      <input
        className="text-black p-2"
        placeholder="Enter your name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <button onClick={createPlayer} className="ml-2 bg-blue-500 px-4 py-2 rounded">
        Join Game
      </button>
      <pre className="mt-4">{JSON.stringify(messages, null, 2)}</pre>
    </div>
  );
}
