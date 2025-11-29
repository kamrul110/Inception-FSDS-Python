import speech_recognition as sr 
import pyttsx3 
import logging 
import os 
import datetime 
import wikipedia 
import webbrowser 
import subprocess 
import google.generativeai as genai
import time
import random
import threading
import pyautogui
# Logging configuration 
LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR,LOG_FILE_NAME)

logging.basicConfig(
    filename=log_path,
    format = "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level= logging.INFO
)


# Activating voice 
engine = pyttsx3.init("sapi5") 
engine.setProperty('rate', 170)#voice er speed komanor jnno
voices = engine.getProperty("voices")
engine.setProperty('voice', voices[0].id)

engine_lock= threading.Lock()

# this is speak function.. for text → voice
def speak(text):
    """This function converts text to voice

    Args:
        text
    returns:
        voice
    """
    with engine_lock:
        engine.say(text)
        engine.runAndWait()
    logging.info(f"Assistant said: {text}")


#This is Listen Function:
def takeCommand():
    """This function takes command & recognize

    Returns:
        text as query
    """
    r = sr.Recognizer()
    
    
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...") 
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        logging.info(f"User said: {query}")
    except Exception as e:
        logging.info(e)
        print("Say that again please")
        return "None"
    
    return query  



def greeting():
    hour = (datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning sir! How are you doing?")
    elif hour>=12 and hour<=18:
        speak("Good Afternoon sir! How are you doing?")
    else:
        speak("Good Evening sir! How are you doing?")
    

    speak("I am Jarvis. Please tell me how may I help you today?")

# screenshot
def screenshot():
    img=pyautogui.screenshot()
    img.save("screenshot.png")
    speak("Screenshot taken")
    logging.info(f"Screenshot taken and saved")
# typing test
def typing_speed_test():
    sentence_list=[
        "The quick brown fox jumps over the lazy dog",
        "Python programming is fun and easy to learn",
        "Jarvis is a helpful voice assistant",
        "Practice makes a man perfect",
        "Learning never exhausts the mind"
    ]
    sentence = random.choice(sentence_list)
    speak("Typing Test started. Type this sentence ")
    print(f"\nType this: \n{sentence}\n")
    start_time = time.time()
    user_input = input("Your input: ")
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    words = len(user_input.split())
    wpm = (words/ elapsed_time) * 60
    
    correct_char = 0
    length = min(len(user_input),len(sentence))
    
    for i in range(length):
        if user_input[i] == sentence[i]:
            
            correct_char +=1
    accuracy = (correct_char/ len(sentence))*100
    speak(f"Your typing speed is {wpm: 2f} words per minute with {accuracy:2f} percent accuracy")   
    print(f"Typing speed {wpm:2f}WPM, Accuracy:{accuracy:.2f}%\n")
    logging.info(f"Typing speed test completed {wpm:2f} Accuracy:{accuracy:.2f}%\n")
#timer function.voice command example
# set a timer for 1 minutes
def set_timer(query):
    for word in query.split():
        if word.isdigit():
            minutes = int(word)
            break
    else:
        speak("sorry, i could not find the time")
        return
        
    speak(f"{minutes} minutes timer started")
    
    def run_timer():
        time.sleep(minutes * 60)
        with engine_lock:
            engine.say("sir, your timer is complete")
            engine.runAndWait()
    threading.Thread(target = run_timer,daemon=True).start()    


    
def gemini_model_response(user_input):
    GEMINI_API_KEY = "AIzaSyCVkQixMpZAEGll-UxaDdOHiczNkXYQECg"
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Your name is JARVIS, You act like JARVIS. Answar the provided question in short, Question:{user_input}"
    response= model.generate_content(prompt)
    result = response.text
    return result

    
greeting()

    
    
    
while True:
    query = takeCommand().lower()
    print(query)
    
    if "your name" in query:
        speak("My name is Jarvis")
        logging.info("User asked for assistant's name.")
    
       
        
    # weather
    elif "weather" in query:
        speak("opening weather details")
        webbrowser.open("https://www.google.com/search?q=weather") 
        logging.info("user requested weather info")
        
        
        
    #speed test
    elif "typing test" in query:
        typing_speed_test()  
        
        
        
          
    # news
    elif "news" in query:
        speak("Opening top news")
        webbrowser.open("https://news.google.com")
        logging.info("user requested news")
    
    
    
    # ss
    elif "take screenshot" in query:
        screenshot()
        
        
            
    #timer
    elif "set a timer" in query:
        set_timer(query)    
  
    elif "time" in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"Sir the time is {strTime}")
        logging.info("User asked for current time.")
    
    elif "wikipedia" in query:
        speak("Searching Wikipedia...")
        query = query.replace("wikipedia", "")
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        speak(results)
        logging.info("User requested information from Wikipedia.")
    
    
    #open YouTube search query
    elif "youtube" in query:
        speak("Opening YouTube for you.")
        query = query.replace("youtube", "")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        logging.info("User requested to search on YouTube.")
        
    #open Google     
    elif "open google" in query:
        speak("ok sir. please type here what do you want to read")
        webbrowser.open("google.com")
        logging.info("User requested to open Google.")  
        
        
# 
    elif "exit" in query:
        speak("Thank you for your time sir. Have a great day ahead!")
        logging.info("User exited the program.")
        exit()


    else:
        response= gemini_model_response(query)
        speak(response)
        logging.info("User asked for others question")    
    