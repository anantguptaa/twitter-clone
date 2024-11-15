import os
import sys
from datetime import datetime
import sqlite3
from followers import follower_utils
from common_utils import *

CONN = None
CURSOR = None
USER_ID = None  # To store the current loggined userId

def login_screen():
    '''
    ## This functions prints a login screen menu and asks for a input from the user.
    '''
    print('\n')
    print_location(3, 0,'1. Registered User')
    print_location(4, 0,'2. Unregisterd User')
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
    global USER_ID
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
        global CURSOR
        CURSOR.execute("SELECT * FROM users WHERE upper(name) = ? AND pwd = ?", (user_name.upper(), password))
        user = CURSOR.fetchone()

        if user:
            move_cursor(6,0)
            print(ANSI["CLEARLINE"], end="\r") # Clear anything written previulsy in that line
            print_location(6, 0, "Login successful!")
            
            USER_ID = user[0]  # After a successful login, assign the user ID to USER_ID
            follower_utils.getFollowers(USER_ID, CURSOR, 8)  # need to test this function
            
            break  # Exit the loop if login is successful
        else:
            print_location(6, 0, "Invalid user ID or password. Please try again.")
            
            move_cursor(3, 0)
            print(ANSI["CLEARLINE"], end="\r") # Clear previous username
            
            move_cursor(4, 0)
            print(ANSI["CLEARLINE"], end="\r") # Clear previous password
            
            
    print("\n")
    
    user_name = input("Enter User ID: ").strip()
    password = input("Enter Password: ").strip()
    
    # Query to check if the user exists and the password is correct
    # global CURSOR
    CURSOR.execute("SELECT * FROM users WHERE upper(name) = ? AND pwd = ?", (user_name.upper(), password))
    user = CURSOR.fetchone()
    
    if user:
        USER_ID = user_name  # After Sucessfully login, assign current usrId to the global variable USER_ID
        print_location(3, 0, "Login successful!")
        follower_utils.displayFollowers(user_name, CURSOR) #need to test this function
    else:
        print_location(3, 0, "Invalid user ID or password.")

# i (anant) will most probbaly delete this function, it doesnt work properly and yuheng has already implemented it
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
        user_id = max_id + 1
    else:
        user_id = 1
        
    # Insert the new user into the users table
    query = "INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)",
    (user_id, name, email, phone, password)
    CURSOR.execute(query)
    CONN.commit()
    
    print_location(7, 0, f"Sign-up successful! Your User ID is {user_id}.")
 
def connect(path):
    global CONN, CURSOR

    CONN = sqlite3.connect(path)
    CURSOR = CONN.cursor()
    CURSOR.execute(' PRAGMA foreign_keys=ON; ')
    CONN.commit()
    return

def system_functions():
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
        # search for users to be added by anant
        pass
    elif user_input == '3' or user_input == '3.':
        compose_tweet()
        pass
    elif user_input == '4' or user_input == '4.':
        # list followers to be added by yuheng
        pass
    elif user_input == '5' or user_input == '5.':
        # logout function to be added
        pass

    return

def search_users():
    #still working on this
    clear_screen()
    print_location(1,0,"*** SEARCH FOR USERS ***")
    
    move_cursor(2,0)
    print_location(2, 0, "Enter Keyword: ")
    move_cursor (2, 16)
    keyword = input("")
    
    global CURSOR
    offset = 0
    CURSOR.execute('''
            SELECT usr, name FROM users 
            WHERE name LIKE ?
            ORDER BY LENGTH(name) ASC
            LIMIT 5 OFFSET ?
        ''', (f'%{keyword}%', offset))
    
    users = CURSOR.fetchall()

def compose_tweet(cursor):
    global CURSOR

    # taing input from user
    tweet_text = input("Enter your tweet: ")
    # making list of input words
    input_terms = tweet_text.split(" ")
    valid = 0
    hashtag = []
    for term in input_terms:
        if term[0] == "#" and len(term) > 1:
            if term[1:].lower() not in hashtag:
                hashtag.append(term[1:0].lower())
            else:
                raise ValueError("Duplicate hashtags are not allowed. Please try again!")


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

    current_date = datetime.now().date() 
    current_time = datetime.now().time()  

    user_id = int(input("Enter your user ID (writer_id): "))

    try:
        # SQL query to insert the tweet
        insert_tweet_query = """
        INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
        VALUES (?, ?, ?, ?, ?, NULL)
        """

        # Inserting the tweet into the database
        CURSOR.execute(
            insert_tweet_query,
            (new_tid, user_id, tweet_text, current_date, current_time)
        )

        # SQL query for hashtag mentions
        insert_hashtag_query = """
        INSERT INTO hashtag_mentions (tid, term)
        VALUES (?, ?)
        """

        # Adding each valid hashtag to the hashtag_mentions table
        for tag in hashtag:
            CURSOR.execute(insert_hashtag_query, (new_tid, tag))

        # Save changes
        print("Tweet and hashtags successfully recorded!")

    except ValueError as ve:
        print(ve)  

    except Exception as error:
        # Error handling
        print(f"Error during database operation: {error}")


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
        #system_functions()
        

if __name__ == "__main__":
    main()