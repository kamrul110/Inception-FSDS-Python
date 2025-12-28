
import datetime
import threading
import time
import webbrowser
from typing import Optional
import pyttsx3
import pyautogui
import wikipedia
import os

class JarvisAssistant:
    def __init__(self, engine, prompt_controller, memory):
        self.engine = engine
        self.prompt_controller = prompt_controller
        self.memory = memory

 
        self._tts_engine = pyttsx3.init("sapi5")
        self._tts_engine.setProperty("rate", 170)
        voices = self._tts_engine.getProperty("voices") or []
        if voices:
            self._tts_engine.setProperty("voice", voices[0].id)

        self._engine_lock = threading.Lock()

 
    def _speak(self, text):
        """Speak text asynchronously so the app does not block.

        Also interrupts any previous speech before starting the new one,
        so commands like "exit" can cut off what JARVIS was saying.
        """

        if not text:
            return

        def _run():
            try:
                with self._engine_lock:
                    # Stop any speech currently in progress
                    try:
                        self._tts_engine.stop()
                    except Exception:
                        pass

                    self._tts_engine.say(text)
                    self._tts_engine.runAndWait()
            except Exception:
                # Never crash the app because of audio issues
                pass

        threading.Thread(target=_run, daemon=True).start()
    
    
    
    def _current_time_text(self) -> str:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return f"Sir, the time is {now}."

    def _take_screenshot(self) -> str:
        try:
            img = pyautogui.screenshot()
            img.save("screenshot.png")
            self._speak("Screenshot taken")
            return "Screenshot taken and saved as screenshot.png."
        except Exception:
            return "I could not take a screenshot right now."

    def _set_timer(self, query: str) -> str:
        minutes: Optional[int] = None
        for word in query.split():
            if word.isdigit():
                minutes = int(word)
                break

        if minutes is None:
            self._speak("Sorry, I could not find the time.")
            return "Sorry, I could not find the time to set a timer. Please say, for example, 'set a timer for 1 minute'."

        self._speak(f"{minutes} minute timer started.")

        def run_timer() -> None:
            time.sleep(minutes * 60)
            try:
                with self._engine_lock:
                    self._tts_engine.say("Sir, your timer is complete.")
                    self._tts_engine.runAndWait()
            except Exception:
                pass

        threading.Thread(target=run_timer, daemon=True).start()
        return f"Timer started for {minutes} minute(s)."

    def _wikipedia_summary(self, query: str) -> str:
        topic = query.replace("wikipedia", "").strip()
        if not topic:
            return "Please tell me what you want me to search on Wikipedia."

        try:
            summary = wikipedia.summary(topic, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as exc:
            return f"The topic '{topic}' is ambiguous. Some options are: {', '.join(exc.options[:5])}."
        except Exception:
            return "I was not able to fetch information from Wikipedia right now."

 
    def respond(self, user_input, role="Tutor", speak_aloud: bool = True):
        """Generate a response using the selected assistant role.

        This method first checks for special commands (weather, news,
        timer, screenshot, etc.). If none match, it falls back to the
        normal conversational Gemini model response.
        """

        text = (user_input or "").strip()
        if not text:
            return ""

        lowered = text.lower()
        reply = None

        if "your name" in lowered:
            reply = "My name is JARVIS."

        elif "weather" in lowered:
            webbrowser.open("https://www.google.com/search?q=weather")
            reply = "Opening weather details in your browser."

        elif "typing test" in lowered:
            # The full, interactive typing test is implemented in the UI.
            reply = (
                "Typing speed test is ready. "
                "Use the 'Typing Speed Test' panel in the sidebar to start."
            )

        elif "news" in lowered:
            webbrowser.open("https://news.google.com")
            reply = "Opening top news in your browser."
        
        elif "battery" in lowered or "battery performance" in lowered:
            reply = "Redirecting you to your battery settings to check performance."
            os.system("start ms-settings:batterysaver")  # opens Battery & Power settings
            
            
            
        elif "take screenshot" in lowered:
            reply = self._take_screenshot()

        elif "set a timer" in lowered:
            reply = self._set_timer(text)

        elif "time" in lowered:
            reply = self._current_time_text()

        elif "wikipedia" in lowered:
            reply = self._wikipedia_summary(lowered)

        elif "youtube" in lowered:
            query = lowered.replace("youtube", "").strip()
            if query:
                url = f"https://www.youtube.com/results?search_query={query}"
            else:
                url = "https://www.youtube.com"
            webbrowser.open(url)
            reply = "Opening YouTube for you."

        elif "open google" in lowered:
            webbrowser.open("https://www.google.com")
            reply = "Opening Google in your browser."

        elif "exit" in lowered:
       
            reply = "Thank you for your time, sir. Have a great day ahead!"

      
        if reply is None:
            context = self.memory.get_history()
            prompt = self.prompt_controller.build_prompt(text, context, role)
            reply = self.engine.generate(prompt)

       
        self.memory.add("User", text)
        self.memory.add("Assistant", reply)
# here
        if speak_aloud:
            self._speak(reply)

        return reply

