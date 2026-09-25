import uuid, json, asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .config import CORS_ORIGINS, SOLUTION_ARCHITECT_FORM_URL
from .agents import KoartAgentSystem

app = FastAPI(title="KOART Support System")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
async def health():
    return {"status":"ok","model":"configured by OPENAI_MODEL","solution_architect_form":SOLUTION_ARCHITECT_FORM_URL}

@app.get("/solution-architect/request", response_class=HTMLResponse)
async def sa_form():
    return HTMLResponse("""<!doctype html><html><head><title>KOART Solution Architect Request</title><style>
    body{font-family:Arial;max-width:800px;margin:40px auto;padding:20px}input,textarea{width:100%;padding:10px;margin:8px 0 16px}button{padding:12px 20px;background:#0f4169;color:#fff;border:0;border-radius:8px}</style></head>
    <body><h1>KOART Solution Architect Request</h1><p>Demo intake form for feature, enhancement and configuration requests.</p>
    <label>Business objective</label><textarea></textarea><label>Current behavior / configuration</label><textarea></textarea>
    <label>Requested change</label><textarea></textarea><label>OU / Market</label><input/>
    <label>Urgency</label><input/><label>Examples / screenshots</label><textarea></textarea>
    <label>Acceptance criteria</label><textarea></textarea><button>Submit Request</button></body></html>""")

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    async def emit(evt):
        await ws.send_json(evt)
    try:
        while True:
            msg = await ws.receive_json()
            question = msg.get("message","").strip()
            if not question: continue
            await emit({"type":"ticket","ticket_id":"KOART-"+uuid.uuid4().hex[:8].upper(),"message":question})
            system = KoartAgentSystem(emit)
            try:
                result = await system.handle(question)
                await emit({"type":"final","agent":result.agent,"route":result.route,"answer":result.answer})
            except Exception as e:
                await emit({"type":"error","message":str(e)})
            finally:
                await system.close()
    except WebSocketDisconnect:
        pass
