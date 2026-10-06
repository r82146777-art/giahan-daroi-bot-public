#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""هر پست = یک گیاه/ادویه/میوه متفاوت | ۸–۲۳ تهران | بدون تکرار"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API_TIMEOUT = 25
STATE_FILE = Path("state.json")
POSTS_FILE = Path("posts.json")
TEHRAN = timezone(timedelta(hours=3, minutes=30))
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://rubika.ir/giahanedaroi").strip()
DESTINATIONS = [
    os.environ.get("CHAT_ID", "").strip(),
    "c0Cr7CY010ddee1b54438f20491db663",
    "@giahanedaroi",
]


def tehran_now():
    return datetime.now(TEHRAN)


def is_active(now):
    return 8 <= now.hour <= 23


def hour_key(now):
    return f"{now.strftime('%Y-%m-%d')}-{now.hour:02d}"


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    data.setdefault("index", 0)
    data.setdefault("used_keys", [])
    data.setdefault("used_plants", [])
    data.setdefault("last_hour_key", None)
    data.setdefault("sent_count", 0)
    data.setdefault("sent_hours", {})
    return data


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_text(token, chat_id, text):
    url = f"https://botapi.rubika.ir/v3/{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=API_TIMEOUT)
    print("Trying", chat_id, "HTTP", resp.status_code, resp.text[:250])
    try:
        data = resp.json()
    except Exception:
        return False
    return data.get("status") == "OK" or bool((data.get("data") or {}).get("message_id"))


def with_footer(body):
    body = body.rstrip()
    if "rubika.ir/giahanedaroi" in body:
        return body
    return body + "\n\n🔗 کانال گیاهان دارویی ارسباران:\n" + CHANNEL_LINK


def next_post(posts, state):
    n = len(posts)
    used_keys = set(state.get("used_keys", []))
    used_plants = set(state.get("used_plants", []))
    idx = int(state.get("index", 0)) % n
    for _ in range(n):
        key, name, body = posts[idx]
        if key not in used_keys and name not in used_plants:
            state["index"] = (idx + 1) % n
            return key, name, body
        idx = (idx + 1) % n
    print("همه گیاهان یک دور کامل شدند — شروع دوباره")
    state["used_keys"] = []
    state["used_plants"] = []
    key, name, body = posts[0]
    state["index"] = 1
    return key, name, body


def main():
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        print("ERROR: BOT_TOKEN missing")
        return 1
    force = os.environ.get("FORCE", "").strip().lower() in ("1", "true", "yes")
    now = tehran_now()
    print("Tehran:", now.isoformat(), "force=", force)
    if not force and not is_active(now):
        print("SKIP: outside 8-23")
        return 0
    hk = hour_key(now)
    state = load_state()
    if not force and state.get("last_hour_key") == hk:
        print("SKIP: already posted this hour")
        return 0
    posts = load_posts()
    print("posts loaded:", len(posts))
    key, name, body = next_post(posts, state)
    text = with_footer(body)
    print("Plant:", name, "key=", key)
    print("preview:", text[:200])
    ok = False
    tried = []
    for chat_id in DESTINATIONS:
        if not chat_id or chat_id in tried:
            continue
        tried.append(chat_id)
        if send_text(token, chat_id, text):
            print("OK ->", chat_id)
            ok = True
            break
    if not ok:
        print("ERROR: send failed")
        return 1
    state.setdefault("used_keys", []).append(key)
    state.setdefault("used_plants", []).append(name)
    state["last_hour_key"] = hk
    state["last_sent_date"] = now.strftime("%Y-%m-%d")
    state["last_sent_hour"] = now.hour
    state["sent_count"] = int(state.get("sent_count", 0)) + 1
    today = now.strftime("%Y-%m-%d")
    hours = list(state.get("sent_hours", {}).get(today, []))
    if now.hour not in hours:
        hours.append(now.hour)
    state.setdefault("sent_hours", {})[today] = sorted(hours)
    save_state(state)
    print("saved plant=", name, "sent_count=", state["sent_count"], "unique_plants=", len(state["used_plants"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
