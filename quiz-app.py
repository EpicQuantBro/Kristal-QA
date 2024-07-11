import streamlit as st
import pandas as pd
import random
import csv
import os
import ast

#### Functions

def read_csv():
    file_path = "question_bank.csv"
    try:
        df = pd.read_csv(file_path, header=None)
        st.write(f"Read {df.shape[0]} rows from {file_path}")
        st.session_state.question_bank = df[0].tolist()  # Store each row as a string
        
        # Debug print
        st.write("Debug: First few rows of question_bank:", st.session_state.question_bank[:2])
        st.write("Debug: Number of questions loaded:", len(st.session_state.question_bank))
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"An error occurred while reading {file_path}: {e}")

def name_to_topic():
    st.session_state.show_topic_choice = True
    st.session_state.show_enter_name = False

def start_quiz():
    st.session_state.show_topic_choice = False
    st.session_state.show_quiz_mode = True
    st.session_state.show_end_quiz = False
    st.session_state.selected_questions = []
    
    if len(st.session_state.question_bank) < 10:
        st.error(f"Not enough questions in the bank. Only {len(st.session_state.question_bank)} questions available.")
        return
    
    while len(st.session_state.selected_questions) < 10:
        new_q = random.randint(0, len(st.session_state.question_bank) - 1)
        if new_q not in st.session_state.selected_questions:
            st.session_state.selected_questions.append(new_q)
    
    st.session_state.q_index = 0
    st.session_state.score = 0

def iterate_question():
    question_data = ast.literal_eval(current_question_from_bank)
    
    # Find the index of the user's answer
    user_answer_index = next((i for i, answer in enumerate(question_data[2:6]) if answer == user_answer), None)
    
    # Check if the answer is correct
    if user_answer_index == 0:  # Correct answer is always at index 2 in the question data
        st.write("You selected the correct answer!")
        st.session_state.score += 1
    else:
        st.write(f"You selected the wrong answer. The correct one was: {question_data[2]}")

    st.session_state.q_index += 1

    if st.session_state.q_index == len(st.session_state.selected_questions):
        # this was the last question, so add the score to csv and move to end_quiz display mode
        st.session_state.show_quiz_mode = False
        st.session_state.show_end_quiz = True

        # Add new row to the CSV file
        file_path = 'scores.csv'
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['Date', 'Name', 'Score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'Date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'Name': st.session_state.name,
                'Score': st.session_state.score
            })

def start_new_quiz():
    st.session_state.show_topic_choice = False
    st.session_state.show_quiz_mode = False
    st.session_state.show_end_quiz = False
    st.session_state.show_enter_name = True

#### Initialize session state variables
if "show_topic_choice" not in st.session_state:
    st.session_state.show_topic_choice = False
if "show_quiz_mode" not in st.session_state:
    st.session_state.show_quiz_mode = False
if "show_end_quiz" not in st.session_state:
    st.session_state.show_end_quiz = False
if "show_enter_name" not in st.session_state:
    st.session_state.show_enter_name = True
if "question_bank" not in st.session_state:
    st.session_state.question_bank = []
if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "name" not in st.session_state:
    st.session_state.name = ""

# Define topics_list
topics_list = ["Securities", "Securities-based derivatives contract", "Securities Industry Council", 
"Administering a financial benchmark", "Advising on corporate finance", "Advocate and solicitor", 
"Licensed trade repository", "Limited liability partnership", "Listing rules", "Product financing"]

#### Display Application Title
st.title("Quiz")
st.write("Securities and Futures Act 2001")

# Read in question bank
read_csv()

### Display option: Show topic selector
if st.session_state.show_topic_choice:
    options = st.multiselect(
        "What topics would you like to be quizzed on?",
        (topics_list)
    )
    
    topics_selected = [topics_list.index(x) for x in options if x in topics_list]
    
    st.button("Start quiz", on_click=start_quiz)

### Display option: Show quiz questions
if st.session_state.show_quiz_mode:
    current_question_from_bank = st.session_state.question_bank[st.session_state.selected_questions[st.session_state.q_index]]
    
    # Debug print
    st.write("Debug: current_question_from_bank =", current_question_from_bank)
    st.write("Debug: Length of current_question_from_bank =", len(current_question_from_bank))

    try:
        question_data = ast.literal_eval(current_question_from_bank)
        user_answer = st.radio(
            question_data[1],  # Question text
            question_data[2:6]  # Answer options
        )
        st.button("Enter", on_click=iterate_question)
    except (ValueError, SyntaxError, IndexError) as e:
        st.error(f"An error occurred while parsing the question: {e}")
        st.write("current_question_from_bank:", current_question_from_bank)

### Display option: Show quiz end with score, and a button to start next quiz
if st.session_state.show_end_quiz:
    st.write(f"Your score is {st.session_state.score}/{len(st.session_state.selected_questions)}.")
    st.button("Start another quiz", on_click=start_new_quiz)
    
    # Read the CSV file and show it as a table
    file_path = 'scores.csv'
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        st.dataframe(df)
    else:
        st.write("No scores recorded yet.")

### Display option: User enters name
if st.session_state.show_enter_name:
    st.session_state.name = st.text_input("Please enter your name")
    st.button("Next", on_click=name_to_topic)
