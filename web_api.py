from mastodon import Mastodon
import re
from textblob import TextBlob
from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

client_id = os.environ.get('MASTODON_CLIENT_ID')
client_secret = os.environ.get('MASTODON_CLIENT_SECRET')
access_token = os.environ.get('MASTODON_ACCESS_TOKEN')
api_base_url = os.environ.get('MASTODON_API_BASE_URL')

# Create a Mastodon client instance using the retrieved credentials
mastodon = Mastodon(
    client_id=client_id,
    client_secret=client_secret,
    access_token=access_token,
    api_base_url=api_base_url
)

# Define a function to search for posts with a specific hashtag
def search_tag(tag):
    mylist = []

    # Get the timeline for a specific hashtag
    hashtag_timeline = mastodon.timeline_hashtag(tag)
    
    # Define a regular expression pattern to remove HTML tags from post content
    pattern = re.compile('<.*?>')

    # Iterate through the posts in the hashtag timeline
    for post in hashtag_timeline:
        # Remove HTML tags from the post content
        result = re.sub(pattern, '', post['content'])
        # Append the cleaned content to the list
        mylist.append(result)

    return mylist

# Define a function to calculate the average polarity score of posts
def calculate_average_polarity(posts):
    total_polarity = 0
    num_posts = len(posts)

    for post in posts:
        analysis = TextBlob(post)
        total_polarity += analysis.sentiment.polarity

    if num_posts > 0:
        average_polarity = total_polarity / num_posts
        return average_polarity
    else:
        return None

@app.route('/average_polarity', methods=['GET'])
def get_average_polarity():
    tag = request.args.get('tag', default=None)

    if tag is not None:
        listposts = search_tag(tag)
        average_polarity = calculate_average_polarity(listposts)
        if average_polarity is not None:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = {
                'tag': tag,
                'average_polarity': average_polarity,
                'timestamp': current_time
            }
            return jsonify(result)
        else:
            return jsonify({'tag': tag, 'message': 'No posts found with the specified tag.'}), 404
    else:
        return jsonify({'message': 'Please provide a "tag" parameter in the URL.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
