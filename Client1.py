import socket
import threading
import multiprocessing
import time
import sqlite3

# Create a SQLite database for storing contacts
contact_db = sqlite3.connect('Contacts.db')
contact_cursor = contact_db.cursor()

contact_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Contacts (
        email TEXT PRIMARY KEY,
        ip_address TEXT NOT NULL
    )
""")

contact_db.commit()

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break

def send_message(client_socket, message):
    client_socket.send(message.encode('utf-8'))

def chat_server(client_name, input_queue, server_ip):
    host = "0.0.0.0"
    port = 8000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"{client_name} listening on {host}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input_queue.get()
        send_message(client_socket, f"{client_name}: {message}")

def Login(server_ip,client_email, client_name, option):
    while True:
        registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        registration_socket.connect((server_ip, 20554))
        registration_socket.send(option.encode('utf-8'))
        time.sleep(0.1)  # Adds a small delay
        registration_socket.send(client_name.encode('utf-8'))
        time.sleep(0.1)  # Adds a small delay
        registration_socket.send(client_email.encode('utf-8'))
        response = registration_socket.recv(1024).decode('utf-8')
        if response == "Not Registered! Please register first then Login":
            print(response)
            return False
        elif response == "Login successful":
            print(response)
            return True
    return False


def Register(server_ip,client_name,client_email, option):
    while True:
        registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        registration_socket.connect((server_ip, 20554))
        registration_socket.send(option.encode('utf-8'))
        time.sleep(0.1)  # Adds a small delay
        registration_socket.send(client_name.encode('utf-8'))
        time.sleep(0.1)  # Adds a small delay
        registration_socket.send(client_email.encode('utf-8'))
        time.sleep(0.1)
        response = registration_socket.recv(1024).decode('utf-8')
        if response == "Email already registered use another email":
            print(response)
            return None      
        elif response == "Registration successful":
            print(response)
            return client_name,client_email

def add_contact(server_ip, client_email):
    client_name = "ADD_CONTACT"
    contact_email = input("Enter the email address of the contact you want to add: ")
    contact_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    contact_socket.connect((server_ip, 20554))
    contact_socket.send("1".encode('utf-8'))  # Login option
    time.sleep(0.1)  # Adds a small delay
    contact_socket.send(client_name.encode('utf-8'))
    time.sleep(0.1)  # Adds a small delay
    contact_socket.send(contact_email.encode('utf-8'))
    time.sleep(0.1)
    response = contact_socket.recv(1024).decode('utf-8')
    if response == "Not Registered! Please register first then Login":
        print("The contact is not registered.")
    elif response == "Login successful":
        time.sleep(0.1)
        contact_address =contact_socket.recv(1024).decode('utf-8')
        contact_cursor.execute("INSERT INTO Contacts VALUES (?, ?)", (contact_email, contact_address))
        contact_db.commit()
        print("Contact added successfully.")

def show_contacts():
    contact_cursor.execute("SELECT * FROM Contacts")
    rows = contact_cursor.fetchall()
    if rows:
        print("Your Contacts:")
        for i, row in enumerate(rows):
            print(f"{i+1}. Email: {row[0]}, IP: {row[1]}")
    else:
        print("You have no contacts.")

def select_contact():
    show_contacts()
    contact_number = int(input("Select a contact to chat with: ")) - 1
    contact_cursor.execute("SELECT * FROM Contacts")
    rows = contact_cursor.fetchall()
    if 0 <= contact_number < len(rows):
        peer_ip = rows[contact_number][1]  # Return the IP address of the selected contact
        return peer_ip
    else:
        print("Invalid contact number.")
        return None

def chat_client(peer_ip, client_name,client_email, input_queue, server_ip):
    port = 8000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((peer_ip, port))
    except ConnectionRefusedError:
        print("Error: Connection refused. Make sure the server is running and the IP address is correct.")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input_queue.get()
        send_message(client_socket, f"{client_name}: {message}")

if __name__ == "__main__":
    #server_hostname =  'DESKTOP-3U1M5OC'
    #server_ip = socket.gethostbyname(server_hostname)
    server_ip = "15.207.21.63" 
    while True:
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        option = input("Select an option: ")

        if option == "1":
            client_name = input("Enter your name: ")
            client_email = input("Enter your email address: ")
            login_successful = Login(server_ip,client_email, client_name, option)

            if login_successful:
                while True:
                    print("1. Your Contacts")
                    print("2. Add Contact")
                    print("0. Back")
                    option = input("Select an option: ")

                    if option == "1":
                        while True:
                            print("1. Select a contact")
                            print("0. Back")
                            option = input("Select an option: ")
                            if option == "0":
                                break
                            elif option =="1":
                                peer_ip = select_contact()
                                if peer_ip == None:
                                    break
                                else:
                                    input_queue = multiprocessing.Queue()
                                    server_process = multiprocessing.Process(target=chat_server, args=(client_name, input_queue, server_ip))
                                    client_process = multiprocessing.Process(target=chat_client, args=(peer_ip, client_name,client_email, input_queue, server_ip))

                                    server_process.start()
                                    client_process.start()

                                    registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    registration_socket.connect((server_ip, 20554))
                                    registration_socket.send("1".encode('utf-8'))

                                    while True:
                                        message = input()
                                        input_queue.put(message)

                                    server_process.join()
                                    client_process.join()
                
                    elif option == "2":
                        while True:
                            print("1. Add a contact")
                            print("0. Back")
                            option = input("Select an option: ")
                            if option == "0":
                                break
                            elif option == "1":    
                                add_contact(server_ip, client_email)
                    elif option == "0":
                        break

        elif option == "2":
            client_name = input("Enter your name: ")
            client_email = input("Enter your email address: ")
            registration_successful = Register(server_ip, client_name, client_email, option)
            if registration_successful:
                print("Registration successful. You can now login.")
                continue
            else:
                print("Registration failed. Please try again.")
        elif option == "3":
            print("Exiting the program...")
            os._exit(0)
