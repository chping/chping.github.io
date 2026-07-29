#!/usr/bin/env python3
"""Create WeChat Official Account draft from HTML content file.
Supports custom cover image upload.

Usage:
  python3 wx_draft.py <title> <content.html> <source_url> [--image cover.jpg]

Reads credentials from ~/.hermes/.env:
  WEIXIN_MP_APPID, WEIXIN_MP_APPSECRET, WEIXIN_MP_THUMB_ID (fallback)
"""
import sys, json, urllib.request, os, argparse

# --- WeChat API error code mapping ---
WX_ERROR_MAP = {
    40001: "invalid credential — access_token 无效或类型错误",
    40013: "invalid appid — APPID 不正确",
    40125: "invalid appsecret — APPSECRET 不正确",
    40164: "IP not in whitelist — 当前出口 IP 未加入公众号后台白名单",
    41001: "access_token missing — token 参数缺失",
    42001: "access_token expired — token 已过期，需重新获取",
    42002: "access_token refresh failed — token 刷新失败",
    40007: "invalid media_id",
}

def wechat_api(url, data=None, headers=None, timeout=30):
    """Call WeChat API with proper error handling."""
    try:
        if data is None:
            resp = urllib.request.urlopen(url, timeout=timeout)
        else:
            req = urllib.request.Request(url, data=data)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            resp = urllib.request.urlopen(req, timeout=timeout)
        body = resp.read()
        return json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            print(f"HTTP {e.code}: {body.decode('utf-8', errors='replace')[:500]}", file=sys.stderr)
            sys.exit(2)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"JSON parse error from WeChat API: {e}", file=sys.stderr)
        sys.exit(2)


def format_wx_error(resp, context=""):
    """Format a WeChat API error response into a human-readable message."""
    errcode = resp.get('errcode', -1)
    errmsg = resp.get('errmsg', 'unknown')
    friendly = WX_ERROR_MAP.get(errcode, f"unknown error ({errcode})")
    prefix = f"{context}: " if context else ""
    return f"{prefix}errcode={errcode} — {friendly}\n  raw: {errmsg}"


# --- Load credentials ---
env_path = os.path.expanduser('~/.hermes/.env')
if not os.path.exists(env_path):
    print(f"ERROR: .env file not found at {env_path}", file=sys.stderr)
    sys.exit(1)

with open(env_path) as f:
    env = {}
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

APPID = env.get('WEIXIN_MP_APPID', '')
SECRET = env.get('WEIXIN_MP_APPSECRET', '')
FALLBACK_THUMB = env.get('WEIXIN_MP_THUMB_ID', '')

if not APPID or not SECRET:
    print("ERROR: WEIXIN_MP_APPID or WEIXIN_MP_APPSECRET not set in ~/.hermes/.env", file=sys.stderr)
    sys.exit(1)

# --- Parse args ---
parser = argparse.ArgumentParser(description='Create WeChat draft')
parser.add_argument('title', help='Article title')
parser.add_argument('content_file', help='Path to HTML content file')
parser.add_argument('source_url', help='Source URL for 阅读原文')
parser.add_argument('--image', help='Path to cover image (jpg/png)', default=None)
args = parser.parse_args()

# --- Read content file ---
if not os.path.exists(args.content_file):
    print(f"ERROR: content file not found: {args.content_file}", file=sys.stderr)
    sys.exit(1)

with open(args.content_file) as f:
    content_html = f.read().strip()

if not content_html:
    print(f"ERROR: content file is empty: {args.content_file}", file=sys.stderr)
    sys.exit(1)

# --- Step 1: Get access token ---
print("Step 1: Fetching access_token...", file=sys.stderr)
token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}'
token_resp = wechat_api(token_url)

if 'access_token' not in token_resp:
    print(f"ERROR: {format_wx_error(token_resp, 'Failed to get access_token')}", file=sys.stderr)
    sys.exit(1)

token = token_resp['access_token']
print(f"  access_token obtained (prefix: {token[:8]}...)", file=sys.stderr)

# --- Step 2: Determine thumb_media_id ---
thumb_id = FALLBACK_THUMB
if args.image and os.path.exists(args.image):
    print(f"Step 2: Uploading cover image: {args.image}", file=sys.stderr)

    with open(args.image, 'rb') as f:
        img_data = f.read()

    if len(img_data) < 100:
        print(f"  Cover image too small ({len(img_data)} bytes), using fallback", file=sys.stderr)
    else:
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
        upload_resp = wechat_api(upload_url, data=body)

        if 'media_id' in upload_resp:
            thumb_id = upload_resp['media_id']
            print(f"  Cover uploaded: {thumb_id[:20]}...", file=sys.stderr)
        else:
            print(f"  WARNING: Cover upload failed, using fallback", file=sys.stderr)
            print(f"  {format_wx_error(upload_resp)}", file=sys.stderr)
else:
    print(f"Step 2: No custom cover, using fallback thumb_id", file=sys.stderr)

# --- Step 3: Create draft ---
print(f"Step 3: Creating draft...", file=sys.stderr)

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
draft_resp = wechat_api(draft_url,
                        data=json.dumps(draft, ensure_ascii=False).encode(),
                        headers={'Content-Type': 'application/json'})

if 'media_id' in draft_resp:
    print(f"DRAFT_OK:{draft_resp['media_id']}")
    sys.exit(0)
else:
    print(f"DRAFT_FAIL:{json.dumps(draft_resp, ensure_ascii=False)}")
    print(f"ERROR: {format_wx_error(draft_resp, 'Failed to create draft')}", file=sys.stderr)
    sys.exit(1)
