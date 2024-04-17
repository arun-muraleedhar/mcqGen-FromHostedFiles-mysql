import os
import json
import PyPDF2
import traceback
from werkzeug.datastructures import FileStorage
import logging
import io

def read_file(file_content_or_path):
    if isinstance(file_content_or_path, bytes):
        # Treat file_content_or_path as file content (bytes)
        filename = "file.pdf"  # Assuming the content is a PDF

        if filename.endswith(".pdf"):
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content_or_path))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            except (PyPDF2.utils.PdfReadError, ValueError) as e:
                logging.error(f"Error reading PDF file: {filename}", exc_info=True)
                raise ValueError("Error reading the PDF file") from e
            except Exception as e:
                logging.error(f"An unexpected error occurred: {filename}", exc_info=True)
                raise ValueError("An error occurred while reading the PDF file") from e
        else:
            raise ValueError("Unsupported file format. Only PDF files are supported.")
    else:
        raise ValueError("Expected file content (bytes)")

        
def get_table_data(quiz_str):
  try:
    # Convert the quiz from a str to dict
    quiz_dict = json.loads(quiz_str)
    quiz_table_data = []

    # Iterate over the quiz dictionary and extract the required information
    for key, value in quiz_dict.items():
      mcq = value["mcq"]
      options = value["options"]

      # Unpack the options dictionary to get individual choices
      choice1 = options.get("a", "")  # Use get() with a default value to handle missing keys
      choice2 = options.get("b", "")
      choice3 = options.get("c", "")
      choice4 = options.get("d", "")  # Assuming there are at most 4 choices

      correct = value["correct"]

      # Append data to the table with separate choice columns
      quiz_table_data.append({
          "id": key,  # Assuming the key from the quiz_dict can be used as id
          "question": mcq,
          "choice1": choice1,
          "choice2": choice2,
          "choice3": choice3,
          "choice4": choice4,
          "correct_answer": correct
      })

    return quiz_table_data

  except json.JSONDecodeError as e:
    raise ValueError("Error decoding the quiz string") from e
  except KeyError as e:
    raise ValueError("Missing key in the quiz dictionary") from e
  except Exception as e:
    traceback.print_exception(type(e), e, e.__traceback__)
    return False
