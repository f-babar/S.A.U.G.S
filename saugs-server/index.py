from flask import Flask, jsonify
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
import re
import requests, json
import pymongo
from pymongo import MongoClient
import time
import constants

app = Flask(__name__)

#--------------------------------------------------
#                   Twitter Connection
#--------------------------------------------------
consumer_key = constants.TWITTER_CONSUMER_KEY
consumer_secret = constants.TWITTER_CONSUMER_SECRET
access_token = constants.TWITTER_ACCESS_TOKEN
access_token_secret = constants.TWITTER_TOKEN_SECRET

auth = OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret) 
api = tweepy.API(auth) 

#--------------------------------------------------
#                   MongoDB Connection
#--------------------------------------------------
client = MongoClient(constants.MONGO_URL)
db = client.saugs
analysis_collection = db.analysis

#--------------------------------------------------
# Get Tweets from Twitter and get locations from 
# each tweet. And then find the sentiment polarity 
# of each tweet.
#--------------------------------------------------

@app.route('/twitter/<query>')
def get_tweets(query):
    count = 100

    users_with_geodata = {
        "data": []
    }
    all_users = []
    total_tweets = 0
    geo_tweets  = 0

    countries = get_countries_list()
    fetched_tweets = api.search(q = query, count = count) 
    for tweet in fetched_tweets:
        tweet_text = tweet.text
        sentiment_analysis = get_tweet_sentiment(tweet_text)
        if tweet.user.id:
            total_tweets += 1 
            user_id = tweet.user.id
            if user_id not in all_users:
                all_users.append(user_id)
                user_data = {
                    "user_id" : tweet.user.id,
                    "result" : {
                        "name" : tweet.user.name,
                        "id": tweet.user.id,
                        "screen_name": tweet.user.screen_name,
                        "tweets" : 1,
                        "location": tweet.user.location,
                    }
                }
                if tweet.coordinates:
                    user_data["result"]["primary_geo"] = 'US' # str(tweet.coordinates[tweet.coordinates.keys()[1]][1]) + ", " + str(tweet.coordinates[tweet.coordinates.keys()[1]][0])
                    user_data["result"]["geo_type"] = "Tweet coordinates"
                elif tweet.place:
                    user_data["result"]["primary_geo"] = tweet.place.full_name + ", " + tweet.place.country
                    user_data["result"]["geo_type"] = "Tweet place"
                else:
                    user_data["result"]["primary_geo"] = tweet.user.location
                    user_data["result"]["geo_type"] = "User location"
                
                if user_data["result"]["primary_geo"]: 
                    user_data["result"]["analysis_result"] = sentiment_analysis
                    user_data["result"]["country"] = get_country(user_data["result"]["primary_geo"])
                    if user_data["result"]["country"] is not None:
                        if user_data["result"]["country"] in countries:
                            countries[user_data["result"]["country"]]["total_tweets"] =  countries[user_data["result"]["country"]]["total_tweets"] + 1
                            if sentiment_analysis.sentiment.polarity > 0:
                                countries[user_data["result"]["country"]]["positive"] =  countries[user_data["result"]["country"]]["positive"] + 1
                            elif sentiment_analysis.sentiment.polarity < 0:
                                countries[user_data["result"]["country"]]["negative"] =  countries[user_data["result"]["country"]]["negative"] + 1
                            else:
                                countries[user_data["result"]["country"]]["neutral"] =  countries[user_data["result"]["country"]]["neutral"] + 1
                            
                            total_polarity = countries[user_data["result"]["country"]]["total_polarity"]
                            total_polarity = total_polarity + sentiment_analysis.sentiment.polarity
                            mean = total_polarity / countries[user_data["result"]["country"]]["total_tweets"]
                            countries[user_data["result"]["country"]]["total_polarity"] =  total_polarity
                            countries[user_data["result"]["country"]]["total"] =  mean * 100
                    users_with_geodata['data'].append(user_data)
                    geo_tweets += 1

                elif user_id in all_users:
                    for user in users_with_geodata["data"]:
                        if user_id == user["user_id"]:
                             user["result"]["tweets"] += 1
            for user in users_with_geodata["data"]:
                geo_tweets = geo_tweets + user["result"]["tweets"]
            
    # print("The file included " + str(len(all_users)) + " unique users who tweeted with or without geo data")
    # print("The file included " + str(len(users_with_geodata['data'])) + " unique users who tweeted with geo data, including 'location'")
    # print("The users with geo data tweeted " + str(geo_tweets) + " out of the total " + str(total_tweets) + " of tweets.")

    timestamp = time.ctime()
    splitted_timestamp = timestamp.split(' ')
    timestamp = splitted_timestamp[1] + " " + splitted_timestamp[2] + ", " + splitted_timestamp[4] + " " + splitted_timestamp[3]
    analysis_data = {
        'topic_name' : query,
        'timestamp' : timestamp,
        'analysis' : countries
    }
    analysis_collection.insert_one(analysis_data)

    previous_result = []
    i = 0
    for x in analysis_collection.find({ "topic_name" : query}).sort('_id', -1).limit(5):
        res = {}
        res['topic_name'] = x['topic_name']
        res['timestamp'] = x['timestamp']
        res['analysis'] = x['analysis']
        
        previous_result.insert(i, res)
        i = i+1
    
    return jsonify({'success' : 1, 'countries' : countries, 'previous_result' : previous_result }), {'Access-Control-Allow-Origin': '*'}

def get_tweet_sentiment(tweet): 
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet))
    return analysis 

def clean_tweet(tweet): 
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

def get_country(location):
    countries_collection = db.countries
    splitted_data = location.split(',')
    country = ''
    if len(splitted_data) > 0:
        city = splitted_data[0]
        splitted_cities = city.split(' ')
        for city in splitted_cities:
            for x in countries_collection.find({ "name" : {"$regex": city, '$options': 'i'} } ):
                country = x["country"]
                break
        if country == "":
            for city in splitted_cities:
                for x in countries_collection.find({ "subcountry" : {"$regex": city, '$options': 'i'} } ):
                    country = x["country"]
                    break
    else:
        for x in countries_collection.find({ "name" : {"$regex": location, '$options': 'i'} } ):
            country = x["country"]
    return country

def get_countries_list():

    with open('data/countries_list.json', errors='ignore') as json_file:
        countries_data = json.load(json_file)
        print('aaa')
    return countries_data

#--------------------------------------------------
# Get Top Trends from Twitter
#--------------------------------------------------

@app.route('/trends')
def get_trends():
    trends = api.trends_place(id = 1)
    return jsonify({'trends' : trends}), {'Access-Control-Allow-Origin': '*'}

if __name__ == '__main__':
    app.run()
