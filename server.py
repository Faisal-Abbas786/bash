from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    client_name = request.headers.get('Client-Name', 'Unknown')
    client_ip = request.remote_addr
    return f'Client Name: {client_name}\nClient IP Address: {client_ip}'

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    print(f'Server running on http://{host}:{port}/')
    app.run(host=host, port=port)
