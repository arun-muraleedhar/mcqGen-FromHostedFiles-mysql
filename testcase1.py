import mysql.connector
from mcqmysql2 import insert_mcq

# Define the sample_quiz_dict directly in the script
sample_quiz_dict = {
    "1": {
        "mcq": "Which of the following is the correct way to hold the bat?",
        "options": {
            "a": "Hands close together towards top of handle",
            "b": "Hands at the bottom of the handle",
            "c": "Hands in the middle of the handle",
            "d": "Hands as far apart as possible"
        },
        "correct": "a"
    },
    "2": {
        "mcq": "What is the first step in the Backlift?",
        "options": {
            "a": "Move back and across",
            "b": "Step forward and across",
            "c": "Step back and stay in place",
            "d": "Step forward and stay in place"
        },
        "correct": "a"
    },
    "3": {
        "mcq": "What is the key to playing a good On Drive?",
        "options": {
            "a": "Dip front shoulder and take a short stride",
            "b": "Lean back and take a long stride",
            "c": "Lean forward and take a short stride",
            "d": "Lean back and take a long stride"
        },
        "correct": "a"
    }
}

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'DFSmt@103',
    'host': 'localhost',
    'database': 'files_db',
    'raise_on_warnings': True
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        return None

def close_db_connection(connection):
    if connection:
        connection.close()

def test_insert_mcq():
    connection = get_db_connection()
    if connection is None:
        print("Error: Could not connect to the database.")
        return

    try:
        insert_mcq(connection, sample_quiz_dict)
        print("MCQs inserted successfully!")
    except mysql.connector.Error as e:
        print(f"MySQL Error inserting MCQs: {e}")
    except Exception as e:
        print(f"Error inserting MCQs: {e}")
    finally:
        close_db_connection(connection)

if __name__ == "__main__":
    test_insert_mcq()
