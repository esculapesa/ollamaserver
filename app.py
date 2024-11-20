from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['POST'])
def query_ollama():
    try:
        data = request.json
        prompt = data.get('prompt', '')

        # Log the original prompt type and value
        logging.debug(f"Original prompt type: {type(prompt)}")
        logging.debug(f"Original prompt value: {prompt}")

        # Ensure prompt is a string and encode it once to bytes
        if not isinstance(prompt, bytes):  # Only encode if it's not already bytes
            logging.debug("Prompt is a string, encoding to bytes...")
            prompt = prompt.encode('utf-8')
        else:
            logging.debug("Prompt is already bytes, no encoding needed.")

        # Run the subprocess command
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # Replace with your model name
            input=prompt,
            capture_output=True,
            text=True,
            check=True
        )

        # Process the output
        response = result.stdout.strip()
        logging.debug(f"Ollama response: {response}")
        return jsonify({'response': response})

    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess error: {e.stderr}")
        return jsonify({'error': 'Failed to execute Ollama command', 'details': e.stderr}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
