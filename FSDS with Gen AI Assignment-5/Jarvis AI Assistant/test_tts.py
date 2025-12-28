import pyttsx3

engine = pyttsx3.init("sapi5")
engine.setProperty("rate", 170)
voices = engine.getProperty("voices") or []
if voices:
    engine.setProperty("voice", voices[0].id)

engine.say("This is a test. If you hear this, text to speech is working.")
engine.runAndWait()
