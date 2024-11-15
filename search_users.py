from main import system_functions
from followers import follower_utils
from common_utils import *

def search_users(cursor, current_user_id):
    global CURSOR, CURRENT_USER_ID
    clear_screen()
    print_location(1,0,"*** SEARCH FOR USERS ***")
    
    while True:
        print_location(3, 0, "Enter Keyword: ")
        move_cursor (3, 16)
        keyword = input("").strip()
        
        offset = 0
        limit = 5
        users = get_users_list(keyword, offset, limit)
    
        if not users:
            print_location(5, 0, "No users found.")
            move_cursor(3, 16)  # Move cursor back to the keyword input position
            print(ANSI["CLEARLINE"], end="\r")
            continue
        
        move_cursor(5,0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(5, 0, "Users found: ")
        for index, (usr, name) in enumerate(users, start=1):
                print_location(5 + index, 4, f"{index}. {name} (User ID: {usr})")
        move_cursor(5+index,0)
        break
    
    # Extract the user IDs
    valid_user_ids = [user[0] for user in users]
    
    while True:
        # Get user input to proceed
        user_input = input("\nEnter 'n' to see more, 'User ID' to view user details, 'q' to quit, or 's' for Main Menu: ").strip().lower()

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
                # Check if the input is a valid user ID
                user_id = int(user_input)
                if user_id in valid_user_ids:
                    follower_utils.showFollowerDetails(user_id, CURSOR)
                else:
                    print("\nInvalid User ID. Please try again.")
            except ValueError:
                print("\nInvalid input. Please enter a valid User ID.")

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
            SELECT t.writer_id, u.name, t.text, t.tdate AS date
            FROM tweets t
            JOIN follows f ON t.writer_id = f.flwee
            JOIN users u ON t.writer_id = u.usr
            WHERE f.flwer = ?
            
            UNION ALL

            -- Retweets
            SELECT r.retweeter_id AS writer_id, u.name, t.text, r.rdate AS date
            FROM retweets r
            JOIN tweets t ON r.tid = t.tid
            JOIN follows f ON r.retweeter_id = f.flwee
            JOIN users u ON r.retweeter_id = u.usr
            WHERE f.flwer = ?
        ) combined
        ORDER BY date DESC
        LIMIT ? OFFSET ?
    ''', (CURRENT_USER_ID, CURRENT_USER_ID, limit, offset))

    return CURSOR.fetchall()