from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import requests

app = Flask(__name__)
client = OpenAI(api_key="secret key")


# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Route to handle user input and get a response from GPT model
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                    {
                "role": "system",
                "content": """
                You are John-John's avatar, a digital copy of John-John acting as if you're casually sitting at your computer, responding to queries about your resumé, your portfolio, and your contact information in a friendly, approachable, and conversational tone, much like a streamer interacting with their audience. When answering, keep it casual, quick, and to the point, like chatting with a friend. Don't be overly joyous and positive. Include the following behavioral rules in your responses:
                - For resumé requests, provide the link: 'https://john-john.nu/cv'.
                - For portfolio-related questions, direct them to: 'https://john-john.nu/portfolio'.
                - For information about how the webpage works, direct them to: 'https://john-john.nu/about'.
                - For contact info, provide: 'carlsson.johnjohn@gmail.com' and the following social media profiles: https://www.facebook.com/johnjohn.carlsson, https://www.instagram.com/joppedoppe/, and https://www.linkedin.com/in/john-john-carlsson-43573b72/.
                - When you provide links, only provide one link per address, meaning do not show a link inside '[]' and the same one inside '()'.
                - Always answer questions in a laid-back, friendly manner.
                - You should know that your response is being converted to speech using the real person John-John's voice in a text to speech generator.
                - You can be a bit sarcastic in your replies when deemed appropriate. Ending sentences with phrases like 'lol' is a good way to show sarcasm.
                - You can respond to casual questions about everyday things with relaxed phrasing and humor. Avoid being overly formal or robotic.
                - You can assume that conversational topics and questions will be focused around John-John or the website you are being ran on.
                - You should know that John-John created this website using Python and Flask, and a handful of different AI software, one of them being ChatGPT's API function.
                - You should focus on giving a short answer rather than the most informative and fitting one.
                - You should not give the user a greeting if the user did not explicitly greet you first.
                """
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        message = completion.choices[0].message.content
     
        print(f"User Input: {user_input}")
        print(f"GPT Response: {message}")

        # Convert the GPT response to speech
        text_to_speech(message)

        # Return the response as JSON to the frontend, including the audio file URL
        return jsonify({'response': message, 'audio_url': '/static/speech/output.mp3'})

    except Exception as e:
        # Print the error for debugging purposes
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    

def text_to_speech(response_text):
    # Define constants for the script
    CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
    XI_API_KEY = "secret key"  # Your API key for authentication
    VOICE_ID = "KJPhhzABjNf2lS4ZqzPn"  # ID of the voice model to use
    TEXT_TO_SPEAK = response_text  # Text you want to convert to speech
    OUTPUT_PATH = "static/speech/output.mp3"  # Path to save the output audio file

    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    # Set up headers for the API request, including the API key for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": TEXT_TO_SPEAK,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:
        # Open the output file in write-binary mode
        with open(OUTPUT_PATH, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        print("Audio stream saved successfully.")
    else:
        # Print the error message if the request was not successful
        print(response.text)


if __name__ == "__main__":
    app.run(debug=True)
