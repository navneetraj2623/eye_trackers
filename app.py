from flask import Flask, render_template, request
import json
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    with open("gazeData.json", "w") as f:
        json.dump(data, f) 
subprocess.run(["python", "analysis.py"])
    
if __name__ == "__main__":
    app.run(debug=True)
