from requests_oauthlib import OAuth1Session
from datetime import datetime
from time import sleep

import time
import os.path
import urllib.request
import json
import env
import sys

user_id = env.USER_ID
CONSUMER_KEY = env.CONSUMER_KEY
CONSUMER_SECRET = env.CONSUMER_SECRET
ACCESS_TOKEN = env.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = env.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

def get_image_url_by_id(id):
    url = "https://api.twitter.com/1.1/statuses/show.json"
    res = twitter.get(url, params={'id': id})
    rimit_tweet = res.headers['X-Rate-Limit-Remaining']
    rimitime_tweet = res.headers['X-Rate-Limit-Reset']
    print("tweet_limit %s" %rimit_tweet)

    if rimit_tweet == "0":
        reset_seconds = float(rimitime_tweet) - time.mktime(datetime.now().timetuple())
        reset_seconds = max(reset_seconds, 0)
        print("getimgs sleep in %s seconds" %reset_seconds)
        time.sleep(reset_seconds + 10)

    if res.status_code == 200:

        if 'media_url_https' in res.text:
            r = json.loads(res.text)
            try:
                medias = r["extended_entities"]["media"]
            except KeyError:
                return False
            return [m["media_url_https"] for m in medias]

    return False

def dl_image_from_url(urls):
    for url in urls:
        name = url.split("/")
        pathname = "/Users/sota/icloud/fav_images/" + name[-1]
        urllib.request.urlretrieve(url + ":large", pathname)

def get_fav_list(maxid):
    url = "https://api.twitter.com/1.1/favorites/list.json"
    params = {'screen_name': user_id, 'count': 200}

    if maxid == None:
        params = {'screen_name': user_id, 'count': 200}
    else:
        params = {'screen_name': user_id, 'count': 200, 'max_id':maxid}
    res = twitter.get(url, params = params)

    rimit_favlist = res.headers['X-Rate-Limit-Remaining']
    rimittime_favlist = res.headers['X-Rate-Limit-Reset']
    print("favlist_limit %s" %rimit_favlist)

    if rimit_favlist == "0":
        reset_seconds = float(rimittime_favlist) - time.mktime(datetime.now().timetuple())
        reset_seconds = max(reset_seconds, 0)
        print("getfavlist sleep in %s seconds " %reset_seconds)
        time.sleep(reset_seconds + 10)

    if res.status_code == 200:
        r = json.loads(res.text) #json dictionary 型
        return [tweets["id"] for tweets in r]

    return False

def get_rt_list():
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {'screen_name': user_id, 'count': 150}
    res = twitter.get(url, params=params)

    if res.status_code == 200:
        r = json.loads(res.text)
        return [tweet["id"] for tweet in r if 'retweeted_status' in tweet]
    return False

def main():
    old_id = None

    while True:
        ids = get_fav_list(old_id)
        old_id = ids[-1]
        #ids = get_rt_list()

        if ids :
            since_id = ids[0]
            for tweet_id in ids:
                media_url = get_image_url_by_id(tweet_id)

                if not media_url:
                    continue
                else:
                    nameimg = media_url[0].split("/")
                    pathname = "/Users/sota/icloud/fav_images/"
                    if nameimg[-1] not in os.listdir(pathname):
                        dl_image_from_url(media_url)
                        print("%s img save" %nameimg[-1])
                    else:
                        print("%s img exist" %nameimg[-1]) #永久に呼び出し続けることになる...?それは困る 一週間前とかapiの限界とか取得可能?

        sleep(10)

if __name__ == "__main__":
    main()
