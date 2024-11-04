from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
import requests
import logging
import sys

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger()

# Configuración del broker (Cluster HiveMQ)
broker_url = "fee7a60180ef4e41a8186ff373e7ff32.s1.eu.hivemq.cloud"
broker_port = 8883
username = "Receptor-99"
password = "Receptor-99"

# Configuración de la API de Supabase
supabase_url = 'https://qiuemjqtqiyyxumrkdga.supabase.co/rest/v1/mensajes_mixtos?limit=10000'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpdWVtanF0cWl5eXh1bXJrZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjczODgyMDMsImV4cCI6MjA0Mjk2NDIwM30.9R7O3A_sVy01z6OgjseBxxks5J5CdVlYnyffAiEV3So'

headers = {
    'apikey': api_key,
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Crear la aplicación Flask
app = Flask(__name__, static_folder='static')
CORS(app)

# Contador para la suscripción (para asegurar suscripción única)
subscription_done = False

# Función que se ejecuta cuando se conecta al broker
def on_connect(client, userdata, flags, rc):
    global subscription_done
    if rc == 0:
        logger.info("Conectado al broker MQTT con éxito")
        if not subscription_done:
            client.subscribe("test/topic")
            subscription_done = True
            logger.info("Suscrito al topic: test/topic")
        else:
            logger.info("Ya se realizó la suscripción.")
    else:
        logger.error(f"Error al conectarse, código de resultado: {rc}")

# Función que se ejecuta cuando se recibe un mensaje
def on_message(client, userdata, message):
    logger.info("on_message called")
    msg = message.payload.decode()
    logger.info(f"Mensaje recibido en el topic {message.topic}: {msg}")
    
    # Enviar el mensaje a Supabase
    data = {
        "mensaje": msg
    }
    try:
        response = requests.post(supabase_url, headers=headers, json=data)
        if response.status_code == 201:
            logger.info("Mensaje almacenado en Supabase con éxito.")
        else:
            logger.error(f"Error al almacenar el mensaje en Supabase: {response.status_code}, {response.text}")
    except Exception as e:
        logger.exception("Ocurrió un error al realizar la solicitud a Supabase")

# Configuración del cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Conectar usando SSL/TLS
mqtt_client.tls_set()
mqtt_client.connect(broker_url, broker_port)

# Mantener el cliente en espera de mensajes
mqtt_client.loop_start()

# Endpoint para servir la página HTML
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mensajes', methods=['GET'])
def get_mensajes():
    try:
        # Obtener página y límite de la solicitud
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Calcular los índices de inicio y fin
        start = (page - 1) * limit
        end = start + limit

        # Modificar URL de Supabase con el rango
        paginated_url = f'{supabase_url}&range={start}-{end-1}'
        response = requests.get(paginated_url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            logger.error("Error al obtener mensajes")
            return jsonify({"error": "Error al obtener mensajes"}), response.status_code
    except Exception as e:
        logger.exception("Ocurrió un error al obtener mensajes")
        return jsonify({"error": str(e)}), 500
