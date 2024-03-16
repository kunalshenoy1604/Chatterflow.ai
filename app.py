import streamlit as st
from langchain.schema import HumanMessage, SystemMessage, AIMessage
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

chat = ChatOpenAI(temperature=0.5)
if 'flowmessages' not in st.session_state:
    st.session_state['flowmessages'] = [SystemMessage(content="You are a Professional AI Assistant")]

st.set_page_config(page_title="Conversational Q&A ChatBot")


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
        .typewriter-text {
            overflow: hidden; /* Ensures the content is not revealed until the animation */
            border-right: .15em solid green; /* The typwriter cursor */
            white-space: nowrap; /* Keeps the content on a single line */
            margin: 0 auto; /* Gives that scrolling effect as the typing happens */
            letter-spacing: .15em; /* Adjust as needed */
            font-size: 38px;
            animation:
              typing 3.5s steps(40, end),
              blink-caret .75s step-end infinite;
        }
        /* The typing effect */
        @keyframes typing {
          from { width: 0 }
          to { width: 100% }
        }
        /* The typewriter cursor effect */
        @keyframes blink-caret {
          from, to { border-color: transparent }
          50% { border-color: green; }
        }
        </style>
    """, unsafe_allow_html=True)


set_custom_styles()

st.markdown("<h1 class='typewriter-text' style='color: #00FF00'>Hey, Welcome to ChatterFlow.ai</h1>", unsafe_allow_html=True)


def listen_voice():
    with sr.Microphone() as source:
        st.write("Listening....")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            st.write(f"You said :- {text}")
            return text
        except sr.UnknownValueError:
            st.error("Could not understand your voice. Please try again.")
        except sr.RequestError as e:
            st.error(f"Could not request results from the speech recognition service;{e}")


def get_chatmodel_response(question):
    st.session_state['flowmessages'].append(HumanMessage(content=question))
    answer = chat(st.session_state['flowmessages'])
    if answer is not None and hasattr(answer, 'content'):
        st.session_state['flowmessages'].append(AIMessage(content=answer.content))
        feedback_response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=f"Provide feedback on the following text: \"{question}\"",
            max_tokens=50
        )

        feedback = feedback_response.choices[0].text.strip()

        translation_response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=f"Provide translation on the following text to Professional English, Hindi and Spanish: \"{question}\"",
            max_tokens=350
        )
        translation = translation_response.choices[0].text.strip()
        return answer.content, feedback, translation
    else:
        return "I'm sorry, I could not generate a response. Please try again!", "", ""


input = st.text_input("Type your question here:", key="input")

if st.button("Speak Now"):
    spoken_text = listen_voice()
    if spoken_text:
        response, feedback, translation = get_chatmodel_response(spoken_text)
        st.subheader("The Response is:")
        st.write(response)
        st.subheader("Language Feedback:")
        st.write(feedback)
        st.subheader("Translation:")
        st.write(translation)
        engine.say(response)
        if hasattr(engine, '_inLoop') and engine._inLoop:
            engine.endLoop()
        engine.runAndWait()

if st.button("Ask the Question"):
    response, feedback, translation = get_chatmodel_response(input)
    st.subheader("The response is:")
    st.write(response)
    st.subheader("Language Feedback:")
    st.write(feedback)
    st.subheader("Translation:")
    st.write(translation)

if 'openai.api_key' in st.session_state:
    del st.session_state['openai.api_key']


