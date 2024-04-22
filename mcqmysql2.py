from flask import Flask, render_template, request, send_file, jsonify
import json
import mysql.connector
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.utils import read_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from src.mcqgenerator.logger import logging
from typing import Dict
import os
import requests
import logging
import random


# Suppress favicon logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
   'user': 'root',
   'password': 'DFSmt@103',
   'host': 'localhost',
   'database': 'mydatabase',
   'raise_on_warnings': True
}

quiz_dict: dict = None
# Function to establish a database connection
def get_db_connection():
   try:
       return mysql.connector.connect(**DB_CONFIG)
   except mysql.connector.Error as err:
       print(f"Error connecting to the database: {err}")
       return None

# Function to close a database connection
def close_db_connection(connection):
   if connection:
       connection.close()

# def insert_mcq(connection, question_dict):
#     if connection:
#         cursor = connection.cursor()
#         question = question_dict["mcq"]
#         correct_answer = question_dict["correct"]
#         options = question_dict["options"]

#         # Extract choices with key and choice
#         choice_keys = list(options.keys())
#         if len(choice_keys) < 4:
#             logging.error(f"Insufficient choices for MCQ: {question_dict}")
#             return

#         choice1 = f"{choice_keys[0]}: {options.get(choice_keys[0], '')}"
#         choice2 = f"{choice_keys[1]}: {options.get(choice_keys[1], '')}"
#         choice3 = f"{choice_keys[2]}: {options.get(choice_keys[2], '')}"
#         choice4 = f"{choice_keys[3]}: {options.get(choice_keys[3], '')}"

#         # SQL query to insert data into the table
#         sql = "INSERT INTO mcqtable (question, choice1, choice2, choice3, choice4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)"
#         try:
#             cursor.execute(sql, (question, choice1, choice2, choice3, choice4, correct_answer))
#             connection.commit()
#             logging.info(f"MCQ inserted successfully: {question_dict}")
#         except mysql.connector.Error as e:
#             logging.error(f"Error inserting MCQ: {e}")
#             connection.rollback()

#         cursor.close()

def insert_mcq(connection, question_dict):
    if connection:
        cursor = connection.cursor()
        question = question_dict["mcq"]
        correct_answer = question_dict["options"][question_dict["correct"]]
        options = list(question_dict["options"].values())

        # Shuffle the options to randomize the order
        random.shuffle(options)

        # Assign the options to the respective columns
        choice1, choice2, choice3, choice4 = options

        # SQL query to insert data into the table
        sql = "INSERT INTO mcqtable (question, choice1, choice2, choice3, choice4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(sql, (question, choice1, choice2, choice3, choice4, correct_answer))
            connection.commit()
            logging.info(f"MCQ inserted successfully: {question_dict}")
        except mysql.connector.Error as e:
            logging.error(f"Error inserting MCQ: {e}")
            connection.rollback()

        cursor.close()


# Rest of your Flask routes and functions
with open("Response.json", 'r') as file:
   RESPONSE_JSON = json.load(file)


@app.route('/api/pdf_files', methods=['GET'])
def get_pdf_files():
   try:
       # Connect to the database
       connection = get_db_connection()

       # Create a cursor
       cursor = connection.cursor()

       # Execute the MySQL query to retrieve PDF file information
       cursor.execute("SELECT id, file_name, file_path FROM pdf_metadata")

       # Fetch all rows
       pdf_files = cursor.fetchall()

       # Close the cursor
       cursor.close()

       # Create a list of dictionaries containing the data
       pdf_data = []
       for file in pdf_files:
           pdf_data.append({
               'id': file[0],
               'file_name': file[1],
               'full_url': f"http://localhost:8000/{file[2]}" # Assuming file_path contains relative paths
           })
           #print(f"Constructed URL: {pdf_data[-1]['full_url']}")

       # Close the database connection
       close_db_connection(connection)

       return jsonify(pdf_data)

   except mysql.connector.Error as e:
       print(f"Error fetching PDF files from database: {e}")
       return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET', 'POST'])
