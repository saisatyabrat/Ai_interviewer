import streamlit as st
import os
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

# Read API Key
with open("keys/.gemini_travel.txt", "r") as f:
    api_key = f.read().strip()

# Streamlit UI
st.title("Intelligent Hiring Assistant")
st.write("Provide your details to receive relevant interview questions.")

# Gemini AI Model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
# output parser
parser = StrOutputParser()
# User Inputs
name = st.text_input("Enter your full name :- ")
email = st.text_input("Enter your E-mail :- ")
phn_num = st.text_input("Enter your contact number :- ")
experience = st.number_input("Enter your years of experience :- ",min_value=0,step=1)
position = st.text_input("Enter your desired position :- ")
location = st.text_input("Enter current location :- ",key="location")
skill = st.text_input("Enter your tech stack :- ")

# Initialize session state for storing questions & answers
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = [""] * 5


if st.button("Generate interview questions"):
    if not (name.strip() and email.strip() and phn_num.strip() and str(experience).strip() and position.strip() and location.strip() and skill.strip()):
        st.warning("!!!!!Please fill out all required fields!!!!!")
    else:
        chat_template = ChatPromptTemplate.from_messages([
                ("system", """You are an AI hiring assistant.
                Generate 3 to 5 technical interview questions for a candidate applying for {position}
                with experience in {skill}. Ensure the questions are relevant and diverse. Based on {experience}
                question should be tricky"""),
                ("human", "Please generate the questions.")
            ])

        # Pipeline
        chain = chat_template | chat_model | parser

        raw_input = {
            'position' : position,
            'skill' : skill,
            'experience':experience
        }

        response = chain.invoke(raw_input)
        
        if response.strip():
            # Extract questions properly (handling different AI response formats)
            extracted_questions = [q.strip() for q in response.split("\n") if q.strip() and q[0].isdigit()]
            st.session_state.questions = extracted_questions[:5]  # Ensure max 5 questions
        else:
            st.warning("⚠️ No questions generated. Try again!")

# Display Questions
if st.session_state.questions:
    st.subheader("📌 Interview Questions:")
    for i, question in enumerate(st.session_state.questions):
        st.write(f"**Q{i+1}:** {question}")
        st.session_state.answers[i] = st.text_area(f"Your Answer for Q{i+1}:", key=f"ans_{i}")

# Evaluate Answers

if st.button("Evaluate My Answer"):
    if all(ans.strip() == "" for ans in st.session_state.answers):
        st.warning("⚠️ Please provide answers before evaluation!")
    else:
        eval_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI hiring assistant evaluating a candidate's responses.
            Provide a constructive assessment, highlighting strengths and improvement areas."""),
            ("human", "Here are my answers:\n{answers}")
        ])
        # Pipeline
        eval_chain = eval_prompt | chat_model | parser

        # Format answers into a string
        answers_text = "\n".join([f"Q{i+1}: {ans}" for i, ans in enumerate(st.session_state.answers) if ans])

        eval_response = eval_chain.invoke({"answers": answers_text})

        st.subheader("📝 Evaluation Feedback:")
        st.write(eval_response)