# Techical support vocie/chatbot AI Agent

This is the technical support voices and chat support assiatant.

## Features

- login/signup option for authentication
- Speech to text / user input by typing
- TTS : for text to speech / user will get response in text on UI
- Store the conversation history in sqldb
- Chatbot/agent should be history awared
- New session button to create a new session

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
