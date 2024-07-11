import streamlit as st
import pandas as pd
import random
import csv
import os

#### Functions

def read_csv():
    st.session_state.question_bank = []
    file_path = "question_bank.csv"  # Updated to match your GitHub file name
    try:
        df = pd.read_csv(file_path, sep='\t')
        st.write(f"Read {df.shape[0]} rows from {file_path}")
        st.session_state.question_bank = df.values.tolist()
        
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
        for x in topics_selected:
            if len(st.session_state.selected_questions) < 10:
                new_q = [x, random.randint(0, len(st.session_state.question_bank) - 1)]
                if new_q not in st.session_state.selected_questions:
                    st.session_state.selected_questions.append(new_q)
    
    st.session_state.q_index = 0
    st.session_state.score = 0

def iterate_question():
    st.session_state.q_index += 1 
    
    # update the score and show the message  
    user_answer_index = current_question_from_bank.index(user_answer)
    if (user_answer_index-1) == (ord(current_question_from_bank[5].upper()) - ord('A')):
        st.write("You selected the correct answer!")
        st.session_state.score += 1
    else:
        st.write("You selected the wrong answer. The correct one was number " + 
        str((ord(current_question_from_bank[5].upper()) - ord('A')) + 1) + " - " +
        f"{current_question_from_bank[(ord(current_question_from_bank[5].upper()) - ord('A')) + 1]}")

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

#### initialize global variables and session state

topics_list = ["Securities", "Securities-based derivatives contract", "Securities Industry Council", 
"Administering a financial benchmark", "Advising on corporate finance", "Advocate and solicitor", 
"Licensed trade repository", "Limited liability partnership", "Listing rules", "Product financing"
]

if "show_topic_choice" not in st.session_state:
    st.session_state.show_topic_choice = False
if "show_quiz_mode" not in st.session_state:
    st.session_state.show_quiz_mode = False
if "show_end_quiz" not in st.session_state:
    st.session_state.show_end_quiz = False
if "show_enter_name" not in st.session_state:
    st.session_state.show_enter_name = True
    
# read in question bank
read_csv()

#### Display Application Title
st.title("Quiz")
st.write(
    "Securities and Futures Act 2001"
)

### Display option:  Show topic selector
if st.session_state.show_topic_choice == True:
    options = st.multiselect(
        "What topics would you like to be quizzed on?",
        (topics_list)
    )
    
    topics_selected = []
    for x in topics_list:
        if x in options:
            topics_selected.append(topics_list.index(x))
    
    st.button("Start quiz", on_click=start_quiz)

### Display option:  Show quiz questions
if st.session_state.show_quiz_mode == True:
    current_question_list = st.session_state.selected_questions[st.session_state.q_index]
    current_question_from_bank = st.session_state.question_bank[current_question_list[1]]
    
    # Debug print
    st.write("Debug: current_question_from_bank =", current_question_from_bank)
    st.write("Debug: Length of current_question_from_bank =", len(current_question_from_bank))

    try:
        user_answer = st.radio(
            current_question_from_bank[0],
            [current_question_from_bank[1], current_question_from_bank[2], 
            current_question_from_bank[3], current_question_from_bank[4]]
        )
    except IndexError as e:
        st.error(f"An error occurred: {e}. The question structure might be incorrect.")
        st.write("current_question_from_bank:", current_question_from_bank)
        st.write("Length of current_question_from_bank:", len(current_question_from_bank))
    else:
        st.button("Enter", on_click=iterate_question)

### Display option:  Show quiz end with score, and a button to start next quiz
if st.session_state.show_end_quiz == True:
    st.write(f"Your score is {st.session_state.score}/{len(st.session_state.selected_questions)}.")
    st.button("Start another quiz", on_click=start_new_quiz)
    
    # Read the CSV file and show it as a table
    file_path = 'scores.csv'
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        st.dataframe(df)
    else:
        st.write("No scores recorded yet.")

### Display option:  User enters name
if st.session_state.show_enter_name == True:
    st.session_state.name = st.text_input("Please enter your name")
    st.button("Next", on_click=name_to_topic)
