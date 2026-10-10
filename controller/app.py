"""
Remote controller for the PP1 Reveal.js presentation.

Single-origin FastAPI app that:
  - serves the mobile control panel at "/"
  - serves the presentation (from ../presentation) at "/presentation/"
  - injects the deck bridge script into the served index.html
  - relays slide commands over a WebSocket at "/ws"

Kept fully separate from the presentation code in ../presentation.
Intended for local-network use only (no authentication in this version).
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
PRESENTATION_DIR = (REPO_ROOT / "presentation").resolve()
STATIC_DIR = BASE_DIR / "static"

DECK_CLIENT_SRC = "/static/deck-client.js"
ALLOWED_ACTIONS = {"next", "prev", "home", "end"}

app = FastAPI(title="PP1 Presentation Remote", docs_url=None, redoc_url=None)


class Hub:
    """Tracks connected decks and control panels and relays messages."""

    def __init__(self) -> None:
        self.decks: set[WebSocket] = set()
        self.controls: set[WebSocket] = set()
        self.last_state: dict | None = None

    def register(self, websocket: WebSocket, role: str) -> None:
        if role == "deck":
            self.decks.add(websocket)
        else:
            self.controls.add(websocket)

    def unregister(self, websocket: WebSocket, role: str) -> None:
        if role == "deck":
            self.decks.discard(websocket)
        else:
            self.controls.discard(websocket)

    async def _send(self, websocket: WebSocket, message: dict) -> bool:
        try:
            await websocket.send_json(message)
            return True
        except Exception:
            return False

    async def to_decks(self, message: dict) -> None:
        for websocket in list(self.decks):
            if not await self._send(websocket, message):
                self.decks.discard(websocket)

    async def to_controls(self, message: dict) -> None:
        self.last_state = message
        for websocket in list(self.controls):
            if not await self._send(websocket, message):
                self.controls.discard(websocket)


hub = Hub()


def _inject_deck_client(html: str) -> str:
    if DECK_CLIENT_SRC in html:
        return html
    tag = f'\t\t<script src="{DECK_CLIENT_SRC}" defer></script>\n'
    if "</body>" in html:
        return html.replace("</body>", tag + "\t</body>", 1)
    return html + "\n" + tag


def _serve_presentation_file(relative_path: str) -> FileResponse | HTMLResponse:
    if relative_path in ("", "/"):
        relative_path = "index.html"

    target = (PRESENTATION_DIR / relative_path).resolve()
    if not target.is_relative_to(PRESENTATION_DIR) or not target.is_file():
        raise HTTPException(status_code=404, detail="Not found")

    if target.suffix == ".html":
        return HTMLResponse(_inject_deck_client(target.read_text(encoding="utf-8")))

    media_type, _ = mimetypes.guess_type(str(target))
    return FileResponse(target, media_type=media_type)


@app.get("/")
async def control_panel() -> FileResponse:
    return FileResponse(STATIC_DIR / "control.html", media_type="text/html")


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "decks": len(hub.decks),
        "controls": len(hub.controls),
    }


@app.get("/presentation", response_model=None)
async def presentation_root():
    return _serve_presentation_file("index.html")


@app.get("/presentation/{relative_path:path}", response_model=None)
async def presentation_file(relative_path: str):
    return _serve_presentation_file(relative_path)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, role: str = "control") -> None:
    if role not in ("deck", "control"):
        role = "control"

    await websocket.accept()
    hub.register(websocket, role)

    if role == "control" and hub.last_state is not None:
        await websocket.send_json(hub.last_state)

    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict):
                continue
            message_type = message.get("type")

            if role == "control" and message_type == "command":
                action = message.get("action")
                if action in ALLOWED_ACTIONS:
                    await hub.to_decks({"type": "command", "action": action})
            elif role == "deck" and message_type == "state":
                state = {
                    "type": "state",
                    "indexh": int(message.get("indexh", 0)),
                    "indexv": int(message.get("indexv", 0)),
                    "current": int(message.get("current", 1)),
                    "total": int(message.get("total", 1)),
                }
                await hub.to_controls(state)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        hub.unregister(websocket, role)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000)
