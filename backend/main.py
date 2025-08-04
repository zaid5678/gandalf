# backend/main.py

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from game_engine import GandalfGame

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {"default": GandalfGame()}

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()

    game = games.setdefault(game_id, GandalfGame())

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "create_player":
                name = data.get("name")
                result = game.add_player(name)
                await websocket.send_json(result)

            elif action == "start_game":
                result = game.start()
                await websocket.send_json(result)

            elif action == "get_state":
                result = game.get_state(data.get("player"))
                await websocket.send_json(result)

            elif action == "player_action":
                result = game.handle_action(data)
                await websocket.send_json(result)

            else:
                await websocket.send_json({"error": "Unknown action"})
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        await websocket.close()
