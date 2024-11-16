import sqlite3
from common_utils import *
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
    while True:
        print("\n\n*** YOUR FOLLOWER LIST ***\n")
        # Get the list of followers with pagination
        followers = getFollowerList(offset=offset, limit=5)

        if followers:
            print(f"{'User ID':<10}{'Name':<15}{'Status'}") 
            print("-" * 40)

            for fid, name in followers:
                follower_ids.append(fid)
                status = 'Following' if isFollowing(fid) else 'Unfollowed'
                print(f"{fid:<10}{name:<15}{status}")

        else:
            print("No more followers")

        user_input = input("\nEnter 'User ID' to check user detail, 'n' to see more followers, 'q' to quit, or 's' for Main Menu: ").strip().lower()
        if user_input == 'n':
            next_followers = getFollowerList(offset=offset + 5, limit=5)
            if next_followers:  # Only load more if there are more followers
               offset += 5  # Move to the next page
            else:
              print("No more follower to display")

        elif user_input == 'q':
            exit()  # exit the loop, go back to Main Menu
        elif user_input == 's':
            # system_functions(cursor, user_id)
            break
        else:
            follower_id = int(user_input)
            if follower_id in follower_ids:
                # Show detailed information of the follower
                showFollowerDetails(follower_id)
                # After viewing the details, return to the main list
                continue  # Continue the loop to display followers
            else:
                print("Invalid input. Please try again.")


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
      Displays detailed information about a specific follower, including contact info,tweet counts, and latest tweets.
      Offers options to follow this follower, see more tweets, or go back.

      Parameters:
          follower_id (int): The ID of the follower whose details are to be shown.

      """

    print("\n\n*** FOLLOWER DETAIL ***\n")
    
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
        print(f"{'User ID':<15}{'Name':<15}{'Email':<25}{'Phone':<15}{'#Tweets':<15}{'#Following':<15}{'#Followers'}")
        print("-" * 110)

        # Print follower details
        print(f"{follower_id:<15}{name:<15}{email:<25}{phone:<15}{tweet_count:<15}{following_count:<15}{follower_count}")

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
                    followUser(follower_id) #if not followed, call the function to follow

            elif user_input == 't':
                # # View more tweets (next 3 tweets)
                print(f"\nNext 3 tweets from {name}:")               
                new_tweets = viewTweets(follower_id, offset=offset, limit=3)
                if new_tweets:  
                    offset += 3  # Increment the offset for the next page of tweets only there is tweets in the next page
              
                  
            elif user_input == 'q':
                break  # Go back to the previous screen
            else:
                print("Invalid option. Please try again.")

    else:
        print("Follower not found.")

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
        print("No more tweets available.")
    
    return tweets

