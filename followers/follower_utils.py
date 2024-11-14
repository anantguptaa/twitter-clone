import sqlite3
CURRENT_USR = None
CURSOR = None

def getFollowers(user_id, cursor):
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
            print("No followers to show.")
            break

        # Display followers
        print("\nYour Followers:")

        # followers = [(101, 'John Doe'), (102, 'Jane Smith'), (103, 'Alice Johnson')]
        index = 1
        follower_ids = []  # To keep track of all follower IDs
        for fid, name in followers:
            follower_ids = []  # To keep track of all follower IDs
            print(f"{index}. {name} (User ID: {fid}  Status: {'Following' if isFollowing(fid) else 'Unfollowed'}) ")
            index += 1


        # Ask for more or quit
        user_input = input("\n'User ID': Check user detail \t'n': for next 5 followers \t'q': quit: \n").strip().lower()

        if user_input == 'n':
            offset += 5
        elif user_input == 'q':
            break
        else:
            try:
                follower_id = int(user_input)
                if follower_id in follower_ids:  # Check if the input is a valid follower ID
                    showFollowerDetails(follower_id)
                else:
                    print("Invalid input. Please try again.")

            except (IndexError, ValueError):
                print("Invalid input. Please try again.")


def showFollowerDetails(follower_id):
    cursor = CURSOR
    cursor.execute("SELECT name, email, phone FROM users WHERE usr = ?", (follower_id,))
    follower = cursor.fetchone()

    if follower:
        name, email, phone = follower
        print(f"\n{name} (User ID: {follower_id})")
        print(f"Email: {email}")
        print(f"Phone: {phone}")

        # Number of tweets
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer_id = ?", (follower_id,))
        tweet_count = cursor.fetchone()[0]

        # Number of people they followers
        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (follower_id,))
        following_count = cursor.fetchone()[0]

        # Number of followers
        cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (follower_id,))
        follower_count = cursor.fetchone()[0]

        print(f"Tweets: {tweet_count}, Following: {following_count}, Followers: {follower_count}")

        # Last 3 tweets
        cursor.execute(
        '''
            SELECT text, tdate FROM tweets
            WHERE writer_id = ?
            ORDER BY tdate DESC
            LIMIT 3
        ''', (follower_id,))

        tweets = cursor.fetchall()

        print("\nLast 3 tweets:")
        for tweet in tweets:
            print(f"{tweet[1]} - {tweet[0]}")

        # Option to followers or see more tweets
        user_input = input("\nEnter 'f' to followers this user or 'q' to quit: ").strip().lower()
        if user_input == 'f':
            followUser(follower_id)

    else:
        print("Follower not found.")


def followUser(follower_id):
    # Check if the follow relationship already exists
    user_id = CURRENT_USR
    cursor = CURSOR

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