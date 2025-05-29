from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    with open("gazeData.json", "w") as f:
        json.dump(data, f)
    return "✅ Gaze data received!"

if __name__ == "__main__":
    app.run(debug=True)
