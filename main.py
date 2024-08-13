from flask import Flask, jsonify
from booru import Safebooru
import asyncio

page = "/safebooru"
#client goes her please check documentation of the booru module
client = Safebooru()


app = Flask(__name__)

async def fetch_safebooru_posts():
    posts = await client.get_posts(limit=100)  # Fetch posts asynchronously
    return posts

def create_video_source(post):
    resolution = post.height or 0
    width = post.width or 0

    return {
        "resolution": resolution,
        "url": post.file_url or '',
        "height": resolution,
        "width": width,
        "size": {
            "w": width,
            "h": resolution,
            "size": None
        }
    }

def create_deovr_json(post):
    video_sources = [create_video_source(post)]
    
    deovr_data = {
        "$schema": "http://schema.deovr.com/v1/video.json",
        "title": post.md5 or 'Unknown',
        "id": post.id,
        "thumbnailUrl": post.preview_url or '',
        "encodings": [
            {
                "name": "h264",
                "videoSources": video_sources
            }
        ],
        "videoLength": None,
        "screenType": "sphere",
        "stereoMode": "mono",
        "is3d": False,
        "videoThumbnail": post.preview_url or '',
        "videoPreview": post.preview_url or '',
        "timeStamps": [],
        "skipIntro": 0,
        "corrections": {
            "x": 0,
            "y": 0,
            "br": 0,
            "cont": 0,
            "sat": 0
        }
    }
    
    return deovr_data

@app.route(page, methods=['GET'])
def safebooru_to_json():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    posts = loop.run_until_complete(fetch_safebooru_posts())

    deovr_videos = []
    for post in posts:
        deovr_json = create_deovr_json(post)
        deovr_videos.append(deovr_json)

    deovr_json_structure = {
        "$schema": "http://schema.deovr.com/v1/multivideo.json",
        "scenes": [{
            "name": "Videos",
            "list": deovr_videos
        }]
    }

    return jsonify(deovr_json_structure)

if __name__ == '__main__':
    app.run(debug=False)
