from followers import follower_utils
from common_utils import *

CURRENT_USER_ID = None
CURSOR = None

def search_users(cursor, current_user_id):
    '''
    ## this fucntion is used to search users, and it calls showFollowerDetails
    when asked to view the follower details

    ### Args:
        - `cursor (_type_)`: sql cursor for database
        - `current_user_id (_type_)`: current user id in the database
    '''
    global CURSOR, CURRENT_USER_ID
    CURSOR = cursor
    CURRENT_USER_ID = current_user_id
    clear_screen()
    print_location(1, 0, "*** SEARCH FOR USERS ***")
    
    offset = 0
    limit = 5
    
    while True:
        while True:
            move_cursor(3, 16)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(3, 0, "Enter Keyword: ")
            move_cursor(3, 16)
            keyword = input("").strip()
            move_cursor(5,0)
            print(ANSI["CLEARLINE"], end="\r")
            if not keyword:
                print_location(5,0,"Invalid Input. Keyowrd cannot be empty.")
            else:
                break
                
        
        # Fetch users based on the keyword, offset, and limit
        users = get_users_list(keyword, offset, limit)
    
        if not users:
            move_cursor(5,0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(5, 0, "No users found.")
            move_cursor(3, 16)  # Move cursor back to the keyword input position
            print(ANSI["CLEARLINE"], end="\r")
            continue
        
        move_cursor(5, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(5, 0, "Users found: ")

        for index, (usr, name) in enumerate(users, start=1):
            print_location(5 + index, 4, f"{index}. {name} (User ID: {usr})")
        
        break  # Exit the loop once users are displayed
    
    # Extract the user IDs from the result for validation
    valid_user_ids = [user[0] for user in users]
    
    print_location(12,0,"Enter 'n' to see more, 'User ID' to view user details, 'q' to quit, 'u' for user feed, or 's' for Main Menu: ")
    while True:
        move_cursor(12, 110)
        user_input = input("").strip().lower()

        if user_input == 'n':
            # Load the next page of users
            offset += 5  # Move to the next set of users
            next_users = get_users_list(keyword, offset=offset, limit=limit)
            
            if next_users:  # Only display more users if there are more
                print_location(5, 0, "Users found: ")
                
                for row in range(6, 11):
                    move_cursor(row, 0)
                    print(ANSI["CLEARLINE"], end="\r")
                
                for index, (usr, name) in enumerate(next_users, start=1):
                    print_location(5 + index, 4, f"{index}. {name} (User ID: {usr})")
                    
                users.extend(next_users)  # Add the new users to the list
                valid_user_ids = [user[0] for user in users]
                move_cursor(12, 110)
                print(ANSI["CLEARLINE"], end="\r")
                
            else:
                move_cursor(13,0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(13, 0, "No more users to display.")
                move_cursor(12, 110)
                print(ANSI["CLEARLINE"], end="\r")
                
        elif user_input == 'u':
            user_feed(CURSOR, CURRENT_USER_ID)
            return
        
        elif user_input == 'q':
            exit()  # Exit the program
        
        elif user_input == 's':
            from main import system_functions
            system_functions(cursor, current_user_id)  # Return to the main menu
            return
    
        else:
            try:
                # Validate if the input is a valid user ID
                user_id = int(user_input)
                if user_id in valid_user_ids:
                    # Show the details of the selected user
                    move_cursor(8 + len(users), 0)
                    print(ANSI["CLEARLINE"], end="\r")
                    follower_utils.showFollowerDetails(user_id, CURSOR)
                else:
                    print("Invalid User ID. Please try again.")
                    move_cursor(7+index, 110)
                    print(ANSI["CLEARLINE"], end="\r")
            except ValueError:
                print("Invalid input. Please enter a valid User ID.")
                move_cursor(7+index, 110)
                print(ANSI["CLEARLINE"], end="\r")

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

def user_feed(cursor, current_user_id):
    """
    Displays all tweets and retweets from users the current user is following.
    Uses the existing `viewTweets` function for pagination.
    """
    global CURRENT_USER_ID, CURSOR

    CURSOR = cursor
    CURRENT_USER_ID = current_user_id

    offset = 0  # Starting point for pagination
    limit = 5  # Number of tweets to display per page

    # Clear the previous screen output
    clear_screen()
    print_location(1, 0, "*** YOUR FEED ***\n")
    while True:
        # Fetch tweets and retweets from the users the current user is following
        tweets = get_feed_tweets(CURSOR, offset=offset, limit=limit)

        if tweets:
            for row in range(5, 10):
                move_cursor(row, 0)
                print(ANSI["CLEARLINE"], end="\r")

            print_location(3, 0, f"{'User':<20}{'Tweet':<50}{'Date'}")
            print_location(4, 0, "-" * 80)

            # Display each tweet or retweet
            for index, (writer_id, name, text, tdate) in enumerate(tweets, start=1):
                print_location(4 + index, 0, f"{name:<20}{text[:45]:<50}{tdate}")

        else:
            if offset == 0:
                print_location(3, 0, "Your feed is empty. Start following users to see their tweets!")
            else:
                move_cursor(12, 0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(12, 0, "No more tweets to display.")
                move_cursor(13, 65)
                print(ANSI["CLEARLINE"], end="\r")
                

        # User prompt for further actions
        print_location(10, 0, "-" * 80)
        print_location(13, 0, "Enter 'n' for next 5 tweets, 'q' to exit, or 's' for Main Menu: ")
        move_cursor(13, 65)
        user_input = input("").strip().lower()
        if user_input == 'n':
            move_cursor(11, 0)
            print(ANSI["CLEARLINE"], end="\r")
            move_cursor(13,65)
            print(ANSI["CLEARLINE"], end="\r")
            offset+=5
        elif user_input == 'q':
            exit()
        elif user_input == 's':
            from main import system_functions
            system_functions(CURSOR, CURRENT_USER_ID)
        else:
            move_cursor(11, 0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(11, 0, "Invalid input. Please try again.")
            move_cursor(13, 65)
            print(ANSI["CLEARLINE"], end="\r")

def get_feed_tweets(cursor, offset=0, limit=5):
    """
    Retrieves tweets and retweets for the current user from followed users.

    Parameters:
        offset (int): The starting point for fetching tweets (default is 0).
        limit (int): The number of tweets to fetch in each request (default is 5).

    Returns:
        List[Tuple]: A list of tuples containing writer ID, writer name, tweet/retweet text, and tweet/retweet date.
    """
    global CURSOR, CURRENT_USER_ID
    
    CURSOR = cursor

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