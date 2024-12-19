import openai

class UserPrompt:
    def __init__(self, prompt, api_key):
        self.userInput = prompt
        self.categories = [
            'song recommendation', 
            'album recommendation', 
            'artist recommendation', 
            'playlist recommendation', 
            'spotify wrapped'
        ]
        self.client = openai
        self.api_key = api_key
        openai.api_key = self.api_key  # Set the API key

    def compilePrompt(self):
        res = ', '.join(self.categories)
        gptPrompt = (
            f"Which category in this list {res} does this prompt belong to: {self.userInput} "
            f"NOTE: just output the category that this prompt belongs to, don't output anything else."
        )
        return gptPrompt

    def identifyCategorie(self):
        message = self.compilePrompt()
        completion = self.client.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Spotify assistant."},
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.content.strip()
