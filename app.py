from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['POST'])
def query_ollama():
    try:
        # Get the JSON payload
        data = request.json
        prompt = data.get('prompt', '')

        # Log the input type and value
        logging.debug(f"Original prompt type: {type(prompt)}")
        logging.debug(f"Original prompt value: {prompt}")

        # Encode prompt to bytes explicitly
        if isinstance(prompt, str):
            prompt_bytes = prompt.encode('utf-8')
            logging.debug(f"Encoded prompt: {prompt_bytes}")
        else:
            return jsonify({'error': 'Prompt must be a string'}), 400

        # Run the subprocess command
        result = subprocess.run(
            ["echo"],  # Simplified for testing; replace with `ollama run llama3.2`
            input=prompt_bytes,
            capture_output=True,
            text=True
        )

        # Capture the output
        response = result.stdout.strip()
        logging.debug(f"Subprocess response: {response}")
        return jsonify({'response': response})

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
