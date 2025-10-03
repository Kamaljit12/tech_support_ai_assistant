# Techical support vocie/chatbot AI Agent

This is the technical support voices and chat support assiatant.

## Features

- login/signup option for authentication
- Speech to text / user input by typing
- TTS : for text to speech / user will get response in text on UI
- Store the conversation history in sqldb like sqllight3
- Chatbot/agent should be history awared
- LLM ability and tools[duck-duck go] for web search
- New session button to create a new session

## High-level architecture

Client (web/mobile/voice device)

Records user audio, sends via WebSocket or REST to server.

Receives TTS audio to play back and streaming chat updates.

FastAPI backend

Endpoints: /stt, /tts, /chat (REST), and /ws (WebSocket for streaming/low-latency).

Manages sessions (JWT or session-id).

Stores conversation into SQL DB (Postgres/MySQL/SQLite).

LangChain + LangGraph agent

Uses an LLM for reasoning and generating responses.

Uses tools for web search and possibly code / DB queries.

Has memory integration that is stored/retrieved from the SQL DB per session.

Storage

SQL DB (Postgres recommended) to store sessions, messages, metadata, and embeddings (optional).

STT / TTS providers

Pluggable interfaces for whichever provider you prefer.

Tooling / infra

Docker-compose (FastAPI + Postgres), monitoring (Prometheus/Grafana), logging, rate-limiting, auth.

## Requirements

- speechRecognition # for STT
- pyttx3 # for TTS
- langgraph # To build agents
- langchain_core # To build tools and to give conversation and history aware ability
- groq # To access LLM model
- fastapi[standard] # to create API for each actions
- uvicorn[standard]
- chromadb # to store vectors
- duck-duck-go # Duck duck go tools to search web
