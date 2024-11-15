class User:
    def __init__(self, user_id, username, name, email, phone):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.phone = phone
        self.followers = []
        self.following = []
        self.tweets = []

    def get_followers(self, cursor):
        cursor.execute(
        '''
            SELECT u.usr, u.name FROM follows f
            JOIN users u ON f.flwer = u.usr
            WHERE f.flwee = ?
        ''', (self.user_id,))
        self.followers = cursor.fetchall()

    def get_tweets(self, cursor):
        cursor.execute(
        '''
            SELECT text, tdate FROM tweets
            WHERE writer_id = ?
            ORDER BY tdate DESC
            LIMIT 3
        ''', (self.user_id,))
        self.tweets = cursor.fetchall()

    def display_info(self):
        print(f"Name: {self.name}")
        print(f"Username: {self.username}")
        print(f"Email: {self.email}")
        print(f"Phone: {self.phone}")
        print(f"Followers: {len(self.followers)}")
        print(f"Tweets: {len(self.tweets)}")
        for tweet in self.tweets:
            print(f"{tweet[1]} - {tweet[0]}")
