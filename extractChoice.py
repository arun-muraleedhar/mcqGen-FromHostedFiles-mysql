import mysql.connector

# Connect to your MySQL server
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='DFSmt@103',
    database= 'files_db'
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS mcq_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255),
    choice1 VARCHAR(255),
    choice2 VARCHAR(255),
    choice3 VARCHAR(255),
    choice4 VARCHAR(255),
    correct_answer VARCHAR(255)
)
""")

# Extracted questions
# data = {
#     "1": {
#         "mcq": "Who led the Dandi March?",
#         "options": {
#             "a": "Jawaharlal Nehru",
#             "b": "Subhash Chandra Bose",
#             "c": "Mahatma Gandhi",
#             "d": "Bhagat Singh"
#         },
#         "correct": "c"
#     },
#     "2": {
#         "mcq": "What was the aim of the Dandi March?",
#         "options": {
#             "a": "To gain independence from British rule",
#             "b": "To protest against the Salt Law",
#             "c": "To promote Hindu-Muslim unity",
#             "d": "To support the Quit India Movement"
#         },
#         "correct": "b"
#     },
#     "3": {
#         "mcq": "When did the Dandi March take place?",
#         "options": {
#             "a": "1928",
#             "b": "1930",
#             "c": "1932",
#             "d": "1934"
#         },
#         "correct": "b"
#     },
#     "4": {
#         "mcq": "Where did the Dandi March start from?",
#         "options": {
#             "a": "Calcutta",
#             "b": "Bombay",
#             "c": "Sabarmati",
#             "d": "Delhi"
#         },
#         "correct": "c"
#     },
#     "5": {
#         "mcq": "What was the result of the Dandi March?",
#         "options": {
#             "a": "It led to India's independence",
#             "b": "It was a failure",
#             "c": "It increased support for the Indian National Congress",
#             "d": "It resulted in the arrest of Gandhi"
#         },
#         "correct": "c"
#     }
# }

data = {
    "1": {
        "ചോദ്യം": "ഡാൻഡി മാർച്ച് ആരുടെ നേതൃത്വത്തിൽ നടന്നു?",
        "ഓപ്ഷനുകൾ": {
            "a": "ജവഹർലാൽ നെഹ്രു",
            "b": "സുഭാഷ് ചന്ദ്ര ബോസ്",
            "c": "മഹാത്മാ ഗാന്ധി",
            "d": "ഭഗത് സിംഗ്"
        },
        "ശരി": "c"
    },
    "2": {
        "ചോദ്യം": "ഡാൻഡി മാർച്ചിന്റെ ഉദ്ദേശ്യം എന്തായിരുന്നു?",
        "ഓപ്ഷനുകൾ": {
            "a": "ബ്രിട്ടിഷ് ശാസനത്തിൽ സ്വാതന്ത്ര്യം നേടാൻ",
            "b": "സാൽട്ട് നിയമത്തിനെ പ്രതിഷേധിക്കാൻ",
            "c": "ഹിന്ദു-മുസ്ലിം ഏകത്വത്തെ പ്രചോദിപ്പിക്കാൻ",
            "d": "ക്വിറ്റ് ഇന്ത്യ പ്രചാരണത്തിനെ പിന്തുണയ്ക്കുക"
        },
        "ശരി": "b"
    },
    "3": {
        "ചോദ്യം": "ഡാൻഡി മാർച്ച് എപ്പോഴും നടന്നു?",
        "ഓപ്ഷനുകൾ": {
            "a": "1928",
            "b": "1930",
            "c": "1932",
            "d": "1934"
        },
        "ശരി": "b"
    }
}


# Insert data into the MySQL table
# for key, value in data.items():
#     question = value["mcq"]
#     choices = value["options"]
#     correct_key = value["correct"]


    # Extract choices with key and choice
    # choice1 = f"{list(choices.keys())[0]}: {choices.get('a', '')}"
    # choice2 = f"{list(choices.keys())[1]}: {choices.get('b', '')}"
    # choice3 = f"{list(choices.keys())[2]}: {choices.get('c', '')}"
    # choice4 = f"{list(choices.keys())[3]}: {choices.get('d', '')}"

for key, value in data.items():
    question = value["ചോദ്യം"]
    choices = value["ഓപ്ഷനുകൾ"]
    correct_key = value["ശരി"]
    choice1 = f"{list(choices.keys())[0]}: {choices.get('a', '')}"
    choice2 = f"{list(choices.keys())[1]}: {choices.get('b', '')}"
    choice3 = f"{list(choices.keys())[2]}: {choices.get('c', '')}"
    choice4 = f"{list(choices.keys())[3]}: {choices.get('d', '')}"

    


    # Extract the text of the correct answer
    correct_answer = choices[correct_key]
    
    # SQL query to insert data into the table
    sql = "INSERT INTO mcq_questions (question, choice1, choice2, choice3, choice4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)"
    
    # Execute the SQL query
    cursor.execute(sql, (question, choice1, choice2, choice3, choice4, correct_answer))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
