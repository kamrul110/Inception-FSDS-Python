"""Always-on voice mode for JARVIS.

Run this script (separate from Streamlit) when you want
JARVIS to listen in a continuous loop and respond by voice
until you say "exit".
"""

import speech_recognition as sr

from config.settings import Settings
from jarvis.gemini_engine import GeminiEngine
from jarvis.prompt_controller import PromptController
from jarvis.memory import Memory
from jarvis.assistant import JarvisAssistant


def main() -> None:
    settings = Settings()
    engine = GeminiEngine(settings.load_api_key())
    memory = Memory()
    controller = PromptController()
    assistant = JarvisAssistant(engine, controller, memory)

    # Initial greeting
    greeting = (
        "Hello! I am JARVIS, your voice assistant. "
        "Speak to me, and say 'exit' when you want me to stop."
    )
    print("JARVIS:", greeting)
    assistant._speak(greeting)

    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.pause_threshold = 1
                audio = recognizer.listen(source)

            try:
                print("Recognizing...")
                query = recognizer.recognize_google(audio, language="en-in")
                print(f"You: {query}")
            except Exception:
                print("I didn't catch that, please speak again.")
                continue

            lower_q = query.lower()
            # Let the assistant handle all commands, including "exit"
            response = assistant.respond(lower_q, role="Tutor", speak_aloud=True)
            print("JARVIS:", response)

            if "exit" in lower_q:
                # After saying the exit message, break the loop
                break

        except KeyboardInterrupt:
            # Allow manual interruption with Ctrl+C
            break


if __name__ == "__main__":
    main()
