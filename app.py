import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from CreatePlaylist import CreatePlaylist
from Reccomendation import Reccomendation
from UserPrompt import UserPrompt

# Retrieve credentials from environment variables
openai_api_key = os.getenv('OPEN_AI_KEY')
spotify_client_id = os.getenv('CLIENT_ID')
spotify_client_secret = os.getenv('ClIENT_SECRET')
spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

print("DEBUG:", spotify_client_id, spotify_client_secret, spotify_redirect_uri)  # Debug print

# Initialize the Reccomendation (assistant) object
assistant = Reccomendation(openai_api_key, spotify_client_id, spotify_client_secret, spotify_redirect_uri)

app = Flask(__name__)

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

    # CreatePlaylist requires a Spotify client. We can pass assistant.spotipy_client to it.
    creator = CreatePlaylist(prompt, assistant.spotipy_client)
    success = creator.create_playlist_from_saved_tracks(playlist_name, assistant)

    if success:
        return jsonify({"message": f"Playlist '{playlist_name}' created successfully!"})
    else:
        return jsonify({"error": "No recommendations could be retrieved."}), 500

if __name__ == '__main__':
    app.run(debug=True)
