import flask
from flask import redirect, url_for, request
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
    username = 'u24_news'
    url = 'https://api.twitter.com/2/users/by/username/' + username
    response_user_id = requests.get(url, headers=headers)
    response_user_id_json = json.loads(response_user_id.text)
    user_id = response_user_id_json['data']['id']
    
    year = datetime.now().year # 2022
    month = datetime.now().month # 4
    day = datetime.now().day - 1 # 13
    max_results = 50

    date_to_parse = datetime(year, month, day).strftime("%Y-%m-%dT00:00:00Z")
    end_time = datetime(year, month, day+1).strftime("%Y-%m-%dT00:00:00Z")
    parse_columns = ['id','created_at','text','lang','entities_list','like_count','retweet_count','reply_count','quote_count','possibly_sensitive']
    upd = pd.DataFrame(columns=parse_columns)

    while True:  
        response = requests.get('https://api.twitter.com/2/users/' + user_id + '/tweets?expansions=attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type&poll.fields=duration_minutes,end_datetime,id,options,voting_status&media.fields=duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics&max_results='+str(max_results)+'&end_time='+end_time, headers=headers)
        response_json = json.loads(response.text)
        # print(response_json)

        data = response_json['data']
        for i in range(len(data)):
            for key, value in data[i]['public_metrics'].items():
                data[i][key] = value
                try: 
                    data[i]['entities_list'] = list(data[i]['entities'].keys())
                except KeyError:
                    data[i]['entities_list'] = []

        df = pd.DataFrame(data)
        df.drop(['author_id','entities','public_metrics','reply_settings','source'], axis=1, inplace=True)
        df = df[parse_columns]
        # df
        
        end_time = min(df['created_at'])
        df = df[df['created_at'] >= date_to_parse]
        upd = upd.append(df, ignore_index=True)
        if end_time < date_to_parse:
            break
        time.sleep(0.1)
    
    dt_string = datetime(year, month, day).strftime("%Y-%m-%d")
    upd.to_excel(username + ' upd ' + dt_string + ".xlsx")  
    return flask.send_file(username + ' upd ' + dt_string + ".xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run()