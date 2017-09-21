import praw
import tweepy
import random
import time
import cfg

reddit = praw.Reddit(client_id=cfg.REDDIT_ID,
                     client_secret=cfg.REDDIT_SECRET,
                     user_agent='A script to scrape Arena FPS (video game genre) subreddits, and collect the most popular comments, and then posting them to twitter.')

arenafps = reddit.subreddit("arenafps")
quakechumps = reddit.subreddit("QuakeChampions")
reflex = reddit.subreddit("Reflex")
quakelive = reddit.subreddit("Quakelive")
toxikk = reddit.subreddit("TOXIKK")


def getHotComments(subreddit):
    """Get the latest 50 HOT threads from a given subreddit.  Filter them to prep for Twitter"""
    sub_submissions = []
    hot_list = []
    for submission in subreddit.hot(limit=50):
        sub_submissions.append(submission)
    for submission in sub_submissions:
        if "AMA" in submission.title:
            sub_submissions.remove(submission)
    for any in sub_submissions:
        for top_comment in any.comments:
            if len(any.title) < 60 and top_comment.score >= 5 and len(top_comment.body) < 115 and "[deleted]" not in top_comment.body:
                hot_list.append([top_comment.subreddit_name_prefixed, any.title,
                                 top_comment.author, top_comment.score, top_comment.body])

    return hot_list

def getControversialComments(subreddit):
    """Get the latest 50 CONTROVERSIAL threads from a given subreddit.  Filter them to prep for Twitter"""
    sub_submissions = []
    controversial_list = []
    for submission in subreddit.controversial(limit=50):
        sub_submissions.append(submission)
    for submission in sub_submissions:
        if "AMA" in submission.title:
            sub_submissions.remove(submission)
    for any in sub_submissions:
        for top_comment in any.comments:
            if len(any.title) < 60 and top_comment.score >= 5 and len(top_comment.body) < 115 and "[deleted]" not in top_comment.body:
                controversial_list.append([top_comment.subreddit_name_prefixed, any.title,
                                           top_comment.author, top_comment.score, top_comment.body])

    return controversial_list

def getPreviousTweets():
    """Uses tweepy to gather last 500 tweets.  Returns a string of past tweets"""
    auth = tweepy.OAuthHandler(cfg.TWITTER_CONSUMER_KEY, cfg.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(cfg.TWITTER_ACCESS_KEY, cfg.TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    last_statuses = api.user_timeline(count=500)
    previous_tweets_string = ""
    for any in last_statuses:
        previous_tweets_string += any.text
    return previous_tweets_string



def checkIfAlreadyTweeted(comment_list, previous_tweets):
    """Input: Comment List - A list of lists, of top comments from reddit
              Previous Tweets - Giant string containing last 250 tweets
        Output: Removes all items from Comment List that are also in Previous Tweets"""
    for comments in comment_list:
        if comments[4] in previous_tweets:
            comment_list.remove(comments)
        else:
            pass


def getCommentsforTweet(previous_tweets):
    """Returns the master list of all viable tweets from different subreddits.
    Previous tweets are filtered out """

    afps_controversial = getControversialComments(arenafps)
    afps_hot = getHotComments(arenafps)
    quakechumps_controversial = getControversialComments(quakechumps)
    quakechumps_hot = getHotComments(quakechumps)
    reflex_controversial = getControversialComments(reflex)
    reflex_hot = getHotComments(reflex)
    quakelive_controversial = getControversialComments(quakelive)
    quakelive_hot = getHotComments(quakelive)
    toxikk_controversial = getControversialComments(toxikk)
    toxikk_hot = getHotComments(toxikk)

    tweeting_master_list = []

    for all in afps_controversial:
        tweeting_master_list.append(all)
    for all in afps_hot:
        tweeting_master_list.append(all)
    for all in quakechumps_controversial:
        tweeting_master_list.append(all)
    for all in quakechumps_hot:
        tweeting_master_list.append(all)
    for all in reflex_controversial:
        tweeting_master_list.append(all)
    for all in reflex_hot:
        tweeting_master_list.append(all)
    for all in quakelive_controversial:
        tweeting_master_list.append(all)
    for all in quakelive_hot:
        tweeting_master_list.append(all)
    for all in toxikk_controversial:
        tweeting_master_list.append(all)
    for all in toxikk_hot:
        tweeting_master_list.append(all)

    checkIfAlreadyTweeted(tweeting_master_list, previous_tweets)

    random.shuffle(tweeting_master_list)

    return tweeting_master_list

def getRandomTweet():
    """Chooses a random tweet from the master tweet list"""
    previous_tweets = getPreviousTweets()
    tweet_list = getCommentsforTweet(previous_tweets)
    tweet = random.choice(tweet_list)
    return tweet


def tweetToTwitter():
    """The main function: tweets to twitter 3 times at 2 hour intervals.  Then sleeps for 14 hours"""
    auth = tweepy.OAuthHandler(cfg.TWITTER_CONSUMER_KEY, cfg.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(cfg.TWITTER_ACCESS_KEY, cfg.TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    counter = 0

    while True:

        if counter == 3:
            print("=====================================")
            print("SLEEPING 14 HOURS")
            print("=====================================")
            time.sleep(50400)
            counter = 0
        else:
            try:
                the_tweet = getRandomTweet()
                api.update_status(the_tweet[0] + "\n" + the_tweet[1] + "\n\n" + "\"" + the_tweet[4] + "\"" + "\n" + " -" + str(the_tweet[2]))
                print("Successfully tweeted!\n-----------------")
                print(the_tweet[0] + "\n" + the_tweet[1] + "\n\n" + "\"" + the_tweet[4] + "\"" + "\n" + " -" + str(the_tweet[2]))
                print("=====================================")
                counter += 1
                time.sleep(7200)
            except tweepy.error.TweepError:
                print("Failed to tweet! Tweet too long.\n-----------------")
                print(the_tweet[0] + "\n" + the_tweet[1] + "\n\n" + "\"" + the_tweet[4] + "\"" + "\n" + " -" + str(the_tweet[2]))
                print("=====================================")
                pass



tweetToTwitter()
