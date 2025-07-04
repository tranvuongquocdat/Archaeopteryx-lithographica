from googleapiclient.discovery import build
import pandas as pd
import re

def get_channel_info_from_url(url, api_key):
    """
    Lấy thông tin kênh trực tiếp từ URL YouTube
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Direct channel ID (youtube.com/channel/UCxxxxxx)
    channel_id_match = re.search(r'youtube\.com/channel/([A-Za-z0-9_-]+)', url)
    if channel_id_match:
        channel_id = channel_id_match.group(1)
        request = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id,
            fields='items(id,snippet/title,snippet/publishedAt,statistics/subscriberCount,statistics/videoCount,statistics/viewCount)'
        )
        response = request.execute()
        return response.get('items', [])
    
    # Username format (youtube.com/@username)
    handle_match = re.search(r'youtube\.com/@([A-Za-z0-9._-]+)', url)
    if handle_match:
        handle = handle_match.group(1)
        request = youtube.channels().list(
            part='snippet,statistics',
            forHandle=handle,  # Không cần @ prefix
            fields='items(id,snippet/title,snippet/publishedAt,statistics/subscriberCount,statistics/videoCount,statistics/viewCount)'
        )
        response = request.execute()
        return response.get('items', [])
    
    # Legacy username format (youtube.com/user/username hoặc youtube.com/c/customname)
    username_match = re.search(r'youtube\.com/(?:user/|c/)([A-Za-z0-9_-]+)', url)
    if username_match:
        username = username_match.group(1)
        request = youtube.channels().list(
            part='snippet,statistics',
            forUsername=username,
            fields='items(id,snippet/title,snippet/publishedAt,statistics/subscriberCount,statistics/videoCount,statistics/viewCount)'
        )
        response = request.execute()
        return response.get('items', [])
    
    return []

def extract_channel_id_from_url(url):
    """
    Trích xuất channel_id từ URL nếu có thể, trả về None nếu không tìm được.
    """
    # Direct channel ID (youtube.com/channel/UCxxxxxx)
    channel_id_match = re.search(r'youtube\.com/channel/([A-Za-z0-9_-]+)', url)
    if channel_id_match:
        return channel_id_match.group(1)
    return None

def get_channels_info_by_ids(channel_ids, api_key):
    """
    Lấy thông tin nhiều kênh bằng channel_id (tối đa 50/lần)
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(
        part='snippet,statistics',
        id=','.join(channel_ids),
        fields='items(id,snippet/title,snippet/publishedAt,statistics/subscriberCount,statistics/videoCount,statistics/viewCount)'
    )
    response = request.execute()
    return response.get('items', [])

def get_multiple_channels_from_urls_batch(channel_urls, api_key):
    """
    Lấy thông tin nhiều kênh từ danh sách URLs, tối ưu quota bằng batch channel_id
    """
    all_data = []
    id_url_map = {}
    ids = []
    fallback_urls = []

    # Tách channel_id nếu có thể
    for url in channel_urls:
        cid = extract_channel_id_from_url(url)
        if cid:
            ids.append(cid)
            id_url_map[cid] = url
        else:
            fallback_urls.append(url)

    # Chia batch 50 id/lần
    for i in range(0, len(ids), 50):
        batch_ids = ids[i:i+50]
        try:
            items = get_channels_info_by_ids(batch_ids, api_key)
            for item in items:
                all_data.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'subscriberCount': item['statistics'].get('subscriberCount', 0),
                    'videoCount': item['statistics'].get('videoCount', 0),
                    'viewCount': item['statistics'].get('viewCount', 0),
                    'source_url': id_url_map[item['id']]
                })
        except Exception as e:
            print(f"Lỗi khi lấy batch ids {batch_ids}: {e}")

    # Với các url không có channel_id, fallback sang hàm cũ (tốn quota hơn)
    for url in fallback_urls:
        print(f"Channel url không có channel_id: {url}")
        try:
            channel_items = get_channel_info_from_url(url, api_key)
            for item in channel_items:
                all_data.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'subscriberCount': item['statistics'].get('subscriberCount', 0),
                    'videoCount': item['statistics'].get('videoCount', 0),
                    'viewCount': item['statistics'].get('viewCount', 0),
                    'source_url': url
                })
        except Exception as e:
            print(f"Lỗi khi lấy thông tin từ {url}: {e}")

    return pd.DataFrame(all_data)

# API Key và danh sách URLs
API_KEY = 'AIzaSyBkbdni528jYjh4Igj5GAvHDV6q4hrR6Kk'
channel_urls = [
    'https://www.youtube.com/@elsarca', 
    'https://www.youtube.com/@ups1dezz', 
    'https://www.youtube.com/@metiktokn',
    'https://www.youtube.com/@tra.dang.904',
    'https://www.youtube.com/@Rocketmanba04',
    'https://www.youtube.com/@lucas-g7t6w',
    'https://www.youtube.com/@ThanhBin',
    'https://www.youtube.com/@MarcelMakesStuff',
    'https://www.youtube.com/@merielx',
    'https://www.youtube.com/@katebrush',
    'https://www.youtube.com/@tieumanthau2708',
    'https://www.youtube.com/channel/UClZAOlfhJQJRym39WoAPxdw',
    'https://www.youtube.com/@Disabledreactionvideo',
    'https://www.youtube.com/@JustaYoutube19',
    'https://www.youtube.com/@vityaperchik',
    'https://www.youtube.com/@duongthoon',
    'https://www.youtube.com/@TheTrenchFamily',
    'https://www.youtube.com/@hoanghonofficial',
    'https://www.youtube.com/@Arbaxyz',
    'https://www.youtube.com/@youssefelbaroudi9766'
]

# Lấy thông tin kênh trực tiếp từ URLs
df = get_multiple_channels_from_urls_batch(channel_urls, API_KEY)
print(df)

# In ra số lượng kênh tìm được
print(f"\nĐã tìm được thông tin của {len(df)} kênh")