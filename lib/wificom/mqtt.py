'''
mqtt.py
Handle MQTT connections, subscriptions, and callbacks
'''

# pylint: disable=unused-argument

import json
from wificom import version
from wificom.import_secrets import secrets_mqtt_username, \
secrets_device_uuid, \
secrets_user_uuid

_mqtt_io_prefix = secrets_mqtt_username.lower() + "/f/"
_mqtt_topic_identifier = secrets_user_uuid + '-' + secrets_device_uuid
_mqtt_topic_input = _mqtt_io_prefix + _mqtt_topic_identifier + '/wificom-input'
_mqtt_topic_output =  _mqtt_io_prefix + _mqtt_topic_identifier + "/wificom-output"

class MQTT_data:  #pylint:disable=invalid-name
	'''
	Stores data for the MQTT connection.
	'''
	def __init__(self):
		self.mqtt_client = None
		self.last_application_id = None
		self.is_output_hidden = None
		self.api_response = None
		self.new_digirom = None
		self.cached_digirom_output = None

class RTB_data:  #pylint:disable=invalid-name
	'''
	Stores data for real-time battles.
	'''
	def __init__(self):
		self.user_type = None
		self.active = False
		self.host = None
		self.battle_type = None
		self.topic = None
		self.digirom = None

_data = MQTT_data()
rtb = RTB_data()

def connect_to_mqtt(mqtt_client):
	'''
	Connect to the MQTT broker
	'''
	# Initialize MQTT interface
	_data.mqtt_client = mqtt_client

	mqtt_client.on_connect = connect
	mqtt_client.on_disconnect = disconnect
	mqtt_client.on_subscribe = subscribe
	mqtt_client.on_unsubscribe = unsubscribe

	# Connect to MQTT Broker
	try:
		print("Connecting to MQTT Broker...")
		mqtt_client.connect()
	except Exception as e:  # pylint: disable=broad-except
		print(f"Failed to connect to MQTT Broker: {repr(e)}")
		return False

	# Use mqtt_client to subscribe to the mqtt_topic_input feed
	mqtt_client.subscribe(_mqtt_topic_input)

	# Set up a callback for the topic/feed
	mqtt_client.add_topic_callback(_mqtt_topic_input, on_app_feed_callback)

	_data.cached_digirom_output = version.dictionary()
	_data.cached_digirom_output["device_uuid"] = secrets_device_uuid

	return True

def loop():
	'''
	Loop IO MQTT client
	'''
	_data.mqtt_client.loop(1)

def get_subscribed_output(clear_rom=True):
	'''
	Get the output from the MQTT broker, and load in new Digirom (and clear if clear_rom is True)
	'''
	returned_digirom = _data.new_digirom

	if clear_rom:
		_data.new_digirom = None

	return returned_digirom

def send_digirom_output(output):
	'''
	Send the output to the MQTT broker
	Set last_application_id and version info for use server side
	'''

	# update json object with output and application_id
	_data.cached_digirom_output["application_uuid"] = _data.last_application_id
	_data.cached_digirom_output["output"] = str(output)

	mqtt_message_json = json.dumps(_data.cached_digirom_output)

	if _data.mqtt_client.is_connected:
		_data.mqtt_client.publish(_mqtt_topic_output, mqtt_message_json)

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
			"user_type": rtb.user_type,
		}

		mqtt_message_json = json.dumps(mqtt_message)

		if rtb.active:
			_data.mqtt_client.publish(rtb.host + '/f/' + rtb.topic, mqtt_message_json)
		else:
			print("RTB not active, shouldn't be calling this callback while RTB is inactive")

def handle_result(result):
	'''
	Handle the DigiROM result according to settings
	'''
	if not _data.api_response:
		print(result)
	else:
		print("DigiROM executed")

def quit_rtb():
	'''
	Exit from any real-time battle
	'''
	if rtb.topic is not None:
		_data.mqtt_client.unsubscribe(rtb.host + "/f/" + rtb.topic)
	_data.api_response = None
	rtb.user_type = None
	rtb.active = False
	rtb.host = None
	rtb.battle_type = None
	rtb.topic = None
	rtb.digirom = None

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
	if _data.is_output_hidden:
		print("check the App", end="")
	print()

	# If message has an ack_id, acknowledge it
	if "ack_id" in message_json:
		mqtt_message = {
			"application_uuid": _data.last_application_id,
			"device_uuid": secrets_device_uuid,
			"ack_id": message_json["ack_id"]
		}

		mqtt_message_json = json.dumps(mqtt_message)
		if _data.mqtt_client.is_connected:
			_data.mqtt_client.publish(_mqtt_topic_output, mqtt_message_json)

	# If message_json contains topic_action, then we have a realtime battle request
	topic_action = message_json.get('topic_action', None)

	# Quit RTB before joining a new one or setting a digirom
	if topic_action is not None or message_json['digirom'] is not None:
		quit_rtb()

	# Subscribe to realtime battle topic
	if topic_action == "subscribe":
		rtb.topic = message_json['topic']
		rtb.active = True
		rtb.user_type = message_json['user_type']
		rtb.host = message_json['host']
		rtb.battle_type = message_json['battle_type']
		_data.mqtt_client.subscribe(rtb.host + "/f/" + message_json['topic'])
		_data.mqtt_client.add_topic_callback(
			rtb.host + "/f/" + message_json['topic'],
			on_realtime_battle_feed_callback
		)
	else:
		# Here we deal with a normal message, one without a topic sub/unsub action
		_data.api_response = message_json['api_response']
		_data.last_application_id = message_json['application_id']
		_data.new_digirom = message_json['digirom']
		print("Received new DigiROM", end="")
		if not _data.api_response:
			print(":", _data.new_digirom, end="")
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

	if rtb.active:
		if 'user_type' in message_json:
			if message_json['user_type'] is not None and message_json['user_type'] != rtb.user_type:
				_data.last_application_id = message_json['application_id']
				rtb.digirom = message_json['output']
			else:
				print('(user_type is [' + rtb.user_type + ']; ignoring message from self)')
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
