import requests
from urllib.parse import urlencode
import sqlite3

con = sqlite3.connect("influencer.db")
cur = con.cursor()

keys = []
columns = []

base_url = "https://graph.facebook.com/v17.0/17841410319691752"

# Access Token
access_token = "EAAS0L6gve6kBO7XVEyQ4Ww6OOZCdrY18YtkUVJyOBPxOGbgsdh5JSghfKZC5opAFotPqz9fto6BLxxYp6d9ziEj9TUvt3t3Ux2nBbN3wIsZAnwApFMkGx6cfbtJxXZBNM8kElGGN7u9zT2vQkhQMGZCqVCRbhmbS0ZAqCcbt8TrHIcLA9amebeXMZBqleFVPFIZD"

# Parameters for profile information
profile_params = {
    "fields": "business_discovery.username(b.saem){biography,name,username,follows_count,website,ig_id,followers_count,media_count}",
    "access_token": access_token,
    "limit": 50
}

# Parameters for feed data
feed_params = {
    "fields": "business_discovery.username(b.saem){media{id,caption,comments_count,children{media_type},like_count,media_product_type,timestamp,username}}",
    "access_token": access_token
}

# Fetching profile information
profile_response = requests.get(base_url, params=profile_params)
if profile_response.status_code == 200:
    profile_data = profile_response.json()
    profile_info = profile_data['business_discovery']

    print("사용자 정보:")
    print(f"ID: {profile_info['ig_id']}")
    print(f"사용자명: {profile_info['username']}")
    print(f"미디어 수: {profile_info['media_count']}")
    print(f"팔로우 수: {profile_info['follows_count']}")
    print(f"팔로워 수: {profile_info['followers_count']}")
    keys = [(profile_info['ig_id']),(profile_info['username']),(profile_info['followers_count']),(profile_info['follows_count']),(profile_info['media_count'])]
    cur.execute("INSERT INTO influencers VALUES (?,?,?,?,?)", (keys))
    con.commit()
    print("-------------------------------------------------------------------------")
else:
    print(f"Error: {profile_response.status_code}, {profile_response.text}")
# Fetching feed data with Pagination
while True:
    feed_response = requests.get(base_url, params=feed_params)
    if feed_response.status_code == 200:
        data = feed_response.json()
        media_list = data['business_discovery']['media']['data']
        
        print("게시물 정보:")
        for media_data in media_list:
            # 미디어 정보 출력 (기존 코드와 동일)
            print("게시물 ID:", media_data['id'])
            #print("캡션:", media_data['caption'])
            print("댓글 수:", media_data['comments_count'])
            like_count = media_data.get('like_count', "비공개")
            print("좋아요 수:", like_count)
            print("미디어 타입:", media_data['media_product_type'])
            print("타임스탬프:", media_data['timestamp'])
            print("사용자명:", media_data['username'])
            columns = [(media_data['id']),(media_data['comments_count']),(like_count),(media_data['media_product_type']),(media_data['timestamp']),(media_data['username'])]
            cur.execute("INSERT INTO influencers_post VALUES (?,?,?,?,?,?)", (columns))
            con.commit()
            print("-------------------------------------------------------------------------")
        
        # Pagination 처리
        if 'paging' in data and 'next' in data['paging']:
            next_page_url = data['paging']['next']
            feed_params['after'] = next_page_url.split('after=')[1]
        else:
            break  # 더 이상 다음 페이지가 없을 경우 종료
    else:
        print(f"Error: {feed_response.status_code}, {feed_response.text}")
        break