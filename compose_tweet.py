from datetime import datetime
from common_utils import *
from search_users import user_feed


def compose_tweet(cursor, CURRENT_USER_ID):
    CURSOR = cursor

    # taing input from user
    clear_screen()
    print_location(1, 10, "*** COMPOSE A TWEET ***")
    print_location(2, 10, "=======================")
    inp = True
    while inp:
        move_cursor(5, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(5, 0, "Enter Tweet: ")
        move_cursor(5, 15)
        tweet_text = input("")
        valid = True

        if tweet_text:
            # making list of input words
            input_terms = tweet_text.split(" ")
            hashtag = []
            for term in input_terms:
                if term[0] == "#" and len(term) > 1:
                    if term.lower() not in hashtag:
                        hashtag.append(term.lower())
                    else:
                        move_cursor(4, 0)
                        print(ANSI["CLEARLINE"], end="\r")
                        print_location(4, 0, "Please try again: Duplicate hashtags are not allowed!")
                        valid = False
            if valid:
                inp = False
        else:
            move_cursor(4, 0)
            print(ANSI["CLEARLINE"], end="\r")
            print_location(4, 0, "Please try again: Empty tweets are not allowed")


    CURSOR.execute(
       """
        SELECT MAX(tid) FROM tweets
       """
    )
    max_tid = CURSOR.fetchone()[0]
    # setting 1 if it is first tweet or setting it as max+1 for next tweet
    if max_tid is None:
        new_tid = 1 
    else:
        new_tid = max_tid + 1  

    current_date = datetime.now().strftime("%Y-%m-%d") 
    current_time = datetime.now().strftime("%H:%M:%S")  


    # SQL query to insert the tweet
    insert_tweet_query = """
    INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
    VALUES (?, ?, ?, ?, ?, NULL)
    """

    # Inserting the tweet into the database
    CURSOR.execute(
        insert_tweet_query,
        (new_tid, CURRENT_USER_ID, tweet_text, current_date, current_time)
    )

    # SQL query for hashtag mentions
    insert_hashtag_query = """
    INSERT INTO hashtag_mentions (tid, term)
    VALUES (?, ?)
    """

    # Adding each valid hashtag to the hashtag_mentions table
    for tag in hashtag:
        CURSOR.execute(insert_hashtag_query, (new_tid, tag))

    print_location(6, 0, "Tweet and hashtags successfully recorded!")
    CURSOR.connection.commit()

    i = True
    while i:
        move_cursor(9, 0)
        print(ANSI["CLEARLINE"], end="\r")
        print_location(9, 0, "Enter 'u' to view user feed, 's' to go back to Main Menu or 'q' to quit:  ")
        move_cursor(9, 75)
        user_input = input("")
        if user_input.lower() == 'u':
            user_feed(CURSOR, CURRENT_USER_ID)
            i = False
        elif user_input.lower() == 'q':
            exit()
            i = False
        elif user_input.lower() == 's':
            from main import system_functions
            system_functions(CURSOR, CURRENT_USER_ID)
            i = False
        else:
            print_location(8 , 0, "Invalid Input: Please Try Again")
            i = True