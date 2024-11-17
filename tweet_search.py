from datetime import datetime
from common_utils import *
from search_users import user_feed

def search_tweets(cursor, user_id):
    """
    Search for tweets based on keywords and display options to reply, retweet, or view replies.
    Displays results 5 at a time.
    :param cursor: SQLite database cursor for executing queries.
    :param user_id: The ID of the user currently logged in.
    """
    global USER_ID
    USER_ID = user_id

    clear_screen()
    print_location(1, 0, "*** TWEET SEARCH ***")

    
    # Prompt for search keywords
    inp = False
    while not inp:
        move_cursor(4, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(4, 0, "Enter keywords (separated by spaces, use # for hashtags): ")
        move_cursor(4, 58)
        keywords = input("").strip().lower().split()
        if not keywords:
            move_cursor(3, 65)
            print(ANSI["CLEARLINE"], end="\r")  
            print_location(3, 0, "Invalid Input: Keyword cannot be empty")
        else:
            move_cursor(3, 65)
            print(ANSI["CLEARLINE"], end="\r")  
            inp = True

    
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
    
    # Display search results 5 at a time
    if results:
        print("\nSearch Results:")
        page_size = 5
        total_results = len(results)
        current_index = 0

        clear_screen()
        print("*** SEARCH RESULTS ***")
        while current_index < total_results:

            for row in range(5, 12):
                move_cursor(row, 0)
                print(ANSI["CLEARLINE"], end="\r")

            move_cursor(3, 0)
            for i in range(current_index, min(current_index + page_size, total_results)):
                tid, text, tdate, ttime = results[i]
                print(f"{i + 1}. {tdate} {ttime} - {text}")
            
            # Check if more tweets are available
            if current_index + page_size < total_results:
                print("\nPress 'n' for the next 5 tweets, press 'u' to return to user feed or choose a tweet number to interact.")
            else:
                print("\nNo more tweets. Choose a tweet number to interact, press 'u' to return to user feed or press Enter to return.")
            
            choice = input("Your choice: ").strip()
            move_cursor(12, 0)
            print(ANSI["CLEARLINE"], end="\r")
            if choice.lower() == 'u':
                user_feed(cursor, user_id)
            elif choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < total_results:
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
                    
                    not_selected = True
                    while not_selected:
                        action = input("Choose an action: ").strip()
                        if action == '1':
                            reply_to_tweet(cursor, user_id, tweet_id)
                            not_selected = False
                        elif action == '2':
                            retweet_tweet(cursor, user_id, tweet_id)
                            not_selected = False
                        elif action == '3':
                            view_replies(cursor, tweet_id)
                            not_selected = False
                        elif action == '4':
                            print("Cancelled.")
                            not_selected = False
                        else:
                            print("Invalid choice. Please try again.")
                else:
                    print("Invalid selection.")
            elif choice.lower() == 'n' and current_index + page_size < total_results:
                current_index += page_size
            elif choice == '':
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print_location(6, 0, "No tweets found with the given keywords.")
    
    input("\nPress Enter to return to the main menu...")
    clear_screen()
    from main import system_functions
    system_functions(cursor, user_id)

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
    input("\nPress Enter to return to the main menu...")
    clear_screen()
    from main import system_functions
    system_functions(cursor, user_id)


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
        input("\nPress Enter to return to the main menu...")
        clear_screen(    )
        from main import system_functions
        system_functions(cursor, user_id)
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
    input("\nPress Enter to return to the main menu...")
    clear_screen(    )
    from main import system_functions
    system_functions(cursor, USER_ID)