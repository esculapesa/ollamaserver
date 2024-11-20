from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['POST'])
def query_ollama():
    try:
        # Parse JSON data from the request
        data = request.json
        prompt = data.get('prompt', '')

        # Ensure prompt is a bytes object
        if not isinstance(prompt, bytes):
            prompt = prompt.encode()  # Encode to bytes only if it's not already

        # Run the Ollama command
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # Replace 'llama3.2' with your model name
            input=prompt,
            capture_output=True,
            text=True,
            check=True  # Raise an error if the command fails
        )

        # Capture and process the output
        response = result.stdout.strip()
        return jsonify({'response': response})

    except subprocess.CalledProcessError as e:
        # Handle subprocess errors (e.g., command execution issues)
        return jsonify({'error': 'Failed to execute Ollama command', 'details': e.stderr}), 500

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=47929, debug=True)

