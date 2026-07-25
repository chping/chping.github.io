#!/usr/bin/env python3
"""Create WeChat Official Account draft from HTML content file.
Reads credentials from ~/.hermes/.env
Usage: python3 wx_draft.py <title> <content_file> <source_url>
"""
import sys, json, urllib.request, os

env_path = os.path.expanduser('~/.hermes/.env')
with open(env_path) as f:
    env = {}
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

APPID = env.get('WEIXIN_MP_APPID', '')
SECRET = env.get('WEIXIN_MP_APPSECRET', '')
THUMB_ID = env.get('WEIXIN_MP_THUMB_ID', '')

if len(sys.argv) < 4:
    print("Usage: wx_draft.py <title> <content.html> <source_url>")
    sys.exit(1)

title, content_file, source_url = sys.argv[1], sys.argv[2], sys.argv[3]

with open(content_file) as f:
    content_html = f.read().strip()

# Get token
token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}'
token = json.loads(urllib.request.urlopen(token_url).read())['access_token']

# Create draft
draft = {
    "articles": [{
        "title": title,
        "author": "Hermes Agent",
        "digest": "AI芯片 / Agentic EDA / Agentic CAE/CAD 每日精选",
        "content": content_html,
        "content_source_url": source_url,
        "thumb_media_id": THUMB_ID,
        "need_open_comment": 0,
        "show_cover_pic": 1,
    }]
}

draft_url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
req = urllib.request.Request(draft_url,
                              data=json.dumps(draft, ensure_ascii=False).encode(),
                              headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req).read())

if 'media_id' in resp:
    print(f"DRAFT_OK:{resp['media_id']}")
else:
    print(f"DRAFT_FAIL:{json.dumps(resp, ensure_ascii=False)}")
