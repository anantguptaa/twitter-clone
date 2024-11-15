import os
import sys
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
        # compose a tweet function to be added by gurbaaz
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
        # system_functions()
        

if __name__ == "__main__":
    main()