import streamlit as st
import pandas as pd
import random
import csv
import os

def read_csv():
    file_path = "question_bank.csv"
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            st.session_state.question_bank = list(reader)
        st.write(f"Read {len(st.session_state.question_bank)} rows from {file_path}")
        
        # Extract unique topics from the question bank
        st.session_state.topics_list = list(set(row[0] for row in st.session_state.question_bank[1:]))  # Assuming first row is header
        
        # Debug print
        st.write("Debug: First few rows of question_bank:", st.session_state.question_bank[:2])
        st.write("Debug: Number of questions loaded:", len(st.session_state.question_bank))
        st.write("Debug: Available topics:", st.session_state.topics_list)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"An error occurred while reading {file_path}: {e}")

def parse_question(question_row):
    if len(question_row) >= 7:
        return {
            'topic': question_row[0],
            'question': question_row[1],
            'correct_answer': question_row[2],
            'wrong_answers': question_row[3:6],
            'explanation': question_row[6] if len(question_row) > 6 else ""
        }
    return None

def name_to_topic():
    st.session_state.show_topic_choice = True
    st.session_state.show_enter_name = False

def start_quiz():
    st.session_state.show_topic_choice = False
    st.session_state.show_quiz_mode = True
    st.session_state.show_end_quiz = False
    st.session_state.selected_questions = []
    
    # Filter questions based on selected topics
    filtered_questions = [q for q in st.session_state.question_bank[1:] if q[0] in st.session_state.selected_topics]
    
    if len(filtered_questions) < 10:
        st.error(f"Not enough questions for selected topics. Only {len(filtered_questions)} questions available.")
        return
    
    while len(st.session_state.selected_questions) < 10:
        new_q = random.randint(0, len(filtered_questions) - 1)
        if new_q not in st.session_state.selected_questions:
            st.session_state.selected_questions.append(new_q)
    
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.shuffled_options = []
    st.session_state.current_answer = None

def iterate_question():
    st.session_state.q_index += 1
    st.session_state.current_answer = None
    if st.session_state.q_index == len(st.session_state.selected_questions):
        st.session_state.show_quiz_mode = False
        st.session_state.show_end_quiz = True
        save_score()

def save_score():
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

# Initialize session state variables
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
if "topics_list" not in st.session_state:
    st.session_state.topics_list = []
if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "name" not in st.session_state:
    st.session_state.name = ""
if "current_answer" not in st.session_state:
    st.session_state.current_answer = None
if "shuffled_options" not in st.session_state:
    st.session_state.shuffled_options = []
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# Display Application Title
st.title("Quiz")
st.write("Securities and Futures Act 2001")

# Read in question bank
if "question_bank" not in st.session_state or not st.session_state.question_bank:
    read_csv()

# Display option: User enters name
if st.session_state.show_enter_name:
    st.session_state.name = st.text_input("Please enter your name", value=st.session_state.name)
    if st.button("Next", key="enter_name"):
        if st.session_state.name:  # Only proceed if a name is entered
            st.session_state.show_enter_name = False
            st.session_state.show_topic_choice = True
            st.experimental_rerun()  # Force a rerun to update the UI

# Display option: Show topic selector
elif st.session_state.show_topic_choice:
    options = st.multiselect(
        "What topics would you like to be quizzed on?",
        st.session_state.topics_list
    )
    
    if st.button("Start quiz", key="start_quiz"):
        if options:  # Only start the quiz if at least one topic is selected
            st.session_state.selected_topics = options
            start_quiz()
            st.experimental_rerun()  # Force a rerun to update the UI
        else:
            st.error("Please select at least one topic.")

# Display option: Show quiz questions
elif st.session_state.show_quiz_mode:
    filtered_questions = [q for q in st.session_state.question_bank[1:] if q[0] in st.session_state.selected_topics]
    current_question_from_bank = filtered_questions[st.session_state.selected_questions[st.session_state.q_index]]
    
    parsed_question = parse_question(current_question_from_bank)
    if parsed_question:
        if len(st.session_state.shuffled_options) <= st.session_state.q_index:
            options = [parsed_question['correct_answer']] + parsed_question['wrong_answers']
            random.shuffle(options)
            st.session_state.shuffled_options.append(options)
        else:
            options = st.session_state.shuffled_options[st.session_state.q_index]
        
        st.write(f"Question {st.session_state.q_index + 1} of {len(st.session_state.selected_questions)}")
        st.write(parsed_question['question'])
        
        user_answer = st.radio("Select your answer:", options, index=None, key=f"question_{st.session_state.q_index}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Answer", key=f"submit_{st.session_state.q_index}"):
                if user_answer == parsed_question['correct_answer']:
                    st.session_state.feedback = "Correct!"
                    st.session_state.score += 1
                else:
                    st.session_state.feedback = f"Incorrect. The correct answer is: {parsed_question['correct_answer']}"
        
        with col2:
            if st.button("Next", key=f"next_{st.session_state.q_index}"):
                st.session_state.feedback = ""
                iterate_question()
                st.experimental_rerun()  # Force a rerun to update the UI
        
        if st.session_state.feedback:
            st.write(st.session_state.feedback)
    else:
        st.error("Unable to parse the current question. Skipping to the next one.")
        iterate_question()
        st.experimental_rerun()  # Force a rerun to update the UI

# Display option: Show quiz end with score, and a button to start next quiz
elif st.session_state.show_end_quiz:
    st.write(f"Your score is {st.session_state.score}/{len(st.session_state.selected_questions)}.")
    if st.button("Start another quiz", key="start_new_quiz"):
        start_new_quiz()
        st.experimental_rerun()  # Force a rerun to update the UI
    
    # Read the CSV file and show it as a table
    file_path = 'scores.csv'
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        st.dataframe(df)
    else:
        st.write("No scores recorded yet.")
