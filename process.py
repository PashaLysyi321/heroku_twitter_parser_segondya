import flask
from flask import redirect, url_for, request
from telethon import TelegramClient, functions, types
from asyncio import run
import asyncio
from telethon.tl.functions.contacts import ResolveUsernameRequest
from datetime import date, timedelta, datetime
import pandas as pd
import re
import requests
import json
import os
import random
import time

app = flask.Flask(__name__)

headers = {
    'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAJ2dbAEAAAAAL75%2B%2F2Ap6j94pj3dcRSUcPz511U%3DrAovY60ru7FSAUEZxJTa6ORAWeA7M1ZchoMXlv2BWI6FzJHfWS',
}

@app.route('/')
def start():
    return str(os.path.abspath(os.curdir))
    #return('write /download to url to load excel')

@app.route('/download', methods=['GET', 'POST'])
def download():
    ran = time.time()
    username = 'segodnya_online'
    url = 'https://api.twitter.com/2/users/by/username/' + username

    response_user_id = requests.get(url, headers=headers)
    max_results = 100
    response = requests.get('https://api.twitter.com/2/users/497830254/tweets?expansions=attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type&poll.fields=duration_minutes,end_datetime,id,options,voting_status&media.fields=duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics&max_results='+str(max_results), headers=headers)
    response_json = json.loads(response.text)
    data = response_json['data']
    for i in range(len(data)):
        for key, value in data[i]['public_metrics'].items():
            data[i][key] = value
            data[i]['entities_list'] = list(data[i]['entities'].keys())
    df = pd.DataFrame(data)
    df.drop(['author_id','entities','public_metrics','reply_settings'], axis=1, inplace=True)
    df = df[['id','created_at','text','lang','entities_list','like_count','retweet_count','reply_count','quote_count','source','possibly_sensitive']]
    df.to_excel("segodnya_twitter_"+str(ran)+".xlsx")
    return flask.send_file("segodnya_tg_"+str(ran)+".xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run()