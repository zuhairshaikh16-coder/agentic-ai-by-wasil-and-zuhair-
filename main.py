"""
main.py
-------

Web server for the AI agent.

This file is the bridge between:

    Browser
       ↓
    FastAPI
       ↓
    agent.py
       ↓
    OpenRouter + tools.py
       ↓
    AI response
       ↓
    Browser

IMPORTANT:
-----------
The actual AI agent remains inside agent.py.

This file does NOT implement the agent logic.
It only exposes the existing agent through HTTP endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import Agent


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="My Agentic AI",
    description="Web interface for my agentic AI system",
    version="1.0.0",
)


# ============================================================
# WEB FRONTEND
# ============================================================
#
# FastAPI will serve:
#
#     web/index.html
#     web/style.css
#     web/script.js
#
# through:
#
#     /static/...
#
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="web"),
    name="static",
)


# ============================================================
# AGENT SESSIONS
# ============================================================
#
# Each browser gets its own session ID.
#
# Example:
#
# User A
#     ↓
# session-123
#     ↓
# Agent A
#
# User B
#     ↓
# session-456
#     ↓
# Agent B
#
# This prevents their conversations from being mixed.
#
# NOTE:
# This is suitable for local development and testing.
# For production, use a persistent session/database system.
# ============================================================

agents = {}


# ============================================================
# REQUEST MODELS
# ============================================================


class ChatRequest(BaseModel):
    """
    Data sent from the browser to the backend.
    """

    session_id: str
    message: str


class ChatResponse(BaseModel):
    """
    Data returned from the backend to the browser.
    """

    response: str


# ============================================================
# HOME PAGE
# ============================================================


@app.get("/")
async def home():
    """
    Serve the main HTML page.
    """

    return FileResponse(
        "web/index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================


@app.get("/health")
async def health():
    """
    Simple endpoint used to check whether
    the server is alive.
    """

    return {
        "status": "ok",
        "agent": "online",
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================


@app.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):
    """
    Send a user message to the existing AI agent.

    Browser:
        POST /chat

    Example request:

        {
            "session_id": "abc123",
            "message": "Calculate 25 * 48"
        }

    The existing Agent.run() method handles:
        THINK
        ACT
        OBSERVE
        FINAL ANSWER
    """

    session_id = request.session_id.strip()

    message = request.message.strip()


    # --------------------------------------------------------
    # Validate session
    # --------------------------------------------------------

    if not session_id:

        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )


    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )


    # --------------------------------------------------------
    # Create an Agent for this session
    # --------------------------------------------------------

    if session_id not in agents:

        agents[session_id] = Agent()


    agent = agents[session_id]


    # --------------------------------------------------------
    # Run the existing agent
    # --------------------------------------------------------

    try:

        answer = agent.run(
            message,
            verbose=False
        )


    except Exception as e:

        print(
            f"Agent error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI agent encountered an error."
            )
        )


    # --------------------------------------------------------
    # Return response to browser
    # --------------------------------------------------------

    return ChatResponse(
        response=answer
    )


# ============================================================
# CLEAR CHAT
# ============================================================


@app.post("/clear")
async def clear_chat(
    request: ChatRequest
):
    """
    Delete the current agent session.

    This effectively starts a fresh conversation.
    """

    session_id = request.session_id.strip()


    if session_id in agents:

        del agents[session_id]


    return {
        "success": True,
        "message": "Conversation cleared."
    }