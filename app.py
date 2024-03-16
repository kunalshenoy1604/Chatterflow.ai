import streamlit as st
from langchain.schema import HumanMessage, SystemMessage,AIMessage
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import openai 

load_dotenv()

openai.api_key = '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'
engine = pyttsx3.init()
engine.setProperty('rate', 150)    
engine.setProperty('volume', 0.9)

r = sr.Recognizer()

chat=ChatOpenAI(temperature=0.5)
if 'flowmessages' not in st.session_state:
    st.session_state['flowmessages']=[SystemMessage(content="You are a Professional AI Assistant")]

st.set_page_config(page_title="Conversational Q&A ChatBot")
st.header("Hey, Welcome to ChatterFlow.ai")

def set_custom_styles():
    st.markdown("""
        <style>
        .stTextInput>div>div>input{
            padding: 10px;
            font-size: 16px;
        }
        .stButton>button{
            width: 100%;
            border-radius: 5px;
            padding: 15px;
            font-size: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
set_custom_styles()

def listen_voice():
    with sr.Microphone() as source:
        st.write("Listening....")
        audio = r.listen(source)
        try:
            text=r.recognize_google(audio)
            st.write(f"You said :- {text}")
            return text
        except sr.UnknownValueError:
            st.error("Could not understand your voice. Please try again.")
        except sr.RequestError as e:
            st.error(f"Could not request results from the speech recognition service;{e}")

def get_chatmodel_response(question):
        st.session_state['flowmessages'].append(HumanMessage(content=question))
        answer=chat(st.session_state['flowmessages'])
        if answer is not None and hasattr(answer,'content'):
            st.session_state['flowmessages'].append(AIMessage(content=answer.content))
            feedback_response=openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=f"Provide feedback on the following text: \"{question}\"",
                max_tokens=50
            )
            
            feedback=feedback_response.choices[0].text.strip()
            
            translation_response=openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=f"Provide translation on the following text to Professional English, Hindi and Spanish: \"{question}\"",
                max_tokens=350
            )
            translation=translation_response.choices[0].text.strip()
            return answer.content,feedback, translation
        else:
            return "I'm sorry, I could not generate a response. Please try again!","",""
    
input=st.text_input("Type your question here:", key="input")

if st.button("Speak Now"):
    spoken_text = listen_voice()
    if spoken_text:
        response,feedback,translation=get_chatmodel_response(spoken_text)
        st.subheader("The Response is:")
        st.write(response)
        st.subheader("Language Feedback:")
        st.write(feedback)
        st.subheader("Translation:")
        st.write(translation)
        engine.say(response)
        if hasattr(engine,'_inLoop') and engine._inLoop:
            engine.endLoop()
        engine.runAndWait()

if st.button("Ask the Question"):
    response,feedback,translation=get_chatmodel_response(input)
    st.subheader("The response is:")
    st.write(response)
    st.subheader("Language Feedback:")
    st.write(feedback)
    st.subheader("Translation:")
    st.write(translation)