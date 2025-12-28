# Streamlit UI
# app.py
import streamlit as st
from config.settings import Settings
from jarvis.gemini_engine import GeminiEngine
from jarvis.prompt_controller import PromptController
from jarvis.memory import Memory
from jarvis.assistant import JarvisAssistant
import speech_recognition as sr
import json
import time
import random

# Setup
settings = Settings()
engine = GeminiEngine(settings.load_api_key())
memory = Memory()
controller = PromptController()
assistant = JarvisAssistant(engine, controller, memory)

st.title("🧠 JARVIS – Your AI Assistant")

# Sidebar controls
st.sidebar.header("Options")
assistant_role = st.sidebar.selectbox(
    "Assistant Role",
    ["Tutor", "Coder", "Mentor"],
    index=0,
)

if st.sidebar.button("Clear Memory"):
    memory.clear()
    st.session_state.messages = []
    st.success("Conversation memory cleared.")

if st.sidebar.button("Export Chat"):
    history = memory.get_history()
    json_str = json.dumps(history, indent=2)
    st.sidebar.download_button(
        "Download Chat History", json_str, file_name="chat_history.json"
    )

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

    # Initial greeting from JARVIS
    greeting = (
        "Hello! I am JARVIS, your personal AI assistant. "
        "Ask me anything, or choose a role in the sidebar "
        "(Tutor, Coder, Mentor) and I will adapt to help you."
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# ---------------------------------------------------------------------
# Typing Speed Test (interactive, with WPM & accuracy)
# ---------------------------------------------------------------------
if "typing_test" not in st.session_state:
    st.session_state.typing_test = {
        "active": False,
        "sentence": "",
        "start_time": 0.0,
    }

st.sidebar.subheader("Typing Speed Test")

typing_sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "Python programming is fun and easy to learn.",
    "Jarvis is a helpful voice assistant.",
    "Practice makes a man perfect.",
    "Learning never exhausts the mind.",
]

if st.sidebar.button("Start Typing Test"):
    sentence = random.choice(typing_sentences)
    st.session_state.typing_test["active"] = True
    st.session_state.typing_test["sentence"] = sentence
    st.session_state.typing_test["start_time"] = time.time()
    # Clear any previous input
    st.session_state["typing_input"] = ""

if st.session_state.typing_test["active"]:
    st.sidebar.info("Type the sentence below as fast and accurately as you can.")
    st.sidebar.code(st.session_state.typing_test["sentence"])
    user_typed = st.sidebar.text_area(
        "Your typed sentence",
        key="typing_input",
    )

    if st.sidebar.button("Submit Result"):
        end_time = time.time()
        elapsed = max(end_time - st.session_state.typing_test["start_time"], 0.001)
        words = len(user_typed.split())
        wpm = (words / elapsed) * 60 if words > 0 else 0.0

        reference = st.session_state.typing_test["sentence"]
        correct_chars = sum(1 for a, b in zip(user_typed, reference) if a == b)
        accuracy = (correct_chars / len(reference) * 100) if reference else 0.0

        st.sidebar.success(
            f"Speed: {wpm:.2f} WPM, Accuracy: {accuracy:.2f}%"
        )

        # Optional voice feedback using JARVIS TTS
        try:
            spoken = (
                f"Your typing speed is {wpm:.0f} words per minute "
                f"with {accuracy:.0f} percent accuracy."
            )
            # Uses the assistant's internal TTS helper
            assistant._speak(spoken)
        except Exception:
            pass

        # Reset test state
        st.session_state.typing_test["active"] = False

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
# here
# Initialize user input and mode so they're always defined
user_input = ""
input_mode = None  # "voice" or "text"

# Voice input button
if st.button("🎤 Speak"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    try:
        user_input = r.recognize_google(audio)
        st.success(f"You said: {user_input}")
        input_mode = "voice"
    except:
        st.error("Could not understand audio.")
        user_input = ""

# Text input (falls back to voice input if present)
user_text = st.chat_input("Ask JARVIS...")
if user_text is not None:
    user_input = user_text
    input_mode = "text"

# Respond
if user_input:
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        # Speak aloud only if the input came from the voice button
        speak_aloud = input_mode == "voice"
        response = assistant.respond(user_input, assistant_role, speak_aloud=speak_aloud)
        displayed = ""
        for char in response:  # streaming simulation
            displayed += char
            placeholder.markdown(displayed)

    # Save full assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": displayed})

