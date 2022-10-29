'''
platform_io.py
Handle MQTT connections, subscriptions, and callbacks
'''
import json
from wificom.common.import_secrets import secrets_mqtt_username, \
secrets_device_uuid, \
secrets_user_uuid
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT

last_application_id = None
is_output_hidden = None
new_digirom = None
rtb_user_type = None
rtb_active = False
rtb_host = None
rtb_battle_type = None
rtb_topic = None
rtb_digirom = None

_mqtt_io_prefix = secrets_mqtt_username.lower() + "/f/"
_mqtt_topic_identifier = secrets_user_uuid + '-' + secrets_device_uuid
_mqtt_topic_input = _mqtt_topic_identifier + '/wificom-input'
_mqtt_topic_output =  _mqtt_io_prefix + _mqtt_topic_identifier + "/wificom-output"

_io = None
_mqtt_client = None

def connect_to_mqtt(output, mqtt_client):
	'''
	Connect to the MQTT broker
	'''
	# Initialize MQTT interface
	# pylint: disable=global-statement
	global _mqtt_client
	_mqtt_client = mqtt_client

	if type(output).__name__ != "SocketPool":
		MQTT.set_socket(socket, output)

	# Initialize an IO MQTT Client
	# pylint: disable=global-statement
	global _io
	_io = IO_MQTT(_mqtt_client)

	# Connect the callback methods defined below to MQTT Broker
	_io.on_connect = connected
	_io.on_disconnect = disconnected
	_io.on_subscribe =  subscribe
	_io.on_unsubscribe = unsubscribe

	# Connect to MQTT Broker
	print("Connecting to MQTT Broker...")
	_io.connect()

	# Subscribe to all messages on the mqtt_topic_input feed
	_io.subscribe(_mqtt_topic_input)

	# Set up a callback for the topic/feed
	_io.add_feed_callback(_mqtt_topic_input, on_app_feed_callback)

def loop():
	'''
	Loop IO MQTT client
	'''
	_io.loop()

def get_subscribed_output(clear_rom=True):
	'''
	Get the output from the MQTT broker, and load in new Digirom (and clear if clear_rom is True)
	'''
	# pylint: disable=global-statement,global-variable-not-assigned
	global new_digirom
	returned_digirom = new_digirom

	if clear_rom:
		new_digirom = None

	return returned_digirom

def send_digirom_output(output):
	'''
	Send the output to the MQTT broker
	Set last_application_id for use server side
	'''
	# 8 or less characters is the loaded digirom
	# pylint: disable=global-statement,global-variable-not-assigned
	global last_application_id, rtb_active, rtb_user_type, rtb_topic

	# create json object containing output and device_uuid
	mqtt_message = {
		"application_uuid": last_application_id,
		"device_uuid": secrets_device_uuid,
		"output": str(output)
	}

	mqtt_message_json = json.dumps(mqtt_message)

	if _mqtt_client.is_connected:
		_mqtt_client.publish(_mqtt_topic_output, mqtt_message_json)

def send_rtb_digirom_output(output):
	'''
	Send the RTB output to the MQTT broker
	'''
	# 8 or less characters is the loaded digirom
	if output is not None and len(str(output)) > 8:
		# pylint: disable=global-statement,global-variable-not-assigned
		global last_application_id, rtb_active, rtb_user_type, rtb_topic
		# create json object containing output and device_uuid
		mqtt_message = {
			"application_id": 1,
			"device_uuid": secrets_device_uuid,
			"output": str(output),
			"user_type": rtb_user_type,
		}

		mqtt_message_json = json.dumps(mqtt_message)

		if rtb_active:
			_mqtt_client.publish(rtb_host + '/f/' + rtb_topic, mqtt_message_json)
		else:
			print("RTB not active, shouldn't be calling this callback while RTB is inactive")

