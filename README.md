# Transcribe
Created a simple voice-note app that records a user's voice, then transcribes it using
Whisper ASR model.
## API

### Create Virtual Environment
1. `cd api`
2. `python -m venv venv`
3. `source venv/bin/activate `

### Install Dependencies 
`pip install -r requirements.txt`

### Copy .env.example file and edit it

### Run API
`uvicorn main:app --reload --port 8000`

## Web

### Install Node
`npm install`

### Run Web
`npm run dev`
