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


# Suppress favicon logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
   'user': 'root',
   'password': 'DFSmt@103',
   'host': 'localhost',
   'database': 'files_db',
   'raise_on_warnings': True
}

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




# def insert_mcq(connection, quiz_dict):
#     if connection:
#         cursor = connection.cursor()
#         for key, value in quiz_dict.items():
#             question = value["mcq"]
#             choices = value["options"]
#             correct_answer = value["correct"]
    
#             # Extract choices with key and choice
#             choice1 = f"{list(choices.keys())[0]}: {choices.get('a', '')}"
#             choice2 = f"{list(choices.keys())[1]}: {choices.get('b', '')}"
#             choice3 = f"{list(choices.keys())[2]}: {choices.get('c', '')}"
#             choice4 = f"{list(choices.keys())[3]}: {choices.get('d', '')}"
    
#              # SQL query to insert data into the table
#             sql = "INSERT INTO mcqs (question, choice1, choice2, choice3, choice4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)"
    
#             # Execute the SQL query
#             cursor.execute(sql, (question, choice1, choice2, choice3, choice4, correct_answer))

#     # Commit the transaction
#     conn.commit()

#     # Close the cursor and connection
#     cursor.close()


# def insert_mcq(connection, quiz_dict):
#     if connection:
#         cursor = connection.cursor()
#         for question_id, question_data in quiz_dict.items():
#             question = question_data["mcq"]
#             choices = question_data["options"]
#             correct_answer = question_data["correct"]

#             # Extract choices using list comprehension
#             choice_list = [f"{choice_key}: {choice_text}" for choice_key, choice_text in choices.items()]
#             choice1 = choice_list[0] if len(choice_list) > 0 else ""
#             choice2 = choice_list[1] if len(choice_list) > 1 else ""
#             choice3 = choice_list[2] if len(choice_list) > 2 else ""
#             choice4 = choice_list[3] if len(choice_list) > 3 else ""

#             # SQL query to insert data into the table
#             sql = "INSERT INTO mcqs (question, choice1, choice2, choice3, choice4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)"

#             try:
#                 cursor.execute(sql, (question, choice1, choice2, choice3, choice4, correct_answer))
#             except mysql.connector.Error as e:
#                 logging.error(f"Error inserting MCQ: {e}")
#                 continue

#         connection.commit()
#         cursor.close()
def insert_mcq(connection, quiz_dict):
    if connection:
        cursor = connection.cursor()

        # Validate the structure of quiz_dict
        if not isinstance(quiz_dict, dict):
            logging.error("Invalid data structure for quiz_dict. Expected a dictionary.")
            return

        for key, value in quiz_dict.items():
            # Validate the structure of each MCQ
            if not isinstance(value, dict) or \
               "mcq" not in value or \
               "options" not in value or \
               "correct" not in value:
                logging.error(f"Invalid MCQ data structure for key: {key}")
                continue

            question = value["mcq"]
            choices = value["options"]
            correct_answer = value["correct"]
            # Add logging statements
            logging.debug(f"Extracted MCQ data: question - {question}, choices - {choices}, correct_answer - {correct_answer}")

            # Extract choices with key and choice
            choice_keys = list(choices.keys())
            if len(choice_keys) < 4:
                logging.error(f"Insufficient choices for MCQ key: {key}")
                continue

            choice1 = f"{choice_keys[0]}: {choices.get(choice_keys[0], '')}"
            choice2 = f"{choice_keys[1]}: {choices.get(choice_keys[1], '')}"
            choice3 = f"{choice_keys[2]}: {choices.get(choice_keys[2], '')}"
            choice4 = f"{choice_keys[3]}: {choices.get(choice_keys[3], '')}"

            # SQL query to insert data into the table
            sql = "INSERT INTO mcqq (question, choice1, choice2, choice3, choice4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)"

            # Execute the SQL query with logging
            logging.debug(f"Executing SQL: {sql}")
            cursor.execute(sql, (question, choice1, choice2, choice3, choice4, correct_answer))

        # Commit the transaction
            connection.commit()
            cursor.close()
    else:
      logging.error("Failed to get database connection.")

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
   quiz_dict = None
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

                   

                   print(quiz_dict)    # Print the whole dictionary
                   # Print the choices content (assuming choices is within quiz_dict)
                #    choices_list = []
                #    for mcq in quiz_dict.get('mcqs', []):  # Handle cases where 'mcqs' key might not exist
                #         choices_list.append(mcq['options'])
                #    print(f"Choices content (from all MCQs): {choices_list}")
                


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

# def add_to_database():
#   error = None
#   success = None
#   selected_questions = request.form.getlist('selected_questions')

#   if not selected_questions:
#     error = "No questions selected."
#   else:
#     try:
#       # Validate if all selected_questions are valid JSON strings
#       valid_questions = []
#       for question_str in selected_questions:
#         try:
#           question_dict = json.loads(question_str)
#           valid_questions.append(question_dict)
#         except json.JSONDecodeError:
#           error = "Invalid question format in some selections."
#           break  # Exit loop if any invalid JSON is found
      
#       if error is None:  # Only proceed if all questions are valid JSON
#         # Connect to the database
#         connection = get_db_connection()
#         if connection is None:
#           error = "Error connecting to the database."
#         else:
#           # Insert the valid questions into the 'mcqs' table
#           for question_dict in valid_questions:
#             try:
#               insert_mcq(connection, question_dict)
#             except mysql.connector.Error as e:
#               error = f"Error adding MCQs to the database: {e}"
#               break  # Exit loop on database insertion error
#           else:
#             success = "MCQs added to the database successfully."

#     except Exception as e:  # Catch any unexpected errors
#       logging.error(f"Unexpected error: {e}")
#       error = "An error occurred while processing MCQs."

#     finally:
#       close_db_connection(connection)

#   return render_template('index.html', success=success, error=error)

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
                    # Insert the valid questions into the 'mcqs' table
                    for question_dict in valid_questions:
                        try:
                            insert_mcq(connection, question_dict)
                        except mysql.connector.Error as e:
                            error = f"Error adding MCQs to the database: {e}"
                            break  # Exit loop on database insertion error
                        except Exception as e:
                            error = f"Unexpected error while inserting MCQs: {e}"
                            logging.error(f"Question dictionary: {question_dict}")  # Log the dictionary content
                            break  # Exit loop on unexpected error
                    else:
                        success = "MCQs added to the database successfully."

        except Exception as e:  # Catch any unexpected errors
            logging.error(f"Unexpected error: {e}")
            error = "An error occurred while processing MCQs."

        finally:
            close_db_connection(connection)

    return render_template('index.html', success=success, error=error)
# Run the Flask application
if __name__ == '__main__':
   app.run(debug=True)