import os
import sys
from datetime import datetime
import sqlite3
from followers import follower_utils
from common_utils import *

CONN = None
CURSOR = None
CURRENT_USER_ID = None  # To store the current loggined userId

def login_screen():
    '''
    ## This functions prints a login screen menu and asks for a input from the user.
    '''
    print('\n')
    print_location(3, 0,'1. Registered User')
    print_location(4, 0,'2. Unregistered User')
    print_location(5, 0,'3. Exit')
    user_input = input(">>> ")
    
    if user_input == '1' or user_input == '1.':
        registered_user()
    elif user_input == '2' or user_input == '2.':
        unregistered_user()
    elif user_input == '3' or user_input == '3.':
        exit()
    return

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
        
        print_location(4, 0, "Enter Password: ")
        move_cursor(4, 17)
        password = input("").strip()

        # Query to check if the user exists and the password is correct
        CURSOR.execute("SELECT * FROM users WHERE upper(name) = ? AND pwd = ?", (user_name.upper(), password))
        user = CURSOR.fetchone()

        if user:
            move_cursor(6,0)
            print(ANSI["CLEARLINE"], end="\r") # Clear anything written previulsy in that line
            print_location(6, 0, "Login successful!")
            
            CURRENT_USER_ID = user[0]  # After a successful login, assign the user ID to CURRENT_USER_ID
            follower_utils.getFollowers(CURRENT_USER_ID, CURSOR, 8)  # need to test this function
            
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

    user_input = input(">>>")
    
    if user_input == '1' or user_input == '1.':
        #search for tweets function to be added by luke
        pass
    elif user_input == '2' or user_input == '2.':
        search_users(CURSOR, CURRENT_USER_ID)
    elif user_input == '3' or user_input == '3.':
        compose_tweet(CURSOR)
        pass
    elif user_input == '4' or user_input == '4.':
        # list followers to be added by yuheng
        pass
    elif user_input == '5' or user_input == '5.':
        logout()
        pass

    return

def search_users(cursor, current_user_id):
    clear_screen()
    print_location(1,0,"*** SEARCH FOR USERS ***")
    
    print_location(3, 0, "Enter Keyword: ")
    move_cursor (3, 16)
    keyword = input("")
    
    global CURSOR, CURRENT_USER_ID
    
    offset = 0
    limit = 5
    users = get_users_list(keyword, offset, limit)
    
    if not users:
        print_location(5, 0, "No users found.")
        
    print_location(5, 0, "Users found: ")

    for index, (usr, name) in enumerate(users, start=1):
            print_location(5 + index, 4, f"{index}. {name} (User ID: {usr})")
            
    move_cursor(5+index,0)
    # Get user input to proceed
    while True:
        user_input = input("\nEnter 'n' to see more, user number to view details, 'q' to quit, or 's' for Main Menu: ").strip().lower()
            
        if user_input == 'n':
            next_followers = get_users_list(keyword, offset=offset + 5, limit=5)
            if next_followers:  # Only load more if there are more followers
                offset += 5  # Move to the next page
            else:
                print("No more users to display")
                
        elif user_input == 'q':
            exit()
            
        elif user_input == 's':
            system_functions(cursor, current_user_id)
            return
            
        else:
            try:
                user_index = int(user_input) - 1
                if 0 <= user_index < len(users):
                    selected_user_id = users[user_index][0]
                    follower_utils.showFollowerDetails(selected_user_id)
                else:
                    print_location(8, 0, "Invalid selection. Try again.")
            except ValueError:
                print_location(8, 0, "Invalid input. Try again.")
        
def get_users_list(keyword, offset=0, limit=5):
    cursor = CURSOR
    user_id = CURRENT_USER_ID
    
    CURSOR.execute('''
            SELECT usr, name FROM users 
            WHERE name LIKE ?
            ORDER BY LENGTH(name) ASC
            LIMIT 5 OFFSET ?
        ''', (f'%{keyword}%', offset))
    
    users = CURSOR.fetchall()
    
    if users:
        return users
    else:
        return None   

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
        valid = 0
        hashtag = []
        for term in input_terms:
            if term[0] == "#" and len(term) > 1:
                if term.lower() not in hashtag:
                    hashtag.append(term.lower())
                    inp = False
                else:
                    move_cursor(4, 0)
                    print(ANSI["CLEARLINE"], end="\r")
                    print_location(4, 0, "Please try again: Duplicate hashtags are not allowed!")
                    inp = True


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
        print_location(9, 0, "Enter 'h' to go back to Home Page, 'm' to go back to Main Menu or 'q' to quit:  ")
        move_cursor(9, 90)
        user_input = input("")
        if user_input == 'h':
            follower_utils.getFollowers(CURRENT_USER_ID, CURSOR, 8)
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
    input("Press Enter to return to the login screen...")
    login_screen()  # Redirect back to the login screen


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