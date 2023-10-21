from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from streamlit_chat import message
from utils import *
import os
import pyttsx3
import speech_recognition as sr
import threading
import time
from gtts import gTTS
import playsound
from streamlit_card import card
import base64
from streamlit_option_menu import option_menu
import requests
from PIL import Image
from io import BytesIO




filepath='Home.png'
with open(filepath, "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data)
data = "data:image/png;base64," + encoded.decode("utf-8")

from streamlit_card import card

PAGE_TITLE: str = "AI Talks"
PAGE_ICON: str = "🤖"
LANG_EN: str = "En"
LANG_RU: str = "Fr" # You can set your app title here

location_map=['washroom']

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.title('🤖 Parklink System Chatbot')

selected_lang = option_menu(
    menu_title="",
    options=[LANG_EN, LANG_RU, ],
    icons=["globe2", "translate"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)
# Store the image URL in session state
if 'image_url' not in st.session_state:
    st.session_state['image_url'] = "url"

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

os.environ["OPENAI_API_KEY"]="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"

llm = ChatOpenAI(model_name="gpt-3.5-turbo")


if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)


system_msg_template = SystemMessagePromptTemplate.from_template(template=f"""You are a chatbot for Parklink-systems. Your main goal is to help customers in resolving their queries.
                                                                Answer the question as truthfully as possible using the provided context, If a user asks for washroom or its location just give the url path to jpg file from the context as it is.
'""")


human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

# Create a pyttsx3 object for text to speech
engine = pyttsx3.init()

# Create a speech recognition object for speech to text
r = sr.Recognizer()

# Define a function to listen to the user's voice and return the text
def listen():
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        # Listen for the user's voice
        print("Listening...")
        audio = r.listen(source)
    try:
        # Recognize the user's voice using Google Speech Recognition
        text = r.recognize_google(audio)
        # Print the user's input
        print(f"You said: {text}")
        # Return the text
        return text
    except:
        # If there is an error, return None
        print("Sorry, I could not understand you.")
        return None

# Define a function to speak the chatbot's response
def speak(text):
    print(f"AI said: {text}")
    tts = gTTS(text=text, lang='en',tld='ca')
    tts.save("good.mp3")
    playsound.playsound('good.mp3')
    os.remove('good.mp3')    

# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()

if st.button("Voice-Search 🎤"):
# Listen to the user's input and store it in a variable
    query = listen()
    if query:
        with st.spinner("processing..."):
            conversation_string = get_conversation_string()
            # st.code(conversation_string)
            refined_query = query_refiner(conversation_string, query)
            st.subheader("Refined Query:")
            st.write(refined_query)
            context = find_match(refined_query)
            print(context)  
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
            if "content/images" in response and "jpg" in response:
                speak("Here is the map for the desired location:")
            else:
                speak(response)
            
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 


     

with textcontainer:
    query = st.text_input("Query: ", key="input")
    
    if query:
        with st.spinner("typing..."):
            conversation_string = get_conversation_string()
            # st.code(conversation_string)
            refined_query = query_refiner(conversation_string, query)
            st.subheader("Refined Query:")
            st.write(refined_query)
            context = find_match(refined_query)
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 

with response_container:
    print(st.session_state['responses'])
    print(response_container)
    if st.session_state['responses']:
        print("Responses Here")
        for i in range(len(st.session_state['responses'])):
            if "content/images" in st.session_state['responses'][i] and st.session_state['image_url']!="url":
                st.image(st.session_state['image_url'], caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')
            
        
        try:
            print(st.session_state['responses'])
            last_element=st.session_state['responses'][-1]
            if 'content/images' in last_element and '.jpg' in last_element:                
                print("True")
                with st.chat_message("Response:"):
                    contentIndex=st.session_state['responses'][-1].index('content')
                    jpgIndex=st.session_state['responses'][-1].index('.jpg')
                    url=st.session_state['responses'][-1][contentIndex:jpgIndex+4]

                    if 'image_url' in st.session_state and st.session_state['image_url']=="url":
                        st.session_state['image_url'] = url
                        st.image(st.session_state['image_url'], caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
         
        except:
            
            print("Exception Occured")
          