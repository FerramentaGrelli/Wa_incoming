from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv
import os
import requests

# Carica le variabili d'ambiente dal file .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permette richieste CORS dal frontend

# Simula un database in memoria per i messaggi
messages = []

@app.route('/incoming-message', methods=['POST'])
def receive_message():
    """Riceve un messaggio WhatsApp in ingresso."""
    data = request.form  # Twilio invia i dati in formato form-urlencoded
    sender = data.get('From', '')  # Numero del mittente
    message = data.get('Body', '')  # Corpo del messaggio

    if sender and message:
        messages.append({'sender': sender, 'message': message})
        return "Messaggio ricevuto", 200
    return "Dati mancanti", 400


@app.route('/get-messages', methods=['GET'])
def get_messages():
    """Ritorna i messaggi in ingresso."""
    return jsonify(messages), 200


@app.route('/send-message', methods=['POST'])
def send_message():
    """Invia un messaggio di risposta tramite Twilio."""
    # Configura le credenziali di Twilio
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_NUMBER')

    client = Client(account_sid, auth_token)

    data = request.get_json()
    recipient = data.get('recipient')
    message = data.get('message')

    if not recipient or not message:
        return jsonify({'error': 'Dati mancanti'}), 400

    try:
        client.messages.create(
            from_=twilio_number,
            to=recipient,
            body=message
        )
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Funzione per scaricare i file multimediali
def download_media(url, from_number):
    # Scarica l'immagine o il file multimediale
    response = requests.get(url)
    
    # Salva il file localmente, puoi anche fare altre operazioni, come archiviarlo su un server
    file_path = f"downloads/{from_number}_media.jpg"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f"File scaricato da {url} e salvato come {file_path}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
