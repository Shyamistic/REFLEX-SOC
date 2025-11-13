from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def hello():
    subprocess.Popen(['sleep', '30'])
    return 'Spawned a 30-second child!'


if __name__ == '__main__':
    app.run(debug=False, port=5000)
