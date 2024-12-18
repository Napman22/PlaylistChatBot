4import openai

class UserPrompt:

    def __init__(self, prompt, api_key):
        self.userInput = prompt
        self.categories = ['song recommendation', 'album recommendation', 'artist recommendation', 'playlist recommendation', 'spotify wrapped']
        self.client = openai
        self.api_key = api_key
        openai.api_key = self.api_key  # Set the API key

    def compilePrompt(self):
        temp = self.categories
        res = ', '.join(self.categories)  # Use a clearer separator
        gptPrompt = f"Which category in this list {res} does this prompt belong to: {self.userInput} NOTE: just output the category that this prompt belongs to, don't output anything else."
        return gptPrompt

    def identifyCategorie(self):
        message = self.compilePrompt()
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Spotify assistant."},
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.content


api_key = "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"
prompt = "Recommend me a good playlist for studying."
user_prompt = UserPrompt(prompt, api_key)
category = user_prompt.identifyCategorie()
print("Category:", category)