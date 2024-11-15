import sqlite3
from common_utils import *

CURRENT_USR = None
CURSOR = None

def displayFollowers(user_id, cursor):
    global CURRENT_USR, CURSOR

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
        clear_screen()
        print_location(1, 0, "*** YOUR FOLLOWER LIST ***")
        # Get the list of followers with pagination
        followers = getFollowerList(offset=offset, limit=5)

        if followers:
            print(f"{'User ID':<10}{'Name':<15}{'Status'}")
            print("-" * 40)

            follower_ids = []  # To keep track of all follower IDs
            for fid, name in followers:
                follower_ids.append(fid)
                status = 'Following' if isFollowing(fid) else 'Unfollowed'
                print(f"{fid:<10}{name:<15}{status:<10}")
        else:
            print("No more followers")

        user_input = input(
            "\nEnter 'User ID' to check user detail, 'n' to see more followers, or 'q' to go back: ").strip().lower()

        if user_input == 'n':
            offset += 5  # Load the next set of followers
        elif user_input == 'q':
            break  # Exit the loop
        else:
            follower_id = int(user_input)
            if follower_id in follower_ids:
                # Show detailed information of the follower
                showFollowerDetails(follower_id)
                # After viewing the details, return to the main list
                continue  # Continue the loop to display the next set of followers
            else:
                print("Invalid input. Please try again.")



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

def showFollowerDetails(follower_id):
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

        # Fetch counts for tweets, following, and followers
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (follower_id,))
        tweet_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (follower_id,))
        following_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (follower_id,))
        follower_count = cursor.fetchone()[0]

        # Print header
        print(f"{'User ID':<15}{'Name':<15}{'Email':<25}{'Phone':<15}{'#Tweets':<15}{'#Following':<15}{'#Followers'}")
        print("-" * 110)

        # Print follower details
        print(f"{follower_id:<15}{name:<15}{email:<25}{phone:<15}{tweet_count:<15}{following_count:<15}{follower_count:<10}")

        # Show the first set of 3 tweets
        print(f"\nLast 3 tweets from {name}:")
        viewTweets(follower_id, offset=0, limit=3)
        offset = 3  # For the next set of tweets

        while True:
            # Option to follow, see more tweets, or go back
            user_input = input("\nEnter 'f' to follow this user, 't' to see more tweets, or 'q' to go back: ").strip().lower()

            if user_input == 'f':
                if(isFollowing(follower_id)):
                    print("You have followed her/him")
                else:
                    followUser(follower_id)  # Assuming you have the followUser function implemented

            elif user_input == 't':
                # View more tweets (next 3 tweets)
                print(f"\nNext 3 tweets from {name}:")
                viewTweets(follower_id, offset=offset, limit=3)
                offset += 3  # Increment the offset for the next page of tweets
            elif user_input == 'q':
                break  # Go back to the previous screen
            else:
                print("Invalid option. Please try again.")

    else:
        print("Follower not found.")

def followUser(follower_id):
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
        print(f"Error: You are already following user {follower_id}.")
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
