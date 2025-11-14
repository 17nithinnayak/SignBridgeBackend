import json
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import io
from pydub import AudioSegment

# --- 1. Load All Models & Data on Startup ---
print("Loading data and models...")

# --- Load the Whisper model ---
# We use "tiny.en" - it's fast and perfect for a hackathon.
WHISPER_MODEL = whisper.load_model("tiny.en")
print("Successfully loaded Whisper model 'tiny.en'")

# --- Global "Brains" of the App ---
WORD_MAP = {}
ALPHABET_MAP = {}
NUMBER_MAP = {}

app = FastAPI(
    title="SignBridge Backend",
    description="Handles real-time sign language translation.",
    version="1.0.0"
)

# --- Add CORS Middleware ---
# This lets your website (on a different domain) talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- 2. Load Translation Maps on Startup ---
@app.on_event("startup")
def load_data():
    """Load the translation maps from JSON files when the server starts."""
    global WORD_MAP, ALPHABET_MAP, NUMBER_MAP
    
    try:
        with open("words.json", "r") as f:
            WORD_MAP = json.load(f)
        print(f"Successfully loaded {len(WORD_MAP)} words.")
    except FileNotFoundError:
        print("WARNING: 'words.json' not found. Word lookup will be empty.")
    
    try:
        with open("alphabet.json", "r") as f:
            ALPHABET_MAP = json.load(f)
        print(f"Successfully loaded {len(ALPHABET_MAP)} alphabet letters.")
    except FileNotFoundError:
        print("WARNING: 'alphabet.json' not found. Spelling fallback will fail.")

    try:
        with open("numbers.json", "r") as f:
            NUMBER_MAP = json.load(f)
        print(f"Successfully loaded {len(NUMBER_MAP)} numbers.")
    except FileNotFoundError:
        print("INFO: 'numbers.json' not found. Number lookup will be empty.")

# --- 3. The "Smart Translator" Logic ---
async def get_translation_urls(text: str) -> list[str]:
    """
    Processes text and returns a list of video URLs.
    Tries words, then numbers, then falls back to spelling.
    """
    urls_to_play = []
    # Clean the text of common punctuation
    cleaned_text = text.lower().strip(" .,?!")
    words = cleaned_text.split()

    for word in words:
        if word in WORD_MAP:
            urls_to_play.append(WORD_MAP[word])
        elif word in NUMBER_MAP:
            urls_to_play.append(NUMBER_MAP[word])
        else:
            # Word not found. Fallback to spelling
            print(f"Word not found: '{word}'. Falling back to spelling.")
            for char in word:
                if char in ALPHABET_MAP:
                    urls_to_play.append(ALPHABET_MAP[char])
                else:
                    print(f"Skipping unknown char: '{char}'")
    
    return urls_to_play

# --- 4. WebSocket Endpoint (For Chrome Extension) ---
@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Chrome Extension connected.")
    try:
        while True:
            # 1. Receive the FINAL transcript text (not bytes)
            transcript_text = await websocket.receive_text()

            if transcript_text:
                print(f"Transcript received: '{transcript_text}'")

                # 2. Send the transcript back for subtitles
                await websocket.send_json({"type": "transcript", "data": transcript_text})

                # 3. Get URLs instantly
                urls = await get_translation_urls(transcript_text)
                if urls:
                    print(f"Sending {len(urls)} URLs to extension...")
                    for url in urls:
                        await websocket.send_json({"type": "video", "data": url})

    except WebSocketDisconnect:
        print("Client disconnected.")

# --- 5. HTTP Endpoints (For Website Team & Swagger) ---

# This is the one that will show up in Swagger UI
@app.post("/api/translate-text", summary="Translate Text to Sign URLs")
async def http_translate_text(data: dict):
    """
    Takes a JSON with {"text": "Hello 123"} and returns a list of
    video URLs for the website to play.
    """
    text = data.get("text", "")
    if not text:
        return {"urls": []}
    
    urls = await get_translation_urls(text)
    print(f"Sending {len(urls)} URLs to website.")
    return {"urls": urls}

@app.get("/api/generate-quiz", summary="Generate a 4-Option Sign Language Quiz")
async def generate_quiz():
    """
    Picks a random video from the 'words' list and returns it,
    along with 3 incorrect options, to build a quiz.
    """
    word_list = list(WORD_MAP.keys())
    
    # Handle case where there are fewer than 4 words
    if len(word_list) < 4:
        return {"error": "Not enough words in the dictionary to generate a quiz."}
        
    quiz_options = random.sample(word_list, 4)
    correct_answer = quiz_options[0]
    video_url = WORD_MAP[correct_answer]
    random.shuffle(quiz_options)
    
    return {
        "video_url": video_url,
        "options": quiz_options,
        "correct_answer": correct_answer
    }

# This is the root (homepage) endpoint
@app.get("/", summary="Check Backend Status")
def read_root():
    """A simple endpoint to check if the server is running."""
    return {"status": "SignBridge Backend is running!"}
