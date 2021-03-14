import requests
from flask import Flask, render_template, request
import logging

subreddits = ['memes', 'dankmemes', 'funny', 'prequelmemes']
limit = 5
timeframe = 'week'  # hour, day, week, month, year, all
listing = 'top'  # controversial, best, hot, new, random, rising, top

app = Flask(__name__)

def get_reddit(subreddit, listing, limit, timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
        request = requests.get(base_url, headers={'User-agent': 'yourbot'})
    except:
        print('An Error Occured')
    return request.json()


def get_post_titles(r):
    '''
    Get a List of post titles
    '''
    posts = []
    for post in r['data']['children']:
        x = post['data']['title']
        posts.append(x)
    return posts

def get_results(r):
    '''
    Create a DataFrame Showing Title, URL, Score and Number of Comments.
    '''
    postList=[]
    for post in r['data']['children']:

        post= {'title': post['data']['title'], 'url': post['data']['url'], 'score': post['data']['score'],
                                         'comments': post['data']['num_comments'], 'is_video': post['data']['is_video']}
        if '.gifv' in post['url']:
            post['url'] = post['url'][:-1]
        if '.gif' in post['url'] or '.png' in post['url'] or '.jpg' in post['url'] or '.jpeg' in post['url']:
            postList.append(post)
    return postList

@app.route("/")
def home():
    app.logger.info("InHomePage")
    reddit_dict = {}
    for subreddit in subreddits:
        name = f'r/{subreddit}'
        r = get_reddit(subreddit, listing, limit, timeframe)
        df = get_results(r)
        for post in df:
            if post["is_video"]:
                df.remove(post)

        reddit_dict[name] = df


    for subreddit in reddit_dict:
        print(subreddit)
        print(reddit_dict[subreddit])
        print()
    return render_template('index.html', page_title = "Popular Meme Subreddits", data=reddit_dict)

@app.route("/redresponse")
def search_handler():
    reddit_dict = {}
    name = request.args.get('name')
    if name:
        r = get_reddit(name, listing, limit, timeframe)
        df = get_results(r)
        reddit_dict[name] = df
        return render_template('index.html', page_title =f"Results for r/{name}", data = reddit_dict)
    else:
        return render_template('index.html', page_title = "Sorry couldn't find that Subreddit")



if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)