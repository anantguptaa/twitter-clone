# Twitter CLI Clone

A command-line Twitter clone built with Python and SQLite, simulating a social media platform. Users can sign up, log in, and perform actions such as posting tweets, replying, retweeting, searching tweets by keywords/hashtags, and managing followers. The system supports paginated feeds, user search, and hashtag-based tweet retrieval.

## Features
- **User Authentication**: Sign up and log in securely.
- **Tweet Management**: Post tweets, reply to tweets, and retweet.
- **Search Functionality**: Find tweets by keywords or hashtags.
- **Followers System**: Follow/unfollow users and view followers.
- **Paginated Feed**: View tweets from followed users in batches of five.
- **SQLite Database**: Persistent data storage with relational schema.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/anantguptaa/twitter-clone.git
   cd twitter-cli
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the SQLite database:
   ```bash
   python init_db.py
   ```

## Usage
Run the main script to start the CLI:
```bash
python main.py
```
Users can then follow on-screen prompts to log in, post tweets, follow users, search tweets, and more.

## Database Schema
The SQLite database consists of the following tables:
- **users**: Stores user information.
- **tweets**: Stores tweet content.
- **follows**: Manages follower relationships.
- **retweets**: Tracks retweeted tweets.
- **hashtag_mentions**: Maps hashtags to tweets.
- **lists & include**: Allows users to categorize tweets.

## File Structure
```
📂 twitter-cli
 ├── main.py               # Entry point of the application
 ├── model.db              # Sample Database
 ├── follower_utils.py     # Manage followers
 ├── compose_tweet.py      # Tweet creation and posting
 ├── tweet_search.py       # Tweet searching functionality
 ├── search_users.py       # User search functionality
 ├── requirements.txt      # Dependencies
 ├── README.md             # Project documentation
```

## Contributors
- **Anant Gupta** - System functionalities, user search, login, and feed.
- **Luke Thomas** - Tweet search and database setup.
- **Yuheng Li** - Followers management.
- **Gurbaaz Gill** - Tweet composition, login/logout optimization.
