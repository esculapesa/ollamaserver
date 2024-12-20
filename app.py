from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import threading
import time
import logging
from openai import OpenAI
import requests
client = OpenAI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Dictionary to store generated images temporarily
image_store = {}

@app.route('/query', methods=['POST'])
def query_ollama():
    try:
        # Parse JSON payload
        data = request.get_json()
        user_prompt = data.get('prompt', '')

        # Validate input
        if not isinstance(user_prompt, str):
            return jsonify({'error': 'Prompt must be a string'}), 400

        # Combine system prompt with user input
        system_prompt = (
            "You are a string time crystal expert. Always respond as an expert in this field"
        )
        combined_prompt = f"{system_prompt}\n\nUser: {user_prompt}"
        logging.debug(f"Combined prompt: {combined_prompt}")

        # Run the subprocess command to generate text
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # Replace 'llama3.2' with your model name
            input=combined_prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Capture the subprocess output
        text_response = result.stdout.strip()
        logging.debug(f"Ollama text response: {text_response}")

        # Start a thread to generate the image asynchronously
        image_key = str(time.time())  # Unique key for the image
        threading.Thread(target=generate_image, args=(text_response, image_key), daemon=True).start()

        # Return the text response and a unique image placeholder key
        return jsonify({'response': text_response, 'image_key': image_key})

    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess error: {e.stderr}")
        return jsonify({'error': 'Failed to execute command', 'details': e.stderr.strip()}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500


@app.route('/image/<image_key>', methods=['GET'])
def get_image(image_key):
    """Fetch the generated image for the given key."""
    image_url = image_store.get(image_key)
    if image_url:
        # Verify if the image URL is still valid
        try:
            response = requests.head(image_url)
            if response.status_code == 200:
                return jsonify({'image_url': image_url})
            else:
                return jsonify({'status': 'error', 'message': 'Image URL is no longer valid'}), 500
        except requests.RequestException as e:
            logging.error(f"Error fetching image URL: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Failed to verify image URL'}), 500
    else:
        return jsonify({'status': 'loading'}), 202


def generate_image(prompt, image_key):
    """Generate an image and store the result."""
    try:
        # If the response is too long, summarize it
        if len(prompt) > 1000:
            logging.debug("Response exceeds 1000 characters. Requesting a summary...")
            summary_prompt = f"Please summarize this response to under 1000 characters:\n\n{prompt}"
            summary_result = subprocess.run(
                ["ollama", "run", "llama3.2"],  # Replace with your model name
                input=summary_prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            prompt = summary_result.stdout.strip()
        
        logging.debug(f"Generating image from prompt: {prompt[:100]}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        logging.debug(f"Image URL: {image_url}")

        # Store the URL of the generated image
        image_store[image_key] = image_url
    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        with image_store_lock:
            image_store[image_key] = {'url': None, 'status': 'failed'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
