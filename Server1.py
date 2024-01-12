import socket
import threading
import os
import sqlite3
import time

registered_clients = {}
identity_counter = 1
terminate_server = False

conn = sqlite3.connect('RegisteredClients.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Clients (
        identity INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        ip_address TEXT NOT NULL
    )
""")

cursor.execute("SELECT MAX(identity) FROM Clients")
result = cursor.fetchone()
identity_counter = (result[0] if result[0] is not None else 0) + 1

conn.commit()

def register_client(client_socket, client_address):
    global identity_counter

    conn = sqlite3.connect('RegisteredClients.db')
    cursor = conn.cursor()
    username = client_socket.recv(1024).decode('utf-8')
    time.sleep(0.1)  # Adds a small delay
    email = client_socket.recv(1024).decode('utf-8')
    cursor.execute("SELECT * FROM Clients WHERE email = ?", (email,))
    if cursor.fetchone() is not None:
        client_socket.send("Email already registered use another email".encode('utf-8'))
        return 
    else:
        client_socket.send("Registration successful".encode('utf-8')) 
        
    identity = identity_counter
    identity_counter += 1
    client_info = {
        'identity': identity,
        'username': username,
        'email': email,
        'ip_address': client_address[0]
    }
    registered_clients[identity] = client_info
    cursor.execute("INSERT INTO Clients VALUES (:identity, :username, :email, :ip_address)", client_info)
    conn.commit()
    conn.close()


def show_database():
    conn = sqlite3.connect('RegisteredClients.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clients")
    rows = cursor.fetchall()
    if rows:
        print("Registered Clients:")
        for row in rows:
            print(f"Identity: {row[0]}, Username: {row[1]}, Email: {row[2]}, IP: {row[3]}")
    else:
        print("NO REGISTRATIONS")
    conn.close()

def delete_registration():
    conn = sqlite3.connect('RegisteredClients.db')
    cursor = conn.cursor()
    identity = int(input("Enter the identity of the registration to delete: ").strip())
    cursor.execute("DELETE FROM Clients WHERE identity = ?", (identity,))
    conn.commit()
    print(f"Deleted registration with identity {identity}")
    conn.close()

def handle_command(command):
    global terminate_server
    if command == "ShowDataBase":
        show_database()
    elif command == "DeleteRegistration":
        delete_registration()
    elif command == "EXIT":
        terminate_server = True
        print("Server termination requested.")
        os._exit(0)

def input_loop():
    while True:
        user_input = input("Enter command : ").strip()
        if user_input in ["ShowDataBase", "EXIT","DeleteRegistration"]:
            handle_command(user_input)
        else:
            print("Invalid command. Please enter valid commands.")

def Login(client_socket, client_address):
    conn = sqlite3.connect('RegisteredClients.db')
    cursor = conn.cursor()
    username = client_socket.recv(1024).decode('utf-8')
    if username == "ADD_CONTACT":
        time.sleep(0.1)  # Adds a small delay
        email = client_socket.recv(1024).decode('utf-8')
        cursor.execute("SELECT * FROM Clients WHERE email = ?", (email,))
        result = cursor.fetchone()

        if result is None:
            client_socket.send("Not Registered! Please register first then Login".encode('utf-8'))
            return
        else:
            client_socket.send("Login successful".encode('utf-8'))
            ip_address = result[3]
            time.sleep(0.1)
            client_socket.send(ip_address.encode('utf-8'))
            
    else:
        time.sleep(0.1)  # Adds a small delay
        email = client_socket.recv(1024).decode('utf-8')
        cursor.execute("SELECT * FROM Clients WHERE email = ? AND username = ?", (email, username))
        user_record = cursor.fetchone()

        if user_record is None:
            client_socket.send("Not Registered! Please register first then Login".encode('utf-8'))
            return
        else:
            # Update the user's IP address
            cursor.execute("UPDATE Clients SET ip_address = ? WHERE email = ?", (client_address[0], email))
            conn.commit()

            client_socket.send("Login successful".encode('utf-8'))
    

def client_handler(client_socket, client_address):
    try:
        while True:
            option = client_socket.recv(1024).decode('utf-8')
            if option == "1":
                Login(client_socket, client_address)
            elif option == "2":
                register_client(client_socket, client_address)
        client_socket.close()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    host = "0.0.0.0"
    port = 20554

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Discovery server listening on {host}:{port}")
    print("Available commands: ShowDataBase, DeleteRegistration, EXIT")

    input_thread = threading.Thread(target=input_loop)
    input_thread.start()

    while True:
        if terminate_server:
            print("Terminating server...")
            break

        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()

    server_socket.close()

if __name__ == "__main__":
    main()
