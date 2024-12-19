import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
load_dotenv()

class Reccomendation:
    def __init__(self, openai_api_key, spotify_client_id, spotify_client_secret, spotify_redirect_uri):
        # Set up OpenAI API
        openai.api_key = openai_api_key
        
        # Set up Spotify API
        self.spotipy_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri,
            scope="playlist-modify-private,playlist-modify-public"
        ))

    def get_song_recommendations(self, user_prompt):
        """Uses OpenAI to get song recommendations based on the user's input."""
        prompt = (
            f"Based on the following user input, recommend 25 of the best new songs. "
            f"Output the song names and artists only in the format 'Song - Artist'.\n\n"
            f"User input: {user_prompt}"
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a music recommendation assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            song_list = response.choices[0].message['content'].strip().split("\n")
            return song_list
        except Exception as e:
            print("Error fetching recommendations from OpenAI:", e)
            return []

    def create_playlist_and_add_songs(self, playlist_name, song_list):
        """Creates a new Spotify playlist and adds the given songs."""
        user_id = self.spotipy_client.me()['id']

        # Create a new playlist
        playlist = self.spotipy_client.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False  # Set to True if you want a public playlist
        )

        playlist_id = playlist['id']
        
        # Search and add songs to the playlist
        track_uris = []
        for song in song_list:
            try:
                query = song
                search_result = self.spotipy_client.search(q=query, type="track", limit=1)
                tracks = search_result.get('tracks', {}).get('items', [])
                if tracks:
                    track_uris.append(tracks[0]['uri'])
            except Exception as e:
                print(f"Error searching for song '{song}':", e)

        if track_uris:
            self.spotipy_client.playlist_add_items(playlist_id, track_uris)
        else:
            print("No songs were added to the playlist.")

        print(f"Playlist '{playlist_name}' created successfully!")
        return playlist_id

# Example usage
if __name__ == "__main__":
    openai_api_key = "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"
    spotify_client_id = "d668b508c7ed449ab5b9a6c58cd39914"
    spotify_client_secret = "acc78b28681c418ab3036e6f42788a7b"
    spotify_redirect_uri = "https://localhost.com/"

    assistant = Reccomendation(openai_api_key, spotify_client_id, spotify_client_secret, spotify_redirect_uri)

    user_prompt = "I want upbeat pop songs for a workout."
    song_recommendations = assistant.get_song_recommendations(user_prompt)

    if song_recommendations:
        playlist_name = "Workout Pop Songs"
        assistant.create_playlist_and_add_songs(playlist_name, song_recommendations)
