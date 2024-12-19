class CreatePlaylist:
    def __init__(self, prompt, client):
        self.userInput = prompt
        self.client = client  # This should be a Spotipy client instance

    def getSavedTracks(self):
        tracks = self.client.current_user_saved_tracks(limit=50)
        track_list = []
        for item in tracks['items']:
            track = item['track']
            track_list.append(f"{track['name']} - {track['artists'][0]['name']}")
        return track_list

    def createPrompt(self):
        saved_tracks = self.getSavedTracks()
        track_text = "\n".join(saved_tracks)
        prompt = f"Give me 50 more songs that are similar to these tracks:\n{track_text}\nFormat the output as 'Song - Artist'."
        return prompt

    def create_playlist_from_saved_tracks(self, playlist_name, assistant):
        # Generate the prompt from saved tracks
        prompt = self.createPrompt()

        # Get recommendations using the assistant (Reccomendation instance)
        recommended_songs = assistant.get_song_recommendations(prompt)

        # Create playlist and add songs
        if recommended_songs:
            assistant.create_playlist_and_add_songs(playlist_name, recommended_songs)
            return True
        else:
            print("No recommendations could be retrieved.")
            return False

