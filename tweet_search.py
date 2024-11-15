from datetime import datetime

def search_tweets(cursor, user_id):
    """
    Search for tweets based on keywords and allow the user to reply or retweet.
    :param cursor: SQLite database cursor for executing queries.
    :param user_id: The ID of the user currently logged in.
    """
    print("*** TWEET SEARCH ***")
    
    # Prompt for search keywords
    keywords = input("Enter keywords (separated by spaces, use # for hashtags): ").strip().lower().split()
    
    # Build the query to search tweets
    search_query = '''
        SELECT DISTINCT t.tid, t.text, t.tdate, t.ttime
        FROM tweets t
        LEFT JOIN hashtag_mentions h ON t.tid = h.tid
        WHERE 
            (h.term IN ({}) OR t.text LIKE ?)
        ORDER BY t.tdate DESC, t.ttime DESC
    '''.format(",".join("?" for _ in keywords))
    
    # Execute search with parameters for both hashtags and text search
    params = keywords + [f"%{' '.join(keywords)}%"]
    cursor.execute(search_query, params)
    results = cursor.fetchall()
    
    # Display search results
    if results:
        print("\nSearch Results:")
        for i, (tid, text, tdate, ttime) in enumerate(results, start=1):
            print(f"{i}. {tdate} {ttime} - {text}")
        
        # Prompt user to select a tweet to interact with
        choice = input("\nSelect a tweet number to interact with it, or press Enter to return: ").strip()
        if choice.isdigit():
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(results):
                tweet_id, tweet_text, tweet_date, tweet_time = results[selected_index]
                
                print(f"\nSelected Tweet: {tweet_text}")
                print("Options: ")
                print("1. Reply to this tweet")
                print("2. Retweet this tweet")
                print("3. Cancel")
                
                action = input("Choose an action: ").strip()
                if action == '1':
                    reply_to_tweet(cursor, user_id, tweet_id)
                elif action == '2':
                    retweet_tweet(cursor, user_id, tweet_id)
                elif action == '3':
                    print("Cancelled.")
                else:
                    print("Invalid choice.")
            else:
                print("Invalid selection.")
    else:
        print("No tweets found with the given keywords.")
    
    input("\nPress Enter to return to the main menu...")

def reply_to_tweet(cursor, user_id, tweet_id):
    """
    Reply to a selected tweet.
    :param cursor: SQLite database cursor for executing queries.
    :param user_id: The ID of the user currently logged in.
    :param tweet_id: The ID of the tweet to reply to.
    """
    reply_text = input("\nEnter your reply: ").strip()
    if reply_text:
        timestamp = datetime.now()
        cursor.execute(
            """
            INSERT INTO tweets (writer_id, text, tdate, ttime, replyto_tid)
            VALUES (?, ?, ?, ?, ?)
            """, 
            (user_id, reply_text, timestamp.strftime('%Y-%m-%d'), timestamp.strftime('%H:%M:%S'), tweet_id)
        )
        cursor.connection.commit()
        print("Reply posted successfully!")
    else:
        print("Reply cannot be empty.")

def retweet_tweet(cursor, user_id, tweet_id):
    """
    Retweet a selected tweet.
    :param cursor: SQLite database cursor for executing queries.
    :param user_id: The ID of the user currently logged in.
    :param tweet_id: The ID of the tweet to retweet.
    """
    # Fetch the original tweet's writer_id
    cursor.execute("SELECT writer_id FROM tweets WHERE tid = ?", (tweet_id,))
    result = cursor.fetchone()
    
    if result:
        original_writer_id = result[0]
        timestamp = datetime.now()
        
        cursor.execute(
            """
            INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate)
            VALUES (?, ?, ?, ?, ?)
            """, 
            (tweet_id, user_id, original_writer_id, 0, timestamp.strftime('%Y-%m-%d'))
        )
        cursor.connection.commit()
        print("Tweet retweeted successfully!")
    else:
        print("Error: Unable to retweet. Original tweet not found.")

