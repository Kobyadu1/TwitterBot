import tweepy, requests, pyodbc, datetime, logging
import azure.functions as func
from datetime import datetime, timezone


server = ''
database = ''
userDB = ''
pwd = '!'
driver = '{ODBC Driver 17 for SQL Server}'

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
usernames = ['livesquawk']
count = 1

def ret_tweet():
    try:
        for username in usernames:
            url = 'https://twitter.com/' + username + '/status/'
            tweets = tweepy.Cursor(api.user_timeline, id=username, include_entities=True).items(count)
            tweetObj = tweets.next()
            dt_string = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            currdt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
            
            tweetID = tweetObj.id
            tweet = url + str(tweetID)

            if (currdt - tweetObj.created_at).total_seconds() > 60:
                return

            with pyodbc.connect(
                    'DRIVER=' + driver +
                    ';SERVER=' + server +
                    ';PORT=1433;DATABASE=' + database +
                    ';UID=' + userDB +
                    ';PWD=' + pwd) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM tweets WHERE username='" + username + "'")
                    data = cursor.fetchall()
                    for row in data:
                        if row[1] == str(tweetID):
                            return
                    cursor.execute("DELETE FROM tweets WHERE username='" + username + "'")
                    cursor.execute("INSERT INTO tweets VALUES ('" + str(tweetID) + "','" + username + "')")
                    requests.post({webhook-url}, json={
                        "username": "TwitterBot",
                        "icon_url": "https://cdn0.iconfinder.com/data/icons/"
                                    "twitter-ui-flat/48/Twitter_UI-02-512.png",
                        "content": tweet
                    })
    except Exception as e:
        logging.info(str(e))

def main(mytimer: func.TimerRequest) -> None:
    ret_tweet()