def quit_rtb():
	'''
	Exit from any real-time battle
	'''
	# pylint: disable=global-statement
	global rtb_user_type, rtb_active, rtb_host, rtb_battle_type, rtb_topic, rtb_digirom
	if rtb_topic is not None:
		try:
			_mqtt_client.unsubscribe(rtb_host + "/f/" + rtb_topic)
		# pylint: disable=broad-except
		except (Exception) as error:
			print(error)
	rtb_user_type = None
	rtb_active = False
	rtb_host = None
	rtb_battle_type = None
	rtb_topic = None
	rtb_digirom = None

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

def unsubscribe(client, userdata, topic, granted_qos):
	# pylint: disable=unused-argument
	'''
	This method is called when the client unsubscribes to a feed.
	'''
	# pylint: disable=consider-using-f-string
	print("Unsubscribed to {0} with QOS level {1}".format(topic, granted_qos))


# pylint: disable=unused-argument
def disconnected(client):
	# pylint: disable=unused-argument
	'''
	Disconnected function will be called when the client disconnects.
	'''
	print("Disconnected from MQTT Broker!")


def on_app_feed_callback(client, topic, message):
	# pylint: disable=unused-argument
	'''
	Method called whenever application specific feed/topic has received data
		Expected request body:
		{
			"output": "V1-0000", # This would likely be the packet to send to the next device, WIP
			"application_id": APP_UUID,
			"hide_output": False,
			"host": "BrassBolt",
			"topic_action" = "subscribe", # subscribe/unsubscribe
			"topic": "RTB_TOPIC_GOES_HERE,
			"user_type": "guest" # Guest or Host, each side expects the opposite for real messages
		}
	'''
	# pylint: disable=consider-using-f-string
	print("New message on topic {0}: {1} ".format(topic, message))

	# parse message as json
	message_json = json.loads(message)

	# pylint: disable=global-statement
	global last_application_id, is_output_hidden, new_digirom, rtb_user_type, \
			rtb_active, rtb_host, rtb_topic, rtb_battle_type

	print(message_json)

	# If message_json contains topic_action, then we have a realtime battle request
	topic_action = message_json.get('topic_action', None)

	# Quit RTB before joining a new one or setting a digirom
	if topic_action is not None or message_json['digirom'] is not None:
		quit_rtb()

	# Subscribe to realtime battle topic
	if topic_action == "subscribe":
		rtb_topic = message_json['topic']
		rtb_active = True
		rtb_user_type = message_json['user_type']
		rtb_host = message_json['host']
		rtb_battle_type = message_json['battle_type']
		_mqtt_client.subscribe(rtb_host + "/f/" + message_json['topic'])
		_mqtt_client.add_topic_callback(
			rtb_host + "/f/" + message_json['topic'],
			on_realtime_battle_feed_callback
		)
	else:
		# Here we deal with a normal message, one without a topic sub/unsub action
		is_output_hidden = message_json['hide_output']
		last_application_id = message_json['application_id']
		new_digirom = message_json['digirom']

def on_realtime_battle_feed_callback(client, topic, message):
	# pylint: disable=unused-argument
	'''
	Method called whenever a realtime battle topic has received data

	Expected request body:
		{
			"output": "V1-0000", # This would likely be the packet to send to the next device, WIP
			"application_id": 1, # This is always 1 for RTB
			"user_type": "guest" # Guest or Host, each side expects the opposite for real messages
		}
	'''
	# pylint: disable=consider-using-f-string
	print("New RTB message on topic {0}: {1} ".format(topic, message))
	# parse message as json
	message_json = json.loads(message)

	# pylint: disable=global-statement
	global last_application_id, rtb_digirom

	if rtb_active:
		if 'user_type' in message_json:
			if message_json['user_type'] is not None and message_json['user_type'] != rtb_user_type:
				last_application_id = message_json['application_id']
				rtb_digirom = message_json['output']
			else:
				print('rtb_user_type is not[' + rtb_user_type + '] ignoring Digirom')
	else:
		print("realtime battle is not active, shouldn't be receiving data to this callback..")
