#!/usr/bin/env python3
"""Create WeChat Official Account draft from HTML content file.
Supports custom cover image upload.

Usage:
  python3 wx_draft.py <title> <content.html> <source_url> [--image cover.jpg]

Reads credentials from ~/.hermes/.env:
  WEIXIN_MP_APPID, WEIXIN_MP_APPSECRET, WEIXIN_MP_THUMB_ID (fallback)
"""
import sys, json, urllib.request, os, argparse

env_path = os.path.expanduser('~/.hermes/.env')
with open(env_path) as f:
    env = {}
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

APPID = env.get('WEIXIN_MP_APPID', '')
SECRET = env.get('WEIXIN_MP_APPSECRET', '')
FALLBACK_THUMB = env.get('WEIXIN_MP_THUMB_ID', '')

parser = argparse.ArgumentParser(description='Create WeChat draft')
parser.add_argument('title', help='Article title')
parser.add_argument('content_file', help='Path to HTML content file')
parser.add_argument('source_url', help='Source URL for 阅读原文')
parser.add_argument('--image', help='Path to cover image (jpg/png)', default=None)
args = parser.parse_args()

with open(args.content_file) as f:
    content_html = f.read().strip()

# Get access token
token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}'
token = json.loads(urllib.request.urlopen(token_url).read())['access_token']

# Determine thumb_media_id
thumb_id = FALLBACK_THUMB
if args.image and os.path.exists(args.image):
    print(f"Uploading cover: {args.image}", file=sys.stderr)
    with open(args.image, 'rb') as f:
        img_data = f.read()

    boundary = '----WxUploadBoundary'
    body = b''
    body += f'--{boundary}\r\n'.encode()
    ext = os.path.splitext(args.image)[1].lower()
    mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png'
    body += f'Content-Disposition: form-data; name="media"; filename="cover{ext}"\r\n'.encode()
    body += f'Content-Type: {mime}\r\n\r\n'.encode()
    body += img_data
    body += f'\r\n--{boundary}--\r\n'.encode()

    upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    req = urllib.request.Request(upload_url, data=body)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    resp = json.loads(urllib.request.urlopen(req).read())

    if 'media_id' in resp:
        thumb_id = resp['media_id']
        print(f"Cover uploaded: {thumb_id[:20]}...", file=sys.stderr)
    else:
        print(f"Cover upload failed: {resp}, using fallback", file=sys.stderr)

# Create draft
draft = {
    "articles": [{
        "title": args.title,
        "author": "Hermes Agent",
        "digest": "AI芯片 / Agentic EDA / Agentic CAE/CAD 每日精选",
        "content": content_html,
        "content_source_url": args.source_url,
        "thumb_media_id": thumb_id,
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
