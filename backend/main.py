from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from game_engine import GandalfGame  # your logic file

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {}

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    if game_id not in games:
        games[game_id] = GandalfGame([])
    game = games[game_id]

    while True:
        data = await websocket.receive_json()
        action = data.get("action")

        if action == "create_player":
            name = data.get("name")
            game.add_player(name)
            await websocket.send_json({"status": "player_created", "player": name})
        
        elif action == "start_game":
            game.start()
            await websocket.send_json({"status": "game_started"})

        elif action == "player_action":
            result = game.handle_action(data)
            await websocket.send_json(result)

        # Add more command handlers here
