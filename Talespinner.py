import os
import json
import pyttsx3  # Text-to-speech engine
import time
import speech_recognition as sr
from groq import Groq

# Initialize Groq client with API key
client = Groq(api_key="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")

engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Slightly slower for storytelling

# Set voice to female if available
voices = engine.getProperty('voices')
female_voice_found = False
for voice in voices:
    if "zira" in voice.name.lower() or "zira" in voice.id:  # Check for a female-sounding voice
        engine.setProperty('voice', voice.id)
        female_voice_found = True
        break

# If no female voice was found, keep the first available voice
if not female_voice_found:
    engine.setProperty('voice', voices[0].id)

# Dictionary to remember user info
user_memory = {}

def groq_generate_text(prompt):
    """Fetch generated text from the Groq API."""
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def speak(text):
    """Convert text to speech with pauses to enhance storytelling effect."""
    phrases = text.split(". ")
    for phrase in phrases:
        engine.say(phrase)
        engine.runAndWait()
        time.sleep(0.5)  # Slight pause between phrases

def listen():
    """Capture user input through microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... You can speak freely until you pause.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            speak("I didn't catch that. Could you repeat, please?")
            return listen()  # Retry listening if there was an error

def initialize_user():
    """Introduce Talespinner, ask for the user’s name, and explain the purpose of the interaction."""
    if "name" not in user_memory:
        speak("Greetings, wanderer. I am Talespinner, your guide through realms of mystery.")
        speak("To begin our adventure, may I know your name?")
        
        user_name = listen()
        if user_name:
            user_memory["name"] = user_name
            speak(f"Welcome, {user_name}. I sense grand adventures ahead!")
        else:
            user_memory["name"] = "friend"
            speak("I'll call you 'friend' then. Let us journey into a tale!")

def choose_story_length():
    """Prompt the user to select a story length and return the appropriate setting."""
    speak("Before we begin, would you like a short, medium, or long story?")
    while True:
        length_choice = listen()
        if "short" in length_choice:
            return "short"
        elif "medium" in length_choice:
            return "medium"
        elif "long" in length_choice:
            return "long"
        else:
            speak("Please say 'short,' 'medium,' or 'long' to choose the story length.")

def tell_story():
    """Engage the user in an interactive, AI-driven story with options to interact or interrupt."""
    initialize_user()
    user_name = user_memory.get("name", "friend")
    
    while True:
        # Select story length
        story_length = choose_story_length()
        length_setting = {"short": "a brief story", "medium": "a moderate-length story", "long": "an elaborate tale"}[story_length]

        speak(f"{user_name}, imagine a place you yearn to explore, or a mystery you wish to uncover. Tell me about it.")
        user_topic = listen()
        
        # Exit conditions
        if user_topic and user_topic in ["exit", "stop", "goodbye"]:
            speak(f"Farewell, {user_name}. I hope you return for another adventure!")
            break

        if user_topic:
            story_prompt = (
                f"Create an {length_setting} about {user_name} exploring {user_topic}. "
                f"Include magical challenges, two clear choices at interactive points, and a satisfying conclusion."
            )

            # Fetch the initial story segment
            story_text = groq_generate_text(story_prompt)
            
            # Split story into sentences and create interactive choice points
            sentences = story_text.split(". ")
            for sentence in sentences:
                if "?" in sentence:
                    # Offer two options to the user
                    speak(sentence.strip() + " You have two choices.")
                    speak("Option one or option two? Say 'one' or 'two'.")
                    
                    while True:
                        user_response = listen()

                        # Check if the user wants to exit mid-story
                        if user_response in ["exit", "stop", "goodbye"]:
                            speak(f"Alright, {user_name}, until next time!")
                            return

                        # Handle choices
                        if "one" in user_response:
                            choice = "Option one selected"
                            break
                        elif "two" in user_response:
                            choice = "Option two selected"
                            break
                        else:
                            speak("Please say 'one' or 'two'.")

                    # Add user response to the story context and fetch the next story continuation
                    story_prompt += f" {choice}. Continue the story with new options for {user_name}."
                    story_text = groq_generate_text(story_prompt)
                else:
                    speak(sentence.strip())
            
            # Conclude the story
            speak(f"And so, {user_name}, concludes your adventure in the realm of {user_topic}.")
            speak("Would you like to hear another story? Just say 'exit' if you'd like to stop.")

# Main Chat Loop
def main_chat_loop():
    global user_memory
    # Load memory if available
    try:
        with open("user_memory.json", "r") as memory_file:
            user_memory = json.load(memory_file)
    except FileNotFoundError:
        user_memory = {}

    try:
        tell_story()
    finally:
        # Save memory to file
        with open("user_memory.json", "w") as memory_file:
            json.dump(user_memory, memory_file)

if __name__ == "__main__":
    main_chat_loop()
