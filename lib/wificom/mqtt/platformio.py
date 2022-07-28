import json
from . import *
from wificom.common.importSecrets import *
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT

newDigirom = None

 # Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
	broker=secrets_mqtt_broker, 
	port=1883,
	username=secrets_mqtt_username,
	password=secrets_mqtt_password
)

# Initialize an IO MQTT Client
io = IO_MQTT(mqtt_client) 

mqtt_topic_input = secrets_user_uuid + '-' + secrets_device_uuid + '/wificom-input'
mqtt_topic_output = secrets_mqtt_username + "/f/" + secrets_user_uuid + "-" + secrets_device_uuid + "/wificom-output"

last_application_id = None
is_output_hidden = None

class PlatformIO:
	def loop():
		io.loop() 

	def getSubscribedOutput(clear_rom=True):
		global newDigirom

		returnedDigirom = newDigirom

		if(clear_rom):
			newDigirom = None
		
		return returnedDigirom

	def getIsOutputHidden():

		global is_output_hidden
		return is_output_hidden
	
	def connect_to_mqtt(esp):
		# Initialize MQTT interface with the esp interface
		MQTT.set_socket(socket, esp)

		# Connect the callback methods defined above to MQTT Broker
		io.on_connect = connected
		io.on_disconnect = disconnected
		io.on_subscribe = subscribe

		# Set up a callback for the led feed
		io.add_feed_callback(mqtt_topic_input, on_feed_callback)

		# Connect to MQTT Broker
		print("Connecting to MQTT Broker...")
		io.connect()

		# Subscribe to all messages on the mqtt_topic_input feed
		io.subscribe(mqtt_topic_input)

	def on_digirom_output(output):
		global last_application_id
		# create json object containing output and device_uuid
		mqtt_message = {
			"application_uuid": last_application_id,
			"device_uuid": secrets['device_uuid'],
			"output": str(output)
		}

		mqtt_message_json = json.dumps(mqtt_message)

		mqtt_client.publish(mqtt_topic_output, mqtt_message_json)

# Define callback functions which will be called when certain events happen.
def connected(client):
	# Connected function will be called when the client is connected to the MQTT Broker
	print("Connected to MQTT Broker! ")


def subscribe(client, userdata, topic, granted_qos):
	# This method is called when the client subscribes to a new feed.
	print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

 
# pylint: disable=unused-argument
def disconnected(client):
	# Disconnected function will be called when the client disconnects.
	print("Disconnected from MQTT Broker!")


def on_feed_callback(client, topic, message):
	# Method called whenever user/feeds/led has a new value
	print("New message on topic {0}: {1} ".format(topic, message))
	# parse message as json
	message_json = json.loads(message)

	global newDigirom, last_application_id, is_output_hidden
	
	last_application_id = message_json['application_id']
	newDigirom = message_json['digirom']
	is_output_hidden = message_json['hide_output']

