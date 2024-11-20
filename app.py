from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['POST'])
def query_ollama():
    try:
        # Parse JSON payload
        data = request.get_json()
        prompt = data.get('prompt', '')

        # Validate input
        if not isinstance(prompt, str):
            return jsonify({'error': 'Prompt must be a string'}), 400

        logging.debug(f"Received prompt: {prompt}")

        # Run the subprocess command
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # Replace 'llama3.2' with your actual model name
            input=prompt.encode('utf-8'),   # Pass the prompt as bytes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Capture and log the subprocess output
        response = result.stdout.strip()
        logging.debug(f"Subprocess response: {response}")

        return jsonify({'response': response})

    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess error: {e.stderr}")
        return jsonify({'error': 'Failed to execute command', 'details': e.stderr.strip()}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
