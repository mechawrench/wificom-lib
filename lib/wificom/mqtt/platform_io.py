'''
platform_io.py
Handle MQTT connections, subscriptions, and callbacks
'''
import json
from wificom.common.import_secrets import secrets_mqtt_broker, \
secrets_mqtt_username, \
secrets_mqtt_password, \
secrets_device_uuid, \
secrets_user_uuid
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT

 # Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
	broker=secrets_mqtt_broker,
	port=1883,
	username=secrets_mqtt_username.lower(),
	password=secrets_mqtt_password,
)

# Initialize an IO MQTT Client
io = IO_MQTT(mqtt_client)

last_application_id = None
is_output_hidden = None
new_digirom = None

class PlatformIO:
	'''
	Handles WiFi connection for Arduino Nano Connect board
	'''
	def __init__(self):
		self.mqtt_io_prefix = secrets_mqtt_username.lower() + "/f/"
		self.mqtt_topic_identifier = secrets_user_uuid + '-' + secrets_device_uuid
		self.mqtt_topic_input = self.mqtt_topic_identifier + '/wificom-input'
		self.mqtt_topic_output =  self.mqtt_io_prefix + self.mqtt_topic_identifier + "/wificom-output"

	def loop(self):
		'''
		Loop IO MQTT client
		'''
		io.loop()

	def get_subscribed_output(self, clear_rom=True):
		'''
		Get the output from the MQTT broker, and load in new Digirom (and clear if clear_rom is True)
		'''
		# pylint: disable=global-statement,global-variable-not-assigned
		global new_digirom
		returned_digirom = new_digirom

		if clear_rom:
			new_digirom = None

		return returned_digirom

	def get_is_output_hidden(self):
		'''
		Get the is_output_hidden value
		'''
		# pylint: disable=global-statement,global-variable-not-assigned
		global is_output_hidden

		return is_output_hidden

	def connect_to_mqtt(self, esp, socket):
		'''
		Connect to the MQTT broker
		'''
		# Initialize MQTT interface with the esp interface
		MQTT.set_socket(socket, esp)

		# Connect the callback methods defined above to MQTT Broker
		io.on_connect = connected
		io.on_disconnect = disconnected
		io.on_subscribe =  subscribe

		# Set up a callback for the led feed
		io.add_feed_callback(self.mqtt_topic_input, on_feed_callback)

		# Connect to MQTT Broker
		print("Connecting to MQTT Broker...")
		# io.connect()
		mqtt_client.connect()

		# Subscribe to all messages on the mqtt_topic_input feed
		io.subscribe(self.mqtt_topic_input)

	def on_digirom_output(self, output):
		'''
		Send the output to the MQTT broker
		Set last_application_id for use serverside
		'''
		# pylint: disable=global-statement,global-variable-not-assigned
		global last_application_id
		# create json object containing output and device_uuid
		mqtt_message = {
			"application_uuid": last_application_id,
			"device_uuid": secrets_device_uuid,
			"output": str(output)
		}

		mqtt_message_json = json.dumps(mqtt_message)

		mqtt_client.publish(self.mqtt_topic_output, mqtt_message_json)

# Define callback functions which will be called when certain events happen.
def connected(client):
	# pylint: disable=unused-argument
	'''
	Connected function will be called when the client is connected to the MQTT Broker
	'''
	print("Connected to MQTT Broker! ")


def subscribe(client, userdata, topic, granted_qos):
	# pylint: disable=unused-argument
	'''
	This method is called when the client subscribes to a new feed.
	'''
	# pylint: disable=consider-using-f-string
	print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


# pylint: disable=unused-argument
def disconnected(client):
	# pylint: disable=unused-argument
	'''
	Disconnected function will be called when the client disconnects.
	'''
	print("Disconnected from MQTT Broker!")


def on_feed_callback(client, topic, message):
	# pylint: disable=unused-argument
	'''
	Method called whenever user/feeds/led has a new value
	'''
	# pylint: disable=consider-using-f-string
	print("New message on topic {0}: {1} ".format(topic, message))
	# parse message as json
	message_json = json.loads(message)

	# pylint: disable=global-statement
	global last_application_id, is_output_hidden, new_digirom

	last_application_id = message_json['application_id']
	is_output_hidden = message_json['hide_output']
	new_digirom = message_json['digirom']
