# follower_util
import sqlite3
from main import print_location, system_functions
CURRENT_USR = None
CURSOR = None

def getFollowers(user_id, cursor, row):
    global CURRENT_USR
    global CURSOR

    CURRENT_USR = user_id
    CURSOR = cursor

    offset = 0
    
    while True:
        cursor.execute(
        '''
            SELECT u.usr, u.name FROM follows f
            JOIN users u ON f.flwer = u.usr
            WHERE f.flwee = ?
            LIMIT 5 OFFSET ?
        ''', (user_id, offset))

        followers = cursor.fetchall()
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
            break
        else:
            try:
                follower_id = int(user_input)
                if follower_id in follower_ids:  # Validate input as a follower ID
                    showFollowerDetails(follower_id, row+2)
                else:
                    print_location(row + 2, 0, "Invalid input. Please try again.")
            except ValueError:
                print_location(row + 2, 0, "Invalid input. Please try again.")


def showFollowerDetails(follower_id, row):
    cursor = CURSOR
    cursor.execute("SELECT name, email, phone FROM users WHERE usr = ?", (follower_id,))
    follower = cursor.fetchone()

    if follower:
        name, email, phone = follower
        print_location(row, 0, f"{name} (User ID: {follower_id})")
        print_location(row + 1, 0, f"Email: {email}")
        print_location(row + 2, 0, f"Phone: {phone}")

        # Number of tweets
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (follower_id,))
        tweet_count = cursor.fetchone()[0]

        # Number of people they followers
        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (follower_id,))
        following_count = cursor.fetchone()[0]

        # Number of followers
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
    # Check if the follow relationship already exists
    user_id = CURRENT_USR
    cursor = CURSOR

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
    Check if the user is already following the given follower.
    """
    user_id = CURRENT_USR
    cursor = CURSOR
    cursor.execute(
        """
        SELECT 1 FROM follows WHERE flwer = ? AND flwee = ?
        """, (user_id, follower_id))

    existing_follow = cursor.fetchone()
    return existing_follow is not None