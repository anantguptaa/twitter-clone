
def search_tweets(cursor):
    '''Search for tweets based on keywords'''
    print("*** TWEET SEARCH ***")
    
    # Prompt for search keywords
    keywords = input("Enter keywords (separated by spaces, use # for hashtags): ").strip().lower().split()
    
    # Build the query to search tweets
    search_query = '''
        SELECT t.tid, t.text, t.tdate
        FROM tweets t
        LEFT JOIN hashtag_mentions h ON t.tid = h.tid
        WHERE 
            (h.term IN ({}) OR t.text LIKE ?)
        ORDER BY t.tdate DESC
    '''.format(",".join("?" for _ in keywords))
    
    # Execute search with parameters for both hashtags and text search
    params = keywords + [f"%{' '.join(keywords)}%"]  # To cover both hashtag and text conditions
    cursor.execute(search_query, params)
    results = cursor.fetchall()
    
    # Display search results
    if results:
        print("Search Results:")
        for i, (tid, text, tdate) in enumerate(results, start=1):
            print(f"{i}. {tdate} - {text}")
        
        input("\nPress Enter to return to the main menu...")
    else:
        print("No tweets found with the given keywords.")
        input("Press Enter to return to the main menu...")
