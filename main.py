from flask import Flask, render_template, request, jsonify
import hashlib
import random as rnd
import requests 
import sys, signal, os
import threading, time
from getpass import getpass
import argparse

import flask.cli
flask.cli.show_server_banner = lambda *args: None

import logging
log = logging.getLogger('werkzeug')
log.disabled = True

uid = rnd.randint(-1000000000, 100000000)
app = Flask(__name__)

app.logger.disabled = True

# Global variables for storing state
class State:
    attempts = 0
    original_message = ""
    encrypted_message = ""
    original_key = ""
    original_hash = ""

state = State()
stop = False

def vigenere_encrypt(message, key):
    encrypted = []
    key_length = len(key)
    for i, char in enumerate(message):
        shift = ord(key[i % key_length])  # Use the key character code directly
        encrypted.append(chr((ord(char) + shift) % 0x110000))  # 0x110000 - maximum character code in Unicode
    return ''.join(encrypted)

def vigenere_decrypt(encrypted, key):
    decrypted = []
    key_length = len(key)
    for i, char in enumerate(encrypted):
        shift = ord(key[i % key_length])  # Use the key character code directly
        decrypted.append(chr((ord(char) - shift) % 0x110000))  # 0x110000 - maximum character code in Unicode
    return ''.join(decrypted)

@app.route('/')
def index():
    global stop
    # print(f"Index called: Encrypted Message: {state.encrypted_message}, Attempts: {state.attempts}")
    if state.attempts >= 3:
        stop = True
        # requests.post('http://127.0.0.1:5000/shutdown', data=jsonify({"token": uid}))  # Server shutdown
        return jsonify({'success': False, 'message': 'The maximum number of attempts has been exceeded'})
    
    return render_template('index.html', 
                         encrypted_message=state.encrypted_message,
                         attempts=state.attempts,
                         max_attempts=3)

@app.route('/check_key', methods=['POST'])
def check_key():
    global stop
    # print(f"Check Key called: Attempts: {state.attempts}, Encrypted Message: {state.encrypted_message}")
    if state.attempts >= 3:
        stop = True
        # requests.post('http://127.0.0.1:5000/shutdown', json={"token": uid})
        return jsonify({'success': False, 'message': 'The maximum number of attempts has been exceeded'})
    
    state.attempts += 1
    user_key = request.json.get('key', '')
    decrypted = vigenere_decrypt(state.encrypted_message, user_key)
    decrypted_hash = hashlib.sha256(decrypted.encode()).hexdigest()
    
    if decrypted_hash == state.original_hash:
        # print(uid)
        # requests.post('http://127.0.0.1:5000/shutdown', json={"token": uid})
        # print(decrypted)
        return jsonify({
            'success': True,
            'decrypted': decrypted,
            'attempts': state.attempts
        })

    if state.attempts >= 3:
        stop = True
        # requests.post('http://127.0.0.1:5000/shutdown', json={"token": uid})  # Server shutdown
        return jsonify({'success': False, 'message': 'The maximum number of attempts has been exceeded'})

    return jsonify({
        'success': False,
        'attempts': state.attempts
    })

@app.route('/get_attempts', methods=['GET'])
def get_attempts():
    return jsonify({'attempts': state.attempts, 'max_attempts': 3})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    token = request.json.get('token', None)
    # print(f"UID: {uid} TOKEN: {token}")
    if str(token) != str(uid) and token != None:
        return jsonify({'success': False, 'message': 'Denied'})
    else:
        word = request.json.get('word', None)
        if state.original_message != word:
            return jsonify({'success': False, 'message': 'Denied'})

    shutdown_server()
    
    # return jsonify({'success': False, 'message': 'Server shutting down...'}) 

def shutdown_server():
    # shutfunc = request.environ.get('werkzeug.server.shutdown')
    # if shutfunc is None:
    #     # print("Not running with the Werkzeug Server")
    os.kill(os.getpid(), signal.SIGINT)
    #     raise RuntimeError('Not running with the Werkzeug Server')
    # shutfunc()
    # sys.exit(2)

if __name__ == '__main__':
    
    import argparse

    parser = argparse.ArgumentParser(description='Launching a one-time cryptographically secure "draft"')
    parser.add_argument('--ip', type=str, help='IP address for the site')
    parser.add_argument('--port', type=int, help='PORT for the site')
    
    args = parser.parse_args()

    ip = args.ip # 192.168.31.102
    port = int(args.port)

    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("Enter data to be encrypted and the key for it:")
        state.original_message = getpass("Message: ")
        state.original_key = getpass("Key: ")
        
        # Check that the values are assigned
        # print(f"Original Message: {state.original_message}, Original Key: {state.original_key}")
        
        state.encrypted_message = vigenere_encrypt(state.original_message, state.original_key)
        state.original_hash = hashlib.sha256(state.original_message.encode()).hexdigest()
        # print(f"Encrypted Message: {state.encrypted_message}, Original Hash: {state.original_hash}")

    def monitor_shutdown():
        while not stop:
            time.sleep(1)  # Проверяем состояние каждую секунду
        shutdown_server()

    shutdown_thread = threading.Thread(target=monitor_shutdown)
    shutdown_thread.start()

    app.run(host=ip, port=port)
