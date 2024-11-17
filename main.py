# Importing files
import sys      # Used to take command line inputs
import sqlite3  # Used to access database

from getpass import getpass     # Used to mke password non-visible
from datetime import datetime   

# Importing Functions from different files
from followers import follower_utils
from compose_tweet import compose_tweet
from common_utils import *
from tweet_search import search_tweets
from search_users import *

CONN = None
CURSOR = None
CURRENT_USER_ID = None  # To store the current loggined userId

def login_screen():
    '''
    ## This function prints a login screen menu and asks for input from the user.
    '''
    clear_screen()
    print_location(1, 0,'*** MINI PROJECT 1 ***') # Print game heading
    print("\n")
    while True:
        print('\n')
        print_location(3, 0, '1. Registered User')
        print_location(4, 0, '2. Unregistered User')
        print_location(5, 0, '3. Exit')
        
        try:
            user_input = int(input(">>> "))
            
            if user_input == 1:
                registered_user()
            elif user_input == 2:
                unregistered_user()
            elif user_input == 3:
                exit()
            else:
                move_cursor(7,0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(7, 0, "Invalid Input.")
                move_cursor(6,5)
                print(ANSI["CLEARLINE"], end="\r")
        except ValueError:
            move_cursor(7,0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(7, 0, "Please enter a valid number.")
            move_cursor(6,5)
            print(ANSI["CLEARLINE"], end="\r")

def registered_user():
    '''
    ## This function is called for registered users.
        It asks the user for a username and password.
        If the user enters the correct credentials, login is successful and prints the user's feed.
    '''
    global CURRENT_USER_ID, CURSOR
    clear_screen()
    print_location(1, 0, "*** REGISTERED USER ***")
    print_location(2, 0, "")

    while True:  # Loop until valid credentials are provided
        
        print_location(3, 0, "Enter User ID: ")
        move_cursor(3, 17)
        user_id = input("").strip()
        
        move_cursor(4, 17)
        password = getpass("Enter Password: ").strip()

        # Query to check if the user exists and the password is correct
        CURSOR.execute("SELECT * FROM users WHERE usr = ? AND pwd = ?", (user_id, password))
        user = CURSOR.fetchone()

        if user:
            move_cursor(6,0)
            print(ANSI["CLEARLINE"], end="\r") # Clear anything written previulsy in that line
            print_location(6, 0, f"Login successful!\nWelcome {user[1]}!\n")
            input("Press Enter to continue......")
            
            CURRENT_USER_ID = user[0]  # After a successful login, assign the user ID to CURRENT_USER_ID
            move_cursor(8,0)
            user_feed(CURSOR, CURRENT_USER_ID)
            break  # Exit the loop if login is successful
        
        else:
            print_location(6, 0, "Invalid user ID or password. Please try again.")
            
            move_cursor(3, 0)
            print(ANSI["CLEARLINE"], end="\r") # Clear previous username
            
            move_cursor(4, 0)
            print(ANSI["CLEARLINE"], end="\r") # Clear previous password
          
def unregistered_user():
    '''
    ## This function is called for unregistered users.
        It asks for name, email, phone and a passowrd and adds a new user to the
        database.
    '''
    clear_screen()
    print_location(1, 0, "*** UNREGISTERED USER ***\n")

    # Display prompts once
    print_location(3, 0, "Enter name: ")
    print_location(4, 0, "Enter email: ")
    print_location(5, 0, "Enter phone number: ")
    print_location(6, 0, "Enter password: ")

    # TAKING USERNAME INPUT
    while True:
        move_cursor(3, 13)  # Align cursor with the "Enter name: " prompt
        print(ANSI["CLEARLINE"], end="\r")
        move_cursor(3, 13)
        name = input("").strip()
        if name.isalnum():
            break
        move_cursor(8, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(8, 0, "Username should not contain spaces. Only alphanumeric usernames are allowed.")

    # TAKING EMAIL INPUT
    while True:
        move_cursor(4, 14)  # Align cursor with the "Enter email: " prompt
        print(ANSI["CLEARLINE"], end="\r")
        move_cursor(4, 14)
        email = input("").strip()
        if '@' in email and '.' in email:  # Simple email validation
            break
        move_cursor(8, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(8, 0, "Invalid email format. Ensure it contains '@' and a domain (e.g., 'example.com').")

    # TAKING PHONE NUMBER INPUT
    while True:
        move_cursor(5, 21)  # Align cursor with the "Enter phone number: " prompt
        print(ANSI["CLEARLINE"], end="\r")
        move_cursor(5, 21)
        try:
            phone = int(input("").strip())
            if len(str(phone)) == 10:
                break
            move_cursor(8, 0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(8, 0, "The phone number must be exactly 10 digits.")
        except ValueError:
            move_cursor(8, 0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(8, 0, "Invalid phone number. Please enter a valid 10-digit number.")

    # TAKING PASSWORD INPUT
    while True:
        move_cursor(6, 17)  # Align cursor with the "Enter password: " prompt
        print(ANSI["CLEARLINE"], end="\r")
        move_cursor(6, 17)
        password = getpass("").strip()
        if password:
            break
        move_cursor(8, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(8, 0, "Password cannot be empty.")


    # Generate a unique user ID (using max `usr` + 1 as a simple method)
    global CURSOR, CONN
    CURSOR.execute("SELECT MAX(usr) FROM users")
    max_id = CURSOR.fetchone()[0]
    if max_id is not None:
        CURRENT_USER_ID = max_id + 1
    else:
        CURRENT_USER_ID = 1
        
    # Insert the new user into the users table
    CURSOR.execute(
        """
        INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)
        """,
        (CURRENT_USER_ID, name, email, phone, password)
    )
    CONN.commit()
    
    clear_screen()
    print_location(1, 0, "*** UNREGISTERED USER ***")
    print_location(3, 0, f"Sign-up successful! Your User ID is {CURRENT_USER_ID}.")
    
    print_location(5, 0, "Would you like to go to the Main Menu y/n: ")
    while True:
        move_cursor(5, 44)
        user_input = input("")
        
        if user_input.lower() == 'y' :
            system_functions(CURSOR, CURRENT_USER_ID)
            break
        elif user_input.lower() == 'n':
            exit()
        else:
            print_location(6, 0, "Invalid Input. Please enter 'y' or 'n'.")
            move_cursor(5, 44)
            print(ANSI["CLEARLINE"], end="\r")
 
def connect(path):
    global CONN, CURSOR
    try:
        CONN = sqlite3.connect(path)
        CURSOR = CONN.cursor()
        CURSOR.execute(' PRAGMA foreign_keys=ON; ')
        CONN.commit()

    except sqlite3.Error as e:
        print(f"\n\n\n\nFailed to connect to database: {e}")
        CONN, CURSOR = None, None

def system_functions(cursor, current_user_id):
    
    global CURSOR, CURRENT_USER_ID
    CURSOR = cursor
    CURRENT_USER_ID = current_user_id
    
    clear_screen()
    print_location(1,0, '*** SYSTEM FUNCTIONALITIES ***')
    print_location(3, 0,'1. Search for tweets')
    print_location(4, 0,'2. Search for users')
    print_location(5, 0,'3. Compose a tweet')
    print_location(6, 0,'4. List followers')
    print_location(7, 0,'5. User Feed')
    print_location(8, 0,'6. Logout')
    
    while True:
        try:
            user_input = int(input(">>> "))
            if user_input == 1:
                search_tweets(CURSOR, CURRENT_USER_ID)
            elif user_input == 2:
                search_users(CURSOR, CURRENT_USER_ID)
            elif user_input == 3:
                compose_tweet(CURSOR, CURRENT_USER_ID)
            elif user_input == 4:
                follower_utils.showFollowers(CURRENT_USER_ID, CURSOR)
            elif user_input == 6:
                logout()
            elif user_input == 5:
                user_feed(CURSOR, CURRENT_USER_ID)
            else:
                move_cursor(9,0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(9, 0, "Invalid input! Please choose a valid number.")
                move_cursor(8,5)
                print(ANSI["CLEARLINE"], end="\r")   

        except ValueError:
            move_cursor(9,0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(9, 0, "Please enter a valid number.")
            move_cursor(8,5)
            print(ANSI["CLEARLINE"], end="\r")
        
          

def logout():
    '''
    ## This function logs out the current user and redirects to the login screen.
    It ensures that the session is cleared and the program does not exit.
    '''
    CURRENT_USER_ID = None  # Clear the current logged-in user's ID
    clear_screen()  # Clear the console screen for a fresh login view
    print("\nYou have successfully logged out.")
    user_input = input("Press Enter to return to the login screen or 'q' to quit: ").lower()
    if user_input == 'q':
        exit()
    login_screen()  # Redirect back to the login screen

def main():
    os.system("")  # Clear console
    clear_screen()  # Clear the screen

    global CURSOR, CONN

    if len(sys.argv) < 2:
        print_location(2, 0, "Database not mentioned")
        exit()
    
    else:
        path = "./" + sys.argv[1]
        connect(path)
        if CONN is None or CURSOR is None:
            print("Could not establish a connection to the database.")
            exit()
        
        else:
            path = "./" + sys.argv[1]
            connect(path)
            login_screen()
            #system_functions()
        
if __name__ == "__main__":
    main()
