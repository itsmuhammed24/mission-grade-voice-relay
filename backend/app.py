import os
import json
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from asr import transcribe_audio_bytes
from llm import analyze_text



# FastAPI APP

app = FastAPI()

# CORS (au cas où tu mixes d'autres front plus tard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# WebSocket Manager

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connecté ({len(self.active_connections)} clients)")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client déconnecté ({len(self.active_connections)} clients)")

    async def broadcast(self, message: str):
        for conn in list(self.active_connections):
            try:
                await conn.send_text(message)
            except:
                self.disconnect(conn)


manager = ConnectionManager()



# Mission Log Utility


LOG_PATH = os.path.join(os.path.dirname(__file__), "mission_logs", "mission_log.jsonl")

def append_log(entry: dict):
    """Ajoute une ligne JSON dans mission_logs/mission_log.jsonl."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")



# ROUTES HTTP


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/audio-chunk")
async def receive_audio_chunk(file: UploadFile = File(...)):
    """
    1. Réception du chunk audio (mp4)
    2. Transcription Whisper
    3. Analyse tactique LLM
    4. Log mission dans un fichier .json
    5. Broadcast WebSocket vers le client
    """
    audio_bytes = await file.read()
    size = len(audio_bytes)
    print(f" Chunk reçu : {size} bytes")

    if size == 0:
        return {"received": True, "size": size, "text": ""}

    
    # 1. Transcription Whisper

    text = transcribe_audio_bytes(audio_bytes)
    print(f"Whisper : {text}")


   
    # 2. Analyse LLM
    
    analysis = analyze_text(text)
    print(f"Analyse LLM : {analysis}")



    # 3. Logging mission
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "text": text,
        "analysis": analysis
    }
    append_log(log_entry)


 
    # 4. Broadcast WebSocket

    await manager.broadcast(json.dumps({
        "type": "analysis",
        "text": text,
        "analysis": analysis
    }))


   
    # 5. Réponse HTTP
    
    return {
        "received": True,
        "size": size,
        "text": text,
        "analysis": analysis
    }



# WebSocket Endpoint


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
      
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)



# Static Client


app.mount(
    "/",
    StaticFiles(directory="client", html=True),
    name="client"
)
