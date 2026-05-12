"""FastAPI server for gameRocket web version."""

import sys
import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure game/ package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.engine import GameEngine


# ── Pydantic models ──────────────────────────────────────────────

class MoveRequest(BaseModel):
    direction: str


class AnswerRequest(BaseModel):
    answer: str


# ── Game state (singleton per server) ────────────────────────────

# Use a mutable container so we can reassign without `global`
_engine_state = {"engine": GameEngine("questions.json")}


# ── WebSocket manager ────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active_connections.append(ws)
        # Send initial state
        await ws.send_json({"type": "state", "state": _engine_state["engine"].get_state()})

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def broadcast(self, message: dict) -> None:
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


# ── Lifespan ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# ── App ──────────────────────────────────────────────────────────

app = FastAPI(title="gameRocket Web", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/css", StaticFiles(directory=os.path.join(static_dir, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(static_dir, "js")), name="js")
app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r") as f:
        return f.read()


# ── REST endpoints ───────────────────────────────────────────────

@app.post("/api/game/start")
async def start_game():
    _engine_state["engine"] = GameEngine("questions.json")
    return {"state": _engine_state["engine"].get_state()}


@app.post("/api/game/move")
async def move_game(req: MoveRequest):
    direction = req.direction.lower()
    eng = _engine_state["engine"]
    if direction == "forward":
        eng.move_forward()
    elif direction == "up":
        eng.move_up()
    elif direction == "down":
        eng.move_down()
    else:
        return {"error": f"Invalid direction: {direction}"}, 400
    state = eng.get_state()
    challenge = None
    if state["challenge_active"] and state["current_challenge"]:
        challenge = state["current_challenge"]
    return {"state": state, "challenge": challenge}


@app.post("/api/game/answer")
async def answer_game(req: AnswerRequest):
    eng = _engine_state["engine"]
    eng.answer_challenge(req.answer)
    state = eng.get_state()
    result = "correct" if state["score"] > 0 else "wrong"
    # Determine result from challenge state
    if state["game_over"]:
        result = "game_over"
    elif state["victory"]:
        result = "victory"
    return {"state": state, "result": result}


@app.post("/api/game/reset")
async def reset_game():
    _engine_state["engine"] = GameEngine("questions.json")
    return {"state": _engine_state["engine"].get_state()}


@app.get("/api/game/state")
async def get_game_state():
    return {"state": _engine_state["engine"].get_state()}


# ── WebSocket endpoint ──────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")
            eng = _engine_state["engine"]

            if msg_type == "move":
                direction = data.get("direction", "forward")
                if direction == "forward":
                    eng.move_forward()
                elif direction == "up":
                    eng.move_up()
                elif direction == "down":
                    eng.move_down()

                state = eng.get_state()
                message = {"type": "state", "state": state}

                if state["challenge_active"] and state["current_challenge"]:
                    message["challenge"] = state["current_challenge"]

                if state["game_over"]:
                    message["type"] = "game_over"
                    message["score"] = state["score"]

                if state["victory"]:
                    message["type"] = "victory"
                    message["score"] = state["score"]
                    message["wrong_answers"] = state["wrong_answers"]

                await ws.send_json(message)

            elif msg_type == "answer":
                answer = data.get("answer", "")
                eng.answer_challenge(answer)
                state = eng.get_state()

                if state["game_over"]:
                    await ws.send_json({
                        "type": "game_over",
                        "state": state,
                        "score": state["score"],
                    })
                elif state["victory"]:
                    await ws.send_json({
                        "type": "victory",
                        "state": state,
                        "score": state["score"],
                        "wrong_answers": state["wrong_answers"],
                    })
                else:
                    await ws.send_json({"type": "state", "state": state})

            elif msg_type == "reset":
                _engine_state["engine"] = GameEngine("questions.json")
                await ws.send_json({"type": "state", "state": _engine_state["engine"].get_state()})

    except WebSocketDisconnect:
        manager.disconnect(ws)
