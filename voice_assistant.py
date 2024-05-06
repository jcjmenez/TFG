import speech_recognition as sr
import subprocess
from fuzzywuzzy import fuzz
from navigator import Navigator
from gtts import gTTS
import os
import pygame
from io import BytesIO

class VoiceAssistant:
    def __init__(self, wake_word="okay drivia", language="es-ES"):
        self.wake_word = wake_word
        self.language = language
        self.recognizer = sr.Recognizer()

    def is_similar_to_wake_word(self, phrase):
        similarity = fuzz.partial_ratio(phrase.lower(), self.wake_word)
        # Minimum similarity of 50% (doesn't recognize drivia as a word)
        return similarity >= 70

    def listen_for_keyword(self):
        with sr.Microphone() as source:
            print("Listening for the wake word...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            print("Recognizing...")
            phrase = self.recognizer.recognize_google(audio, language=self.language)
            print("You said:", phrase)
            if self.is_similar_to_wake_word(phrase):
                return True
            else:
                return False
        except sr.UnknownValueError:
            print("Could not understand audio")
            return False
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            return False

    def process_command(self):
        with sr.Microphone() as source:
            

            try:
                print("Listening for the command...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10)
                command = self.recognizer.recognize_google(audio, language=self.language)
                print("Command:", command)
                return self.perform_action(command)
            except sr.WaitTimeoutError:
                print("Timeout...")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
        return None

    def perform_action(self, command):
        print("Triggering action...")
        #TODO: Implement predictive model to determine the action to perform
        if "abre" in command:
            subprocess.Popen(["notepad.exe"])
        
        elif "gasolinera" in command.lower():
            navigator = Navigator()
            self.text_to_speech(navigator.nearest_gas_station())
            return "Gas"
        elif "clip" in command.lower() or "graba" in command.lower() or "video" in command.lower():
            self.text_to_speech("Grabando video")
            return "Clip"
        elif "distancia" in command.lower():
            location = command.split(" a ")[1]
            navigator = Navigator()
            self.text_to_speech(navigator.get_distance_to(location))
        else:
            print("Command not recognized")
            return None
    
    

    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='es')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        pygame.mixer.init()
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

    def run(self):
        while True:
            if self.listen_for_keyword():
                self.process_command()

if __name__ == "__main__":
    assistant = VoiceAssistant(language="es-ES")
    assistant.run()
