import os
import sys
import getpass
from datetime import datetime
import sqlite3
from followers import follower_utils
from common_utils import *
from tweet_search import search_tweets

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
        
        move_cursor(4, 17)
        password = getpass.getpass("Enter Password: ").strip()

        # Query to check if the user exists and the password is correct
        CURSOR.execute("SELECT * FROM users WHERE upper(name) = ? AND pwd = ?", (user_name.upper(), password))
        user = CURSOR.fetchone()

        if user:
            move_cursor(6,0)
            print(ANSI["CLEARLINE"], end="\r") # Clear anything written previulsy in that line
            print_location(6, 0, "Login successful!")
            
            CURRENT_USER_ID = user[0]  # After a successful login, assign the user ID to CURRENT_USER_ID
            move_cursor(8,0)
            user_feed()  # need to test this function
            
            break  # Exit the loop if login is successful
        else:
            print_location(6, 0, "Invalid user ID or password. Please try again.")
            
            move_cursor(3, 0)
            print(ANSI["CLEARLINE"], end="\r") # Clear previous username
            
            move_cursor(4, 0)
            print(ANSI["CLEARLINE"], end="\r") # Clear previous password

def get_feed_tweets(offset=0, limit=5):
    """
    Retrieves tweets and retweets for the current user from followed users.

    Parameters:
        offset (int): The starting point for fetching tweets (default is 0).
        limit (int): The number of tweets to fetch in each request (default is 5).

    Returns:
        List[Tuple]: A list of tuples containing writer ID, writer name, tweet/retweet text, and tweet/retweet date.
    """
    global CURSOR, CURRENT_USER_ID

    CURSOR.execute('''
        SELECT writer_id, name, text, date FROM (
            -- Original tweets
            SELECT t.writer_id, u.name, t.text, t.tdate AS date, t.tdate || ' ' || t.ttime AS datetime
            FROM tweets t
            JOIN follows f ON t.writer_id = f.flwee
            JOIN users u ON t.writer_id = u.usr
            WHERE f.flwer = ?
            
            UNION ALL

            -- Retweets
            SELECT r.retweeter_id AS writer_id, u.name, t.text, r.rdate AS date, r.rdate AS datetime
            FROM retweets r
            JOIN tweets t ON r.tid = t.tid
            JOIN follows f ON r.retweeter_id = f.flwee
            JOIN users u ON r.retweeter_id = u.usr
            WHERE f.flwer = ?
        ) combined
        ORDER BY datetime DESC -- Sort by combined date and time descending
        LIMIT ? OFFSET ?
    ''', (CURRENT_USER_ID, CURRENT_USER_ID, limit, offset))

    return CURSOR.fetchall()



def user_feed():
    """
    Displays all tweets and retweets from users the current user is following.
    Uses the existing `viewTweets` function for pagination.
    """
    global CURRENT_USER_ID, CURSOR

    offset = 0  # Starting point for pagination
    limit = 5  # Number of tweets to display per page

    while True:
        # Fetch tweets and retweets from the users the current user is following
        tweets = get_feed_tweets(offset=offset, limit=limit)

        if tweets:
            print("\n*** YOUR FEED ***\n")
            print(f"{'User':<20}{'Tweet':<50}{'Date'}")
            print("-" * 80)

            for writer_id, name, text, tdate in tweets:
                print(f"{name:<20}{text[:45]:<50}{tdate}")
        else:
            if offset == 0:
                print("Your feed is empty. Start following users to see their tweets!")
            else:
                print("No more tweets to display.")

        # User prompt for further actions
        user_input = input("\nEnter 'n' for next 5 tweets,'q' to exit, or 's' for Main Menu: ").strip().lower()
        if user_input == 'n':
            offset += limit  # Increment offset to fetch the next set of tweets
        elif user_input == 'q':
            break
        elif user_input == 's':
            system_functions(CURSOR, CURRENT_USER_ID)
        else:
            print("Invalid input. Please try again.")
          
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
    
    while True:
      clear_screen()
      print_location(1,0, '*** SYSTEM FUNCTIONALITIES ***')
      print_location(3, 0,'1. Search for tweets')
      print_location(4, 0,'2. Search for users')
      print_location(5, 0,'3. Compose a tweet')
      print_location(6, 0,'4. List followers')
      print_location(7, 0,'5. Logout')

      user_input = input(">>>")
      
      if user_input == '1' or user_input == '1.':
          search_tweets(CURSOR, CURRENT_USER_ID)
          pass
      elif user_input == '2' or user_input == '2.':
          search_users(CURSOR, CURRENT_USER_ID)
      elif user_input == '3' or user_input == '3.':
          compose_tweet(CURSOR)
      elif user_input == '4' or user_input == '4.':
          follower_utils.showFollowers(CURRENT_USER_ID, CURSOR)
      elif user_input == '5' or user_input == '5.':
          logout()
          

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
        user_input = input("\nEnter 'n' to see more, user ID to view details, 'q' to quit, or 's' for Main Menu: ").strip().lower()
            
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
