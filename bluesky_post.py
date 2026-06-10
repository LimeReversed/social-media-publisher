from atproto import Client, models
# from atproto import AppBskyEmbedExternal
import json

import requests

with open('bluesky_client_secret.json') as f:
    secrets = json.load(f)

client = Client()
client.login(secrets['user_name'], secrets['api_key'])

def post_bluesky(text: str):
    post = client.send_post(text=text)
    print('Posted to Bluesky!')
    return post

def post_bluesky_with_youtube_video(text: str, video_id: str, title: str = "", description: str = ""):
    if video_id:
        thumb_bytes = requests.get(f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg').content
        thumb_blob = client.upload_blob(thumb_bytes).blob

        embed = models.AppBskyEmbedExternal.External(
            uri=f'https://youtube.com/shorts/{video_id}',
            title=title,  # The title shown in the embed
            description=description,  # The description shown in the embed
            thumb=thumb_blob
        )
        embed_obj = models.AppBskyEmbedExternal.Main(external=embed)
    else:
        embed_obj = None
    
    post = client.send_post(text=text, embed=embed_obj)
    print('Posted to Bluesky!')
    return post
