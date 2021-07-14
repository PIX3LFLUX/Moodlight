import requests
import json 
import time

bridge_ip="192.168.178.79"
bridge_username="ZdgukOoXbpuwxKhcMioCljyeyCMKXIeJC0LmEtKI"
def turn_on_group(where):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":True}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

# Beispiel:
# turn_off_group('kitchen')
def turn_off_group(where):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":False}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

def switch_light_color(where,what):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":True,"sat":254, "bri":254,"hue":what}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)
turn_on_group('pixelflux')

switch_light_color('pixelflux',64000)