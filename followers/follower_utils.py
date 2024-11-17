import sqlite3
from common_utils import *
from search_users import user_feed
from main import system_functions

CURRENT_USER_ID = None
CURSOR = None

def showFollowers(user_id, cursor):
    global CURRENT_USER_ID, CURSOR

    CURRENT_USER_ID = user_id
    CURSOR = cursor
    """
      Retrieves and displays a list of followers for the given user, in groups of five.
      Displays each follower's name, ID, and whether the current user is following them.
      Allows the user to view more followers, check follower details, or quit.
    
    """
 
    offset = 0 # The starting point for fetching followers.
    follower_ids = []  # To keep track of all follower IDs
    clear_screen()
    print_location(1,0, "*** YOUR FOLLOWER LIST ***")
    
    while True:
        # Get the list of followers with pagination
        followers = getFollowerList(offset=offset, limit=5)

        if followers:
            print_location(3, 0, f"{'User ID':<10}{'Name':<15}{'Status'}")
            print_location(4, 0, "-" * 35)

            for idx, (fid, name) in enumerate(followers):
                follower_ids.append(fid)
                status = 'Following' if isFollowing(fid) else 'Unfollowed'
                print_location(5 + idx, 0, f"{fid:<10}{name:<15}{status}")
        else:
            print_location(3, 0, "No followers")

        # User interaction prompt
        print_location(10, 0, "-" * 35)
        print_location(12, 0, "Enter 'User ID' to check user detail, 'n' to see more followers, 'q' to quit, 'u' for user feed, or 's' for Main Menu: ")
        move_cursor(12, 120)
        print(ANSI["CLEARLINE"], end="\r")
        move_cursor(12, 120)
        user_input = input("").strip().lower()

        if user_input == 'n':
            next_followers = getFollowerList(offset=offset + 5, limit=5)
            if next_followers:  # Only load more if there are more followers
                offset += 5  # Move to the next page
            else:
                move_cursor(13,0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(13, 0, "No more followers to display")
        elif user_input == 'q':
            exit()
        elif user_input == 'u':
            user_feed(CURSOR, CURRENT_USER_ID)
            return
        elif user_input == 's':
            system_functions(cursor, user_id)
            return  # Return to the main menu
        else:
            try:
                follower_id = int(user_input)
                if follower_id in follower_ids:
                    # Show detailed information of the follower
                    showFollowerDetails(follower_id, cursor)
                    # After viewing the details, return to the main list
                    continue
                else:
                    move_cursor(13,0)
                    print(ANSI["CLEARLINE"], end="\r")
                    print_location(13, 0, "Invalid User ID. Please try again.")
            except ValueError:
                move_cursor(13,0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(13, 0, "Invalid input. Please try again.")

def getFollowerList(offset=0, limit=5):
    """
    Retrieves a list of followers for a given user with pagination support.

    Parameters:
        user_id (int): The ID of the current user.
        offset (int): The starting point for fetching followers (default is 0).
        limit (int): The number of followers to fetch in each request (default is 5).
    """
    cursor = CURSOR
    user_id = CURRENT_USER_ID

    cursor.execute('''
        SELECT u.usr, u.name 
        FROM follows f
        JOIN users u ON f.flwer = u.usr
        WHERE f.flwee = ?
        LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))

    followers = cursor.fetchall()

    if followers:
        follower_list = []
        for fid, name in followers:
            follower_list.append((fid, name))
        return follower_list
    else:
        return None

def showFollowerDetails(follower_id, cursor):
    """
    Displays detailed information about a specific follower, including contact info, tweet counts, and latest tweets.
    Offers options to follow this follower, see more tweets, or go back.

    Parameters:
        follower_id (int): The ID of the follower whose details are to be shown.
    """

    clear_screen()
    print_location(1, 0, "*** FOLLOWER DETAIL ***")
    
    global CURSOR
    CURSOR = cursor
    cursor.execute("SELECT name, email, phone FROM users WHERE usr = ?", (follower_id,))
    follower = cursor.fetchone()

    if follower:
        name, email, phone = follower

        # Fetch counts for tweets, following, and followers
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (follower_id,))
        tweet_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (follower_id,))
        following_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (follower_id,))
        follower_count = cursor.fetchone()[0]

        # Print header
        print_location(3, 0, f"{'User ID':<15}{'Name':<15}{'Email':<25}{'Phone':<15}{'#Tweets':<15}{'#Following':<15}{'#Followers'}")
        print_location(4, 0, "-" * 110)

        # Print follower details
        print_location(5, 0, f"{follower_id:<15}{name:<15}{email:<25}{phone:<15}{tweet_count:<15}{following_count:<15}{follower_count}")

        # Show the first set of 3 tweets
        print_location(7, 0, f"Last 3 tweets from {name}:")
        if not viewTweets(follower_id, offset=0, limit=3):
            print_location(8,4,"No tweets by this user.")
        offset = 3  # For the next set of tweets

        while True:
            # Option to follow, see more tweets, or go back
            print_location(12, 0, "Enter 'f' to follow this user, 't' to see more tweets, 'q' to quit, 'u' for user feed, or 's' for Main Menu: ")
            move_cursor(12, 110)
            print(ANSI["CLEARLINE"], end="\r")
            move_cursor(12, 110)     # Move cursor for user input
            user_input = input("").strip().lower()  
            

            if user_input == 'f':
                if isFollowing(follower_id):
                    move_cursor(14,0)
                    print(ANSI["CLEARLINE"], end="\r")
                    print_location(14, 0, "You are already following this user.")
                else:
                    followUser(follower_id)  # Call the function to follow
                    move_cursor(14,0)
                    print(ANSI["CLEARLINE"], end="\r")
                    print_location(14, 0, "You are now following this user.")

            elif user_input == 't':
                # View more tweets (next 3 tweets)
                print_location(7, 0, f"Next 3 tweets from {name}:")
                new_tweets = viewTweets(follower_id, offset=offset, limit=3)
                if new_tweets:
                    offset += 3  # Increment the offset for the next page of tweets
                else:
                    move_cursor(14,0)
                    print(ANSI["CLEARLINE"], end="\r")
                    print_location(14, 0, "No more tweets to display.")
            elif user_input == 'q':
                exit()      
            elif user_input == 's':
                system_functions(CURSOR, CURRENT_USER_ID)
                return
            elif user_input == 'u':
                user_feed(CURSOR, CURRENT_USER_ID)
                return
            else:
                move_cursor(14,0)
                print(ANSI["CLEARLINE"], end="\r")
                print_location(14, 0, "Invalid option. Please try again.")

    else:
        print_location(3, 0, "Follower not found.")


def followUser(follower_id):
    """
        Allows the current user to follow another user if they are not already following them.
        Checks if the current user already follows the specified user, If not, adds a follow relationship in the database and commits the change.

        Parameters:
            follower_id (int): The ID of the user to follow.
        """
    user_id = CURRENT_USER_ID
    cursor = CURSOR


    # Check if the follow relationship already exists
    if isFollowing(follower_id):
        # print(f"Error: You are already following user {follower_id}.")
        return

    else:
        # Insert followers relationship into the database if it doesn't exist
        cursor.execute(
            """
            INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, date('now'))
            """, (user_id, follower_id))

        cursor.connection.commit()
        print(f"Successfully followed user{follower_id}.")


def isFollowing(follower_id):
    """
       Checks if the current user is already following a specified user.

       Parameters:
           follower_id (int): The ID of the user to check.
       """

    user_id = CURRENT_USER_ID
    cursor = CURSOR
    cursor.execute(
        """
        SELECT 1 FROM follows WHERE flwer = ? AND flwee = ?
        """, (user_id, follower_id))

    existing_follow = cursor.fetchone()
    return existing_follow is not None


def viewTweets(follower_id, offset=0, limit=3):
    """
    Displays a set of tweets from a follower, given the offset for pagination.

    Parameters:
        follower_id (int): The ID of the follower whose tweets are to be shown.
        offset (int): starting point for fetching tweets (default is 0).
        limit (int): The number of tweets to fetch in each request (default is 3).
    """
    
    cursor = CURSOR
    cursor.execute('''
        SELECT text, tdate FROM tweets
        WHERE writer_id = ?
        ORDER BY tdate DESC
        LIMIT ? OFFSET ?
    ''', (follower_id, limit, offset))

    tweets = cursor.fetchall()

    if tweets:
        for tweet in tweets:
            print(f"{tweet[1]} - {tweet[0]}")
    else:
        return False
    
    return tweets

