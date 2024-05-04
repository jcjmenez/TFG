import speech_recognition as sr
import subprocess
from fuzzywuzzy import fuzz

class VoiceAssistant:
    def __init__(self, wake_word="ok drivia", language="es-ES"):
        self.wake_word = wake_word
        self.language = language
        self.recognizer = sr.Recognizer()

    def is_similar_to_wake_word(self, phrase):
        similarity = fuzz.partial_ratio(phrase.lower(), self.wake_word)
        # Minimum similarity of 50% (doesn't recognize drivia as a word)
        return similarity >= 50

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
                self.perform_action(command)
            except sr.WaitTimeoutError:
                print("Timeout...")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

    def perform_action(self, command):
        print("Triggering action...")
        if "abre" in command:
            subprocess.Popen(["notepad.exe"]) 
        else:
            print("Command not recognized")

    def run(self):
        while True:
            if self.listen_for_keyword():
                self.process_command()

if __name__ == "__main__":
    assistant = VoiceAssistant(language="es-ES")
    assistant.run()
