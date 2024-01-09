from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World! This is your Flask API.'

if __name__ == '__main__':
    app.run(host='192.168.18.49', port=1234)
