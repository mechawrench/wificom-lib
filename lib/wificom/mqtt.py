'''
mqtt.py
Handle MQTT connections, subscriptions, and callbacks
'''

# pylint: disable=global-statement,unused-argument

import time
import json
from wificom.import_secrets import secrets_mqtt_username, \
secrets_device_uuid, \
secrets_user_uuid

last_application_id = None
is_output_hidden = None
api_response = None
new_digirom = None
rtb_user_type = None
rtb_active = False
rtb_host = None
rtb_battle_type = None
rtb_topic = None
rtb_digirom = None

_mqtt_io_prefix = secrets_mqtt_username.lower() + "/f/"
_mqtt_topic_identifier = secrets_user_uuid + '-' + secrets_device_uuid
_mqtt_topic_input = _mqtt_io_prefix + _mqtt_topic_identifier + '/wificom-input'
_mqtt_topic_output =  _mqtt_io_prefix + _mqtt_topic_identifier + "/wificom-output"

_io = None
_mqtt_client = None

def connect_to_mqtt(mqtt_client):
	'''
	Connect to the MQTT broker
	'''
	# Initialize MQTT interface
	global _mqtt_client
	_mqtt_client = mqtt_client

	_mqtt_client.on_connect = connect
	_mqtt_client.on_disconnect = disconnect
	_mqtt_client.on_subscribe = subscribe
	_mqtt_client.on_unsubscribe = unsubscribe

	# Connect to MQTT Broker
	attempt = 0
	while attempt < 3:
		try:
			print(f"Connecting to MQTT Broker (attempt {attempt+1})...")
			_mqtt_client.connect()
			break
		except Exception as e:  # pylint: disable=broad-except
			print(f"Failed to connect to MQTT Broker: {type(e)} - {e}")
			attempt += 1
			time.sleep(1)
	else:
		print("Unable to connect to MQTT Broker after 3 attempts.")
		return False

	# Use _mqtt_client to subscribe to the mqtt_topic_input feed
	_mqtt_client.subscribe(_mqtt_topic_input)

	# Set up a callback for the topic/feed
	_mqtt_client.add_topic_callback(_mqtt_topic_input, on_app_feed_callback)

	return True

def loop():
	"""
	Loop IO MQTT client
	"""
	max_failures = 5
	failure_count = 0
	start_time = time.monotonic()
	timeout = 50

	while failure_count < max_failures:
		try:
			_mqtt_client.loop()
			return True
		# pylint: disable=broad-except
		except Exception as e:
			failure_count += 1
			print(f"Error: {e}. Attempt {failure_count} of {max_failures} failed.")

			if time.monotonic() - start_time >= timeout:
				start_time = time.monotonic()
				failure_count = 0

			if failure_count == max_failures:
				print("Maximum number of failures reached.")
				return False

def get_subscribed_output(clear_rom=True):
	'''
	Get the output from the MQTT broker, and load in new Digirom (and clear if clear_rom is True)
	'''
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

def handle_result(result):
	'''
	Handle the DigiROM result according to settings
	'''
	if not api_response:
		print(result)
	else:
		print("DigiROM executed")

def quit_rtb():
	'''
	Exit from any real-time battle
	'''
	global rtb_user_type, rtb_active, rtb_host, rtb_battle_type, rtb_topic, rtb_digirom
	if rtb_topic is not None:
		try:
			_mqtt_client.unsubscribe(rtb_host + "/f/" + rtb_topic)
		except Exception as e:  # pylint: disable=broad-except
			print(e)
	rtb_user_type = None
	rtb_active = False
	rtb_host = None
	rtb_battle_type = None
	rtb_topic = None
	rtb_digirom = None

def on_app_feed_callback(client, topic, message):
	'''
	Method called whenever application specific feed/topic has received data
		Expected request body:
		{
			"output": "V1-0000", # This would likely be the packet to send to the next device, WIP
			"application_id": APP_UUID,
			"api_response": False,
			"host": "BrassBolt",
			"topic_action" = "subscribe", # subscribe/unsubscribe
			"topic": "RTB_TOPIC_GOES_HERE,
			"user_type": "guest" # Guest or Host, each side expects the opposite for real messages,
			"ack_id" 111111 # Acknowledgement ID, used to acknowledge the message
		}
	'''

	print(f"New message on topic {topic}", end="")

	# parse message as json
	try:
		message_json = json.loads(message)
	except json.decoder.JSONDecodeError:
		print(":", message)
		raise

	if not message_json["api_response"]:
		print(":", message, end="")
	if is_output_hidden:
		print("check the App", end="")
	print()

	global last_application_id, api_response, new_digirom, rtb_user_type, \
			rtb_active, rtb_host, rtb_topic, rtb_battle_type

	# If message has an ack_id, acknowledge it
	if "ack_id" in message_json:
		mqtt_message = {
			"application_uuid": last_application_id,
			"device_uuid": secrets_device_uuid,
			"ack_id": message_json["ack_id"]
		}

		mqtt_message_json = json.dumps(mqtt_message)
		if _mqtt_client.is_connected:
			_mqtt_client.publish(_mqtt_topic_output, mqtt_message_json)

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
		api_response = message_json['api_response']
		last_application_id = message_json['application_id']
		new_digirom = message_json['digirom']
		print("Received new DigiROM", end="")
		if not api_response:
			print(":", new_digirom, end="")
		print()

def on_realtime_battle_feed_callback(client, topic, message):
	'''
	Method called whenever a realtime battle topic has received data

	Expected request body:
		{
			"output": "V1-0000", # This would likely be the packet to send to the next device, WIP
			"application_id": 1, # This is always 1 for RTB
			"user_type": "guest" # Guest or Host, each side expects the opposite for real messages
		}
	'''
	print(f"New RTB message on topic {topic}: {message}")
	# parse message as json
	message_json = json.loads(message)

	global last_application_id, rtb_digirom

	if rtb_active:
		if 'user_type' in message_json:
			if message_json['user_type'] is not None and message_json['user_type'] != rtb_user_type:
				last_application_id = message_json['application_id']
				rtb_digirom = message_json['output']
			else:
				print('(user_type is [' + rtb_user_type + ']; ignoring message from self)')
	else:
		print("realtime battle is not active, shouldn't be receiving data to this callback..")

def connect(client, userdata, flags, r_c):
	'''
	This method is called when the client connects to MQTT Broker
	'''
	print('Connected to MQTT Broker!')

def disconnect(client, userdata, r_c):
	'''
	This method is called when the client disconnects from the MQTT Broker
	'''
	print('Disconnected from MQTT Broker!')

def subscribe(client, userdata, topic, granted_qos):
	'''
	This method is called when the client subscribes to a new feed.
	'''
	print(f"Subscribed to {topic} with QOS level {granted_qos}")

def unsubscribe(client, userdata, topic, pid):
	'''
	This method is called when the client unsubscribes from a feed.
	'''
	print(f"Unsubscribed from {topic} with PID {pid}")
