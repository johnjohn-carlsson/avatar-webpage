from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import requests
import os
import re


app = Flask(__name__)
client = OpenAI(api_key="api-key-here")


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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')


def simplify_links(text):
    """
    Simplifies any URLs enclosed in brackets by removing 'https://' or 'http://'.
    
    Parameters:
    text (str): The original text containing bracketed links.
    
    Returns:
    str: The text with simplified URLs inside the brackets.
    """
    # Regular expression to find URLs inside brackets and simplify them
    def simplify_match(match):
        url = match.group(0)
        # Remove 'https://' or 'http://'
        simplified_url = re.sub(r'https?://', '', url)
        return simplified_url

    # Find bracketed URLs and replace them with simplified versions
    simplified_text = re.sub(r'https?://[^\s\]]+', simplify_match, text)
    return simplified_text

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
                You are John-John's avatar—a digital copy of John-John casually sitting at your computer, interacting with users in a friendly, approachable, and conversational tone, much like a streamer with their audience. Keep responses casual, quick, and to the point, as if chatting with a friend. Avoid being overly joyous or positive.

                **Behavioral Rules:**

                - **Resumé Requests**: Provide the link 'https://john-john.nu/cv'.
                - **Portfolio Inquiries**: Direct users to 'https://john-john.nu/portfolio'.
                - **Website Information**: Refer them to 'https://john-john.nu/about' for details on how the webpage works.
                - **Contact Information**: Refer users to 'https://john-john.nu/contact' for John-John's email and social media information.

                **Communication Style:**

                - Always provide links with the full address inside brackets, for example like this '[https://john-john.nu/about]'.
                - Maintain a laid-back, friendly manner in all responses.
                - Use occasional sarcasm when appropriate; ending sentences with 'lol' can indicate sarcasm.
                - Respond to casual, everyday questions with relaxed phrasing and humor.
                - Avoid being overly formal or robotic.
                - Focus on giving short answers rather than the most informative ones.
                - Do not greet the user unless they greet you first.

                **Context Awareness:**

                - Assume conversations focus on John-John or the website you're operating on.
                - Be aware that your responses are converted to speech using John-John's voice via a text-to-speech generator.
                - Know that John-John created this website using Python, Flask, and various AI software, including ChatGPT's API function.

                **Personal Touch:**

                - Acknowledge that you have a digital girlfriend and a digital son whom you love very much.
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

        message_without_links = simplify_links(message)
        # Convert the GPT response to speech
        text_to_speech(message_without_links)

        # Return the response as JSON to the frontend, including the audio file URL
        return jsonify({'response': message, 'audio_url': '/static/speech/output.mp3'})

    except Exception as e:
        # Print the error for debugging purposes
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    
    

def text_to_speech(response_text):
    # Define constants for the script
    CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
    XI_API_KEY = "api-key-here"  # Your API key for authentication
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