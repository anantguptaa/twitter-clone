import sqlite3
from common_utils import *
from main import system_functions

CURRENT_USR = None
CURSOR = None

def getFollowers(user_id, cursor, row):
    global CURRENT_USR
    global CURSOR

    CURRENT_USR = user_id
    CURSOR = cursor
    """
      Retrieves and displays a list of followers for the given user, in groups of five.

       Parameters:
           user_id (int): The ID of the current user.
           cursor (sqlite3.Cursor): The database cursor to execute SQL queries.

       Functionality:
           - Fetches followers from the database in batches of five.
           - Displays each follower's name, ID, and whether the current user is following them.
           - Allows the user to view more followers, check follower details, or quit.
       """

    offset = 0
    

    while True:
        followers = getFollowerList(offset=offset, limit=5)
        if not followers:
            print_location(row, 0, "No followers to show.")
            break

        # Display followers
        print_location(row, 0, "Your Followers:")

        # followers = [(101, 'John Doe'), (102, 'Jane Smith'), (103, 'Alice Johnson')]
        row += 1  # Start printing followers from this row
        follower_ids = [] # Track valid follower IDs to verify user input

        for index, (fid, name) in enumerate(followers, start=1):
            follower_ids.append(fid)  # Add valid follower ID
            status = 'Following' if isFollowing(fid) else 'Unfollowed'
            print_location(row, 4, f"{index}. {name} (User ID: {fid}  Status: {status})")
            row += 1

        # Prompt options for user input
        print_location(row + 1, 0, "'User ID': Check user detail \t'n': for next 5 followers \t's': System Functionalities \t'q': quit: ")
        user_input = input(">>> ").strip().lower()

        if user_input == 'n':
            offset += 5
        elif user_input == 's':
            system_functions()
            return
        elif user_input == 'q':
            break  # Exit the loop
        else:
            try:
                follower_id = int(user_input)
                if follower_id in follower_ids:  # Validate input as a follower ID
                    showFollowerDetails(follower_id, row+2)
                else:
                    print_location(row + 2, 0, "Invalid input. Please try again.")
            except ValueError:
                print_location(row + 2, 0, "Invalid input. Please try again.")



def getFollowerList(offset=0, limit=5):
    """
    Retrieves a list of followers for a given user with pagination support.

    Parameters:
        user_id (int): The ID of the current user.
        offset (int): The starting point for fetching followers (default is 0).
        limit (int): The number of followers to fetch in each request (default is 5).

    Functionality:
        - Fetches followers from the database in batches.
        - Returns a list of follower IDs and names.
    """
    cursor = CURSOR
    user_id = CURRENT_USR

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

def showFollowerDetails(follower_id, row):
    """
      Displays detailed information about a specific follower, including contact info,
      tweet counts, and latest tweets.

      Parameters:
          follower_id (int): The ID of the follower whose details are to be shown.

      Functionality:
          - Fetches and displays the follower's name, email, and phone number.
          - Shows the number of tweets, people they follow, and their followers.
          - Displays the last three tweets.
          - Offers options to follow this follower, see more tweets, or go back.
      """

    print_location(1, 0, "*** FOLLOWER DETAIL ***")

    cursor = CURSOR
    cursor.execute("SELECT name, email, phone FROM users WHERE usr = ?", (follower_id,))
    follower = cursor.fetchone()

    if follower:
        name, email, phone = follower
        print_location(row, 0, f"{name} (User ID: {follower_id})")
        print_location(row + 1, 0, f"Email: {email}")
        print_location(row + 2, 0, f"Phone: {phone}")

        # Fetch counts for tweets, following, and followers
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (follower_id,))
        tweet_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (follower_id,))
        following_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (follower_id,))
        follower_count = cursor.fetchone()[0]

        print_location(row + 3, 0, f"Tweets: {tweet_count}, Following: {following_count}, Followers: {follower_count}")
        
        # Last 3 tweets
        cursor.execute(
        '''
            SELECT text, tdate FROM tweets
            WHERE writer_id = ?
            ORDER BY tdate DESC
            LIMIT 3
        ''', (follower_id,))

        tweets = cursor.fetchall()

        print_location(row + 4, 0, "\nLast 3 tweets:")
        tweet_row = row + 5  # Adjust this for formatting the tweets
        for tweet in tweets:
            print_location(tweet_row, 0, f"{tweet[1]} - {tweet[0]}")
            tweet_row += 1

        # Option to followers or see more tweets
        print_location(tweet_row+1, 0, "")
        user_input = input("Enter 'f' to follow this user or 'q' to quit: ").strip().lower()
        if user_input == 'f':
            followUser(follower_id, tweet_row+2)

    else:
        print_location(row, 0, "Follower not found.")

def followUser(follower_id, row):
    """
        Allows the current user to follow another user if they are not already following them.

        Parameters:
            follower_id (int): The ID of the user to follow.

        Functionality:
            - Checks if the current user already follows the specified user.
            - If not, adds a follow relationship in the database and commits the change.
        """
    user_id = CURRENT_USR
    cursor = CURSOR


    # Check if the follow relationship already exists
    if isFollowing(follower_id):
        print_location(row, 0, f"Error: You are already following user {follower_id}.")
        return

    else:
        # Insert followers relationship into the database if it doesn't exist
        cursor.execute(
            """
            INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, date('now'))
            """, (user_id, follower_id))

        cursor.connection.commit()
        print_location(row, 0, f"Successfully followed user{follower_id}.")


def isFollowing(follower_id):
    """
       Checks if the current user is already following a specified user.

       Parameters:
           follower_id (int): The ID of the user to check.

       Returns:
           bool: True if the current user is following the specified user, False otherwise.
       """

    user_id = CURRENT_USR
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
        offset (int): The offset (starting point) for fetching tweets (default is 0).
        limit (int): The number of tweets to fetch in each request (default is 3).

    Functionality:
        - Fetches and displays tweets from the specified follower.
        - Allows pagination by adjusting the offset.
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
        print("No more tweets available.")
