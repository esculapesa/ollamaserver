from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging
import requests
import base64
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Define the system prompt
SYSTEM_PROMPT = "You are a string time crystal expert. Always respond as an expert in this field."

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
        combined_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_prompt}"
        logging.debug(f"Combined prompt: {combined_prompt}")

        # Run the text subprocess command
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # Replace 'llama3.2' with your actual model name
            input=combined_prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Capture and log the text subprocess output
        text_response = result.stdout.strip()
        logging.debug(f"Subprocess text response: {text_response}")

        # Generate an image using DALL·E or other API
        image_url = generate_image(text_response)

        return jsonify({'response': text_response, 'image_url': image_url})

    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess error: {e.stderr}")
        return jsonify({'error': 'Failed to execute command', 'details': e.stderr.strip()}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500


def generate_image(prompt):
    """Generate an image based on the text response."""
    try:
        # Replace with the image generation API of your choice
        # Example: Using DALL·E or Stable Diffusion API
        response = requests.post(
            "https://api.openai.com/v1/images/generations",  # Example for DALL·E
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
            },
            json={
                "prompt": prompt,
                "n": 1,
                "size": "512x512"
            }
        )
        response.raise_for_status()
        image_data = response.json()

        # Return the URL of the generated image
        return image_data["data"][0]["url"]
    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
