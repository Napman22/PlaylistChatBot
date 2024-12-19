import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from CreatePlaylist import CreatePlaylist
from Reccomendation import Reccomendation
from UserPrompt import UserPrompt

# Retrieve credentials from environment variables
openai_api_key = os.getenv('OPEN_AI_KEY')
spotify_client_id = os.getenv('CLIENT_ID')
spotify_client_secret = os.getenv('ClIENT_SECRET')
spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')

# Initialize the Reccomendation (assistant) object
assistant = Reccomendation(openai_api_key, spotify_client_id, spotify_client_secret, spotify_redirect_uri)

app = Flask(__name__)

@app.route('/ui', methods=['GET'])
def ui():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>App Navigation</title>
    <style>
        body {
            font-family: Arial, sans-serif; 
            margin: 20px;
        }
        h1, h2 {
            font-weight: normal;
        }
        .section {
            margin-bottom: 40px;
        }
        input, textarea {
            display: block; 
            margin: 10px 0;
            width: 300px;
        }
        button {
            padding: 10px;
        }
        #results {
            margin-top: 20px;
            border: 1px solid #ccc; 
            padding: 10px; 
            width: 80%; 
            background: #f9f9f9;
        }
    </style>
</head>
<body>
    <h1>App Navigation</h1>
    <p>Use the links and forms below to interact with the app.</p>

    <div class="section">
        <h2>Identify Category (Frontend Demo)</h2>
        <p><a href="/frontend" target="_blank">Go to Identify Category Frontend</a></p>
    </div>

    <div class="section">
        <h2>Recommend Songs</h2>
        <p>Enter a prompt, and the app will recommend songs (using POST /recommend_songs):</p>
        <form id="recommend-form">
            <label for="rec-prompt">Prompt:</label>
            <input type="text" id="rec-prompt" placeholder="e.g. 'I want upbeat pop songs for a workout'">
            <button type="submit">Get Recommendations</button>
        </form>
        <div id="rec-results"></div>
    </div>

    <div class="section">
        <h2>Create Playlist From Saved Tracks</h2>
        <p>Enter a playlist name and a prompt, and the app will create a playlist (using POST /create_playlist_from_saved):</p>
        <form id="playlist-form">
            <label for="playlist-name">Playlist Name:</label>
            <input type="text" id="playlist-name" placeholder="e.g. 'My New Playlist'">

            <label for="playlist-prompt">Prompt:</label>
            <input type="text" id="playlist-prompt" placeholder="e.g. 'I want upbeat pop songs for a workout.'">

            <button type="submit">Create Playlist</button>
        </form>
        <div id="playlist-results"></div>
    </div>

    <script>
        // Handle Recommend Songs POST request
        document.getElementById('recommend-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const prompt = document.getElementById('rec-prompt').value;
            const response = await fetch('/recommend_songs', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prompt: prompt })
            });
            const data = await response.json();
            const resultDiv = document.getElementById('rec-results');
            resultDiv.innerHTML = '<h3>Recommendations:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
        });

        // Handle Create Playlist POST request
        document.getElementById('playlist-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const playlistName = document.getElementById('playlist-name').value;
            const playlistPrompt = document.getElementById('playlist-prompt').value;
            const response = await fetch('/create_playlist_from_saved', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ playlist_name: playlistName, prompt: playlistPrompt })
            });
            const data = await response.json();
            const resultDiv = document.getElementById('playlist-results');
            resultDiv.innerHTML = '<h3>Playlist Creation:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
        });
    </script>
</body>
</html>
'''

@app.route('/frontend', methods=['GET'])
def frontend():
    return '''
<html>
<head><title>Front-End Test</title></head>
<body>
<h1>Identify Category</h1>
<form id="category-form">
    <input type="text" id="prompt" placeholder="Enter your prompt" style="width:300px;" />
    <button type="submit">Identify Category</button>
</form>
<div id="result" style="margin-top:20px;"></div>

<script>
document.getElementById('category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = document.getElementById('prompt').value;
    const response = await fetch('/identify_category', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ prompt: prompt })
    });
    const data = await response.json();
    document.getElementById('result').innerText = 'Category: ' + JSON.stringify(data);
});
</script>
</body>
</html>
'''

@app.route('/identify_category', methods=['POST'])
def identify_category():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400

    prompt = data['prompt']
    user_prompt = UserPrompt(prompt, openai_api_key)
    category = user_prompt.identifyCategorie()
    return jsonify({"category": category})

@app.route('/recommend_songs', methods=['POST'])
def recommend_songs():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400

    prompt = data['prompt']
    songs = assistant.get_song_recommendations(prompt)
    return jsonify({"songs": songs})

@app.route('/create_playlist_from_saved', methods=['POST'])
def create_playlist_from_saved():
    data = request.get_json()
    if not data or 'playlist_name' not in data or 'prompt' not in data:
        return jsonify({"error": "Please provide 'playlist_name' and 'prompt'"}), 400

    playlist_name = data['playlist_name']
    prompt = data['prompt']

    creator = CreatePlaylist(prompt, assistant.spotipy_client)
    success = creator.create_playlist_from_saved_tracks(playlist_name, assistant)

    if success:
        return jsonify({"message": f"Playlist '{playlist_name}' created successfully!"})
    else:
        return jsonify({"error": "No recommendations could be retrieved."}), 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/', methods=['GET'])
def home():
    return "Welcome! Navigate to /ui for the main navigation page.", 200