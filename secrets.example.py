'''
This file is where you keep secret settings, keep it safe and keep a backup.
Please note, you can get an automatically generated version of this on the webapp
'''

secrets = {
	# WiFi network variables
	"wireless_networks":[
		{'ssid': 'FIRST_SSID', 'password': 'YOURSECUREPASSWORD'},
		# {'ssid': 'SECOND_SSID', 'password': 'YOURSECUREPASSWORD'}, # Example of an additional network
		# {'ssid': 'THIRD_SSID', 'password': 'YOURSECUREPASSWORD'}, # Example of an additional network
	],
	# Hosted service variables
	'broker' : 'mqtt.wificom.dev',
	'mqtt_username' : 'YOUR_WIFICOM.DEV_USERNAME',
	'mqtt_password' : 'YOUR_WIFICOM.DEV_MQTT_AUTH_TOKEN',
	'user_uuid': 'FIND_ON_WIFICOM.DEV',
	'device_uuid': 'FIND_ON_WIFICOM.DEV',
}
