# SignBridge Backend

This repository contains the backend server for SignBridge, a real-time sign language translation application. Built with FastAPI, this server provides a robust API to convert text into a sequence of corresponding sign language video URLs. It is designed to support both a web application and a Chrome extension.

## Core Functionality

The primary function of this backend is to act as a "smart translator." When it receives a string of text, it processes it and returns a list of video URLs that represent the text in sign language.

The translation logic follows a specific hierarchy:
1.  **Direct Word Match**: The input text is split into words. Each word is checked against a comprehensive `words.json` dictionary.
2.  **Number Match**: If a word is not found in the word dictionary, it's checked against the `numbers.json` map.
3.  **Character Fallback**: If a word is not found in either dictionary, the system defaults to spelling the word out character by character, using the `alphabet.json` mapping.

This ensures that any text can be translated, either through whole words or by spelling.

## Features

- **FastAPI Framework**: A modern, high-performance web framework for building APIs.
- **WebSocket Support**: Provides a real-time, low-latency communication channel for the SignBridge Chrome Extension.
- **REST API**: Offers standard HTTP endpoints for web clients.
- **Modular Vocabulary**: Sign language vocabulary is managed through simple JSON files (`words.json`, `numbers.json`, `alphabet.json`), making it easy to update and expand.
- **Quiz Generation**: An endpoint to dynamically create multiple-choice quizzes to help users learn and practice sign language.

## Getting Started

Follow these instructions to set up and run the backend server on your local machine.

### Prerequisites

- Python 3.8+
- [Git](https://git-scm.com/)

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/17nithinnayak/SignBridgeBackend.git
    cd SignBridgeBackend
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    The project uses PyTorch for the Whisper model. The `requirements.txt` file is configured to install the CPU version.
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the server:**
    ```sh
    uvicorn main:app --reload
    ```
    The server will start and be accessible at `http://127.0.0.1:8000`.

## API Endpoints

The server exposes several endpoints. You can view interactive documentation by navigating to `http://127.0.0.1:8000/docs` while the server is running.

### `GET /`
- **Summary**: Check Backend Status
- **Description**: A simple endpoint to verify that the server is running correctly.
- **Response**:
    ```json
    {
      "status": "SignBridge Backend is running!"
    }
    ```

### `POST /api/translate-text`
- **Summary**: Translate Text to Sign URLs
- **Description**: Takes a JSON object with text and returns a list of video URLs for a web client to play.
- **Request Body**:
    ```json
    {
      "text": "hello world"
    }
    ```
- **Response**:
    ```json
    {
      "urls": [
        "https://cdn.jsdelivr.net/gh/17nithinnayak/signbridge-assets@main/Words/Hello.mp4",
        "https://cdn.jsdelivr.net/gh/17nithinnayak/signbridge-assets@main/Words/World.mp4"
      ]
    }
    ```

### `GET /api/generate-quiz`
- **Summary**: Generate a 4-Option Sign Language Quiz
- **Description**: Returns a random sign language video, a list of four possible word options, and the correct answer.
- **Response**:
    ```json
    {
      "video_url": "https://cdn.jsdelivr.net/gh/17nithinnayak/signbridge-assets@main/Words/Happy.mp4",
      "options": [
        "sad",
        "happy",
        "go",
        "work"
      ],
      "correct_answer": "happy"
    }
    ```

### `WS /ws/translate`
- **Summary**: Real-time Translation via WebSocket
- **Description**: Establishes a WebSocket connection, typically with a Chrome extension. The backend listens for transcribed text and sends back video URLs as they are processed.
- **Client to Server Message** (Text):
    ```
    "This is a test"
    ```
- **Server to Client Messages** (JSON):
    The server first sends the received transcript back for subtitle display, then sends a stream of video URLs.
    ```json
    {"type": "transcript", "data": "This is a test"}
    ```
    ```json
    {"type": "video", "data": "https://.../This.mp4"}
    {"type": "video", "data": "https://.../I.mp4"}
    {"type": "video", "data": "https://.../S.mp4"}
    {"type": "video", "data": "https://.../A.mp4"}
    {"type": "video", "data": "https://.../T.mp4"}
    {"type": "video", "data": "https://.../E.mp4"}
    {"type": "video", "data": "https://.../S.mp4"}
    {"type": "video", "data": "https://.../T.mp4"}