def home():
   print("Entered home route") # This will print when the route is entered
   error = None
   success = None
   #quiz_dict = None
   quiz_dict: dict = None
   pdf_files = []

   # Fetch the PDF file list from the server
   try:
       response = requests.get('http://localhost:5000/api/pdf_files')
       response.raise_for_status()
       pdf_files = response.json()
   except requests.exceptions.RequestException as e:
       print(f"Error fetching PDF files from server: {e}")

   if request.method == 'POST':
       print("Received a POST request") # This will print when a POST request is received
       #uploaded_file = request.files.get('file')
       selected_filename = request.form.get('selected_file')  # Access selected filename
       mcq_count = request.form.get('mcq_count')
       subject = request.form.get('subject')
       tone = request.form.get('tone')

       print(f"Selected PDF: {selected_filename}")
       print(f"MCQ Count: {mcq_count}")
       print(f"Subject: {subject}")
       print(f"Tone: {tone}")


       if not selected_filename or not mcq_count or not subject or not tone:
           error = "All fields are required."
       else:
           try:

                # Construct the full URL for the selected PDF based on filename
               pdf_url = f"http://localhost:8000/pdf_files/{selected_filename}"  # Assuming file_path contains relative paths

               print(f"Constructed URL: {pdf_url}")  # Added for debugging

               # Fetch PDF content from the URL
               response = requests.get(pdf_url)

               response.raise_for_status()  # Raise exception for non-200 status codes
               # Capture content type for verification
               content_type = response.headers.get('Content-Type')
               print(f"Content Type: {content_type}")

               # Print the response content for debugging
               print(f"Response content (might be large):")
               print(response.content[:100])

               pdf_content = response.content  # Assuming read_file handles text directly
               print(f"Fetched PDF content (might be large):")
               print(pdf_content[:100])# Print only the first 100 characters to avoid overwhelming the console

               print(type(request.files.get('selected_file')))
               # Process PDF content
               text = read_file(response.content) # Assuming read_file handles the content
               #text = read_file(request.files.get('selected_file'))

               print(text)
               response = generate_evaluate_chain({
                   "text": text,
                   "number": mcq_count,
                   "subject": subject,
                   "tone": tone,
                   "response_json": json.dumps(RESPONSE_JSON)
               })

               if isinstance(response, dict) and 'quiz' in response:
                   quiz_json_start = response['quiz'].find('{')
                   quiz_json_end = response['quiz'].rfind('}') + 1
                   quiz = response['quiz'][quiz_json_start:quiz_json_end]
                   quiz_dict = json.loads(quiz)

                   

                   #print(quiz_dict)    # Print the whole dictionary


                   # Generate a unique document ID
                   document_id = str(uuid4())

                   # Insert the document ID into the database
                   connection = get_db_connection()
                   insert_document(connection, document_id)
                   close_db_connection(connection)
               else:
                   error = "Error in response format."
                   logging.error(f"Error processing response: {response}")
           except Exception as e:
               #error = "Error processing file. Please ensure the file is a PDF or text file."
               logging.error(f"Error processing file: {e}")

   return render_template('index.html', quiz_dict=quiz_dict, error=error, success=success, pdf_files=pdf_files) 


@app.route('/add_to_database', methods=['POST'])
def add_to_database():
    error = None
    success = None
    selected_questions = request.form.getlist('selected_questions')

    if not selected_questions:
        error = "No questions selected."
    else:
        try:
            # Validate if all selected_questions are valid JSON strings
            valid_questions = []
            for question_str in selected_questions:
                try:
                    question_dict = json.loads(question_str)
                    valid_questions.append(question_dict)
                except json.JSONDecodeError:
                    error = "Invalid question format in some selections."
                    break  # Exit loop if any invalid JSON is found
            
            if error is None:  # Only proceed if all questions are valid JSON
                # Connect to the database
                connection = get_db_connection()
                if connection is None:
                    error = "Error connecting to the database."
                else:
                    logging.info("Connected to the database successfully.")
                    # Insert the valid questions into the'mcqs' table
                    for question_dict in valid_questions:
                        #print(question_dict)
                        try:
                            #print("Inserted MCQ:", question_dict)
                            logging.info(f"Inserting MCQ: {question_dict}")
                            insert_mcq(connection, question_dict)
                        except mysql.connector.Error as e:
                            error = f"Error adding MCQs to the database: {e}"
                            logging.error(f"Error inserting MCQ: {question_dict} - {e}")
                            break  # Exit loop on database insertion error
                        except Exception as e:
                            error = f"Unexpected error while inserting MCQs: {e}"
                            logging.error(f"Error inserting MCQ: {question_dict} - {e}")
                            break  # Exit loop on unexpected error
                    else:
                        success = "MCQs added to the database successfully."
                        logging.info("MCQs added to the database successfully.")

        except Exception as e:  # Catch any unexpected errors
            logging.error(f"Unexpected error: {e}")
            error = "An error occurred while processing MCQs."

        finally:
            close_db_connection(connection)

    return render_template('index.html', success=success, error=error)
# @app.route('/add_to_database', methods=['POST'])
# def add_to_database():
#     error = None
#     success = None
#     selected_questions = request.form.getlist('selected_questions')

#     if not selected_questions:
#         error = "No questions selected."
#     else:
#         try:
#             # Validate if all selected_questions are valid JSON strings
#             valid_questions = []
#             for question_str in selected_questions:
#                 try:
#                     question_dict = json.loads(question_str)
#                     valid_questions.append(question_dict)
#                 except json.JSONDecodeError:
#                     error = "Invalid question format in some selections."
#                     break  # Exit loop if any invalid JSON is found
            
#             if error is None:  # Only proceed if all questions are valid JSON
#                 # Connect to the database
#                 connection = get_db_connection()
#                 if connection is None:
#                     error = "Error connecting to the database."
#                 else:
#                     # Insert the valid questions into the 'mcqs' table
#                     for question_dict in valid_questions:
                        
#                         try:
                            
#                             insert_mcq(connection, question_dict)
#                         except mysql.connector.Error as e:
#                             error = f"Error adding MCQs to the database: {e}"
#                             break  # Exit loop on database insertion error
#                         except Exception as e:
#                             error = f"Unexpected error while inserting MCQs: {e}"
#                             logging.error(f"Question dictionary: {question_dict}")  # Log the dictionary content
#                             break  # Exit loop on unexpected error
#                     else:
#                         success = "MCQs added to the database successfully."
                        

#         except Exception as e:  # Catch any unexpected errors
#             logging.error(f"Unexpected error: {e}")
#             error = "An error occurred while processing MCQs."

#         finally:
#             close_db_connection(connection)

#     return render_template('index.html', success=success, error=error)
# Run the Flask application
if __name__ == '__main__':
   app.run(debug=True)
