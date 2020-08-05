from requests_oauthlib import OAuth1Session
from datetime import datetime
from time import sleep
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
        #print(pathname)
        urllib.request.urlretrieve(url + ":large", pathname)

def get_fav_list():
    url = "https://api.twitter.com/1.1/favorites/list.json"
    params = {'screen_name': user_id, 'count': 100}
    res = twitter.get(url, params = params)
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
    #print("test")

    old_ids = []
    while True:
        ids = get_fav_list()
        #ids = get_rt_list()
        if ids :
            since_id = ids[0]
            for tweet_id in ids:
                if tweet_id in old_ids:
                    continue
                media_url = get_image_url_by_id(tweet_id)
                if not media_url:
                    continue
                else:
                    nameimg = media_url[0].split("/")
                    pathname = "/Users/sota/icloud/fav_images/"
                    # print(os.listdir(pathname))
                    # print(os.listdir(pathname)[0])
                    if nameimg[-1] in os.listdir(pathname):
                        print("exist")
                        sys.exit(0)

                    dl_image_from_url(media_url)
                    sleep(100)
        old_ids = ids

        sleep(300)


if __name__ == "__main__":
    main()
