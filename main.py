import os
import sys
import sqlite3
import pwinput

CONN = None
CURSOR = None

ANSI = {
    "RESET": "\033[0m",     # Reset color
    "CLEARLINE": "\033[0K"  # Clear line
}

def print_location(x, y, text):
    '''
    ## Print text at specified location

    ### Args:
        - `x (int)`: x - coordinate
        - `y (_type_)`: y - coordinate
        - `text (_type_)`: The text to be printed
    '''    
    print("\033[{1};{0}H{2}".format(y, x, text))

def clear_screen():
    '''
    ## Clear the terminal screen
    '''    
    if os.name == "nt":  # for Windows
            os.system("cls")
    else:                # for Mac/Linux
        os.system("clear")    
    
def move_cursor(x, y):
    '''
    ## Move cursor to specified location

    ### Args:
        - `x (int)`: x coordinate
        - `y (int)`: y coordinate
    '''    
    print("\033[{1};{0}H".format(y, x), end='')    

def login_screen():
    print_location(2, 0,'1. Registered User')
    print_location(3, 0,'2. Unregisterd User')
    print_location(4, 0,'3. Exit')
    user_input = input("")
    
    if user_input == '1' or user_input == '1.':
        registered_user()
    elif user_input == '2' or user_input == '2.':
        unregistered_user()
    elif user_input == '3' or user_input == '3.':
        exit()
    return

def registered_user():
    clear_screen()
    print_location(1, 0, "*** REGISTERED USER ***")
    print("\n")
    
    user_id = input("Enter User ID: ").strip()
    password = input("Enter Password: ").strip()
    
    # Query to check if the user exists and the password is correct
    CURSOR.execute("SELECT * FROM users WHERE usr = ? AND pwd = ?", (user_id, password))
    user = CURSOR.fetchone()
    
    if user:
        print_location(3, 0, "Login successful!")
        display_feed(user_id)
    else:
        print_location(3, 0, "Invalid user ID or password.")

def display_feed(user_id):
    offset = 0
    while True:
        CURSOR.execute('''
            SELECT tid, text, tdate FROM tweets 
            WHERE writer_id IN (SELECT flwee FROM follows WHERE flwer = ?)
            ORDER BY tdate DESC
            LIMIT 5 OFFSET ?
        ''', (user_id, offset))
        
        tweets = CURSOR.fetchall()
        
        if not tweets:
            print("No more tweets to show.")
            break
        
        clear_screen()
        print_location(1, 0, "*** FEED ***")
        for i, (tid, text, tdate) in enumerate(tweets, start=1):
            print_location(i + 1, 0, f"{tdate} - {text}")
        
        # Prompt user for more or exit
        user_input = input("Enter 'n' for next 5 tweets or 'q' to quit: ").strip().lower()
        if user_input == 'n':
            offset += 5
        else:
            break

def unregistered_user():
    clear_screen()
    print_location(1, 0, "*** UNREGISTERED USER ***")
    print("\n")
    
    name = input("Enter name: ")
    email = input("Enter email: ")
    phone = input("Enter phone number: ")
    password = input("Enter password: ")
    
    # Generate a unique user ID (using max `usr` + 1 as a simple method)
    CURSOR.execute("SELECT MAX(usr) FROM users")
    max_id = CURSOR.fetchone()[0]
    user_id = max_id + 1 if max_id is not None else 1
    
    # Insert the new user into the users table
    CURSOR.execute("INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)",
                   (user_id, name, email, phone, password))
    CONN.commit()
    
    print_location(6, 0, f"Sign-up successful! Your User ID is {user_id}.")
    display_feed(user_id)
 
def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def main():
    os.system("")  # Clear console
    clear_screen()  # Clear the screen
    print_location(1, 0,'*** MINI PROJECT 1 ***') # Print game heading
    print("\n")

    global CURSOR, CONN

    if len(sys.argv) < 2:
        print_location(2, 0, "Database not mentioned")
        exit()
    
    else:
        path = "./" + sys.argv[1]
        connect(path)
        login_screen()
        

if __name__ == "__main__":
    main()