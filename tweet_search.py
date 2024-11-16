from datetime import datetime

def search_tweets(cursor, user_id):
    """
    Search for tweets based on keywords and display options to reply, retweet, or view replies.
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
                
                # Fetch tweet statistics
                cursor.execute("SELECT COUNT(*) FROM retweets WHERE tid = ?", (tweet_id,))
                retweet_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM tweets WHERE replyto_tid = ?", (tweet_id,))
                reply_count = cursor.fetchone()[0]
                
                print(f"\nSelected Tweet: {tweet_text}")
                print(f"Date: {tweet_date} Time: {tweet_time}")
                print(f"Retweets: {retweet_count}, Replies: {reply_count}")
                
                # Interaction options
                print("\nOptions: ")
                print("1. Reply to this tweet")
                print("2. Retweet this tweet")
                print("3. View replies")
                print("4. Cancel")
                
                action = input("Choose an action: ").strip()
                if action == '1':
                    reply_to_tweet(cursor, user_id, tweet_id)
                elif action == '2':
                    retweet_tweet(cursor, user_id, tweet_id)
                elif action == '3':
                    view_replies(cursor, tweet_id)
                elif action == '4':
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

    reply = True
    while reply:
        reply_text = input("\nEnter your reply: ").strip()
        if reply_text:
            input_terms = reply_text.split(" ")
            hashtag = []
            valid = True  # Track if the input is valid
            
            for term in input_terms:
                if term[0] == "#" and len(term) > 1:
                    if term.lower() not in hashtag:
                        hashtag.append(term.lower())
                    else:
                        print("\nPlease try again: Duplicate hashtags are not allowed!\n")
                        valid = False  # Mark the input as invalid
                        break  # Exit the loop as input is already invalid
            
            if valid:  # If no duplicates, exit the loop
                reply = False

        else:
            print( "\nPlease try again: Reply cannot be empty!\n")
            reply = True

    cursor.execute(
       """
        SELECT MAX(tid) FROM tweets
       """
    )
    max_tid = cursor.fetchone()[0]
    if max_tid is None:
        new_tid = 1 
    else:
        new_tid = max_tid + 1  


    timestamp = datetime.now()
    cursor.execute(
        """
        INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
        VALUES (?, ?, ?, ?, ?, ?)
        """, 
        (new_tid, user_id, reply_text, timestamp.strftime('%Y-%m-%d'), timestamp.strftime('%H:%M:%S'), tweet_id)
    )
    for tag in hashtag:
        cursor.execute(
            """
            INSERT INTO hashtag_mentions (tid, term)
            VALUES (?, ?)
            """,
            (new_tid, tag)

        )


    cursor.connection.commit()
    print("Reply posted successfully!")


def retweet_tweet(cursor, user_id, tweet_id):
    """
    Retweet a selected tweet.
    :param cursor: SQLite database cursor for executing queries.
    :param user_id: The ID of the user currently logged in.
    :param tweet_id: The ID of the tweet to retweet.
    """
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

def view_replies(cursor, tweet_id):
    """
    View replies to a selected tweet.
    :param cursor: SQLite database cursor for executing queries.
    :param tweet_id: The ID of the tweet to view replies for.
    """
    cursor.execute(
        """
        SELECT t.text, t.tdate, t.ttime, u.name
        FROM tweets t
        JOIN users u ON t.writer_id = u.usr
        WHERE t.replyto_tid = ?
        ORDER BY t.tdate ASC, t.ttime ASC
        """, 
        (tweet_id,)
    )
    replies = cursor.fetchall()
    
    if replies:
        print("\nReplies:")
        for i, (text, tdate, ttime, writer_name) in enumerate(replies, start=1):
            print(f"{i}. {tdate} {ttime} - {writer_name}: {text}")
    else:
        print("No replies for this tweet.")


