# Importing files
import sys      # Used to take command line inputs
import sqlite3  # Used to access database

from getpass import getpass     # Used to mke password non-visible
from datetime import datetime   

# Importing Functions from different files
from followers import follower_utils
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
        
        print_location(3, 0, "Enter Username: ")
        move_cursor(3, 17)
        user_name = input("").strip()
        
        move_cursor(4, 17)
        password = getpass("Enter Password: ").strip()

        # Query to check if the user exists and the password is correct
        CURSOR.execute("SELECT * FROM users WHERE upper(name) = ? AND pwd = ?", (user_name.upper(), password))
        user = CURSOR.fetchone()

        if user:
            move_cursor(6,0)
            print(ANSI["CLEARLINE"], end="\r") # Clear anything written previulsy in that line
            print_location(6, 0, "Login successful!")
            
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
    print_location(1, 0, "*** UNREGISTERED USER ***")
    
    name = input("Enter name: ")
    email = input("Enter email: ")
    phone = int(input("Enter phone number: "))
    password = input("Enter password: ")
    
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
    user_input = input("Would you like to go to the Main Menu y/n: ")
    if user_input.lower() == 'y' :
        system_functions(CURSOR, CURRENT_USER_ID)
    elif user_input.lower() == 'n':
        exit()
    else:
        print('Invalid Input.')
 
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
    print_location(7, 0,'5. Logout')
    
    while True:
        try:
            user_input = int(input(">>> "))
            if user_input == 1:
                search_tweets(CURSOR, CURRENT_USER_ID)
            elif user_input == 2:
                search_users(CURSOR, CURRENT_USER_ID)
            elif user_input == 3:
                compose_tweet(CURSOR)
            elif user_input == 4:
                follower_utils.showFollowers(CURRENT_USER_ID, CURSOR)
            elif user_input == 5:
                logout()
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
        
def compose_tweet(cursor):
    global CURSOR

    # taing input from user
    clear_screen()
    print_location(1, 10, "*** COMPOSE A TWEET ***")
    print_location(2, 10, "=======================")
    inp = True
    while inp:
        move_cursor(5, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(5, 0, "Enter Tweet: ")
        move_cursor(5, 15)
        tweet_text = input("")

        # making list of input words
        input_terms = tweet_text.split(" ")
        hashtag = []
        for term in input_terms:
            if term[0] == "#" and len(term) > 1:
                if term.lower() not in hashtag:
                    hashtag.append(term.lower())
                else:
                    move_cursor(4, 0)
                    print(ANSI["CLEARLINE"], end="\r")
                    print_location(4, 0, "Please try again: Duplicate hashtags are not allowed!")
                    inp = True
        inp = False


    CURSOR.execute(
       """
        SELECT MAX(tid) FROM tweets
       """
    )
    max_tid = CURSOR.fetchone()[0]
    # setting 1 if it is first tweet or setting it as max+1 for next tweet
    if max_tid is None:
        new_tid = 1 
    else:
        new_tid = max_tid + 1  

    current_date = datetime.now().strftime("%Y-%m-%d") 
    current_time = datetime.now().strftime("%H:%M:%S")  


    # SQL query to insert the tweet
    insert_tweet_query = """
    INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
    VALUES (?, ?, ?, ?, ?, NULL)
    """

    # Inserting the tweet into the database
    CURSOR.execute(
        insert_tweet_query,
        (new_tid, CURRENT_USER_ID, tweet_text, current_date, current_time)
    )

    # SQL query for hashtag mentions
    insert_hashtag_query = """
    INSERT INTO hashtag_mentions (tid, term)
    VALUES (?, ?)
    """

    # Adding each valid hashtag to the hashtag_mentions table
    for tag in hashtag:
        CURSOR.execute(insert_hashtag_query, (new_tid, tag))

    print_location(6, 0, "Tweet and hashtags successfully recorded!")


    i = True
    while i:
        print_location(9, 0, "Enter 'f' to view user feed, 'm' to go back to Main Menu or 'q' to quit:  ")
        move_cursor(9, 90)
        user_input = input("")
        if user_input == 'f':
            user_feed()
            i = False
        elif user_input == 'q':
            exit()
            i = False
        elif user_input == 'm':
            system_functions(CURSOR, CURRENT_USER_ID)
            i = False
        else:
            print_location(8 , 0, "Invalid Input: Please Try Again")
            i = True              

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
    registered_user()  # Redirect back to the login screen

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
