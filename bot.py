#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات گیاهان دارویی — فقط متن
هر ساعت تهران (۸ تا ۲۳) یک پست | بدون تکرار
"""
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API_TIMEOUT = 25
STATE_FILE = Path("state.json")
TEHRAN = timezone(timedelta(hours=3, minutes=30))
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://rubika.ir/giahanedaroi").strip()

DESTINATIONS = [
    os.environ.get("CHAT_ID", "").strip(),
    "c0Cr7CY010ddee1b54438f20491db663",
    "@giahanedaroi",
]

HERBS = [
    {"e": "🌿", "n": "آویشن", "about": "آویشن یکی از معروف‌ترین گیاهان دارویی معطر است و از دیرباز برای مشکلات تنفسی در طب سنتی به کار می‌رود.",
     "benefits": ["کمک به تسکین سرفه و خلط‌آوری", "تقویت نسبی ایمنی در سرماخوردگی", "خاصیت ضدباکتریایی ملایم برای گلو"],
     "harms": ["مصرف زیاد ممکن است معده را تحریک کند", "در بارداری بدون نظر پزشک توصیه نمی‌شود"],
     "how": "دم‌کرده روزی ۱ تا ۲ فنجان با عسل"},
    {"e": "🌱", "n": "زنجبیل", "about": "زنجبیل ریشهٔ تند و گرمی است که برای هضم، تهوع و گرم کردن بدن کاربرد دارد.",
     "benefits": ["کاهش حالت تهوع", "کمک به هضم و کاهش نفخ", "گرم‌کننده بدن"],
     "harms": ["در زخم معده فعال احتیاط", "تداخل احتمالی با رقیق‌کننده‌های خون"],
     "how": "چای زنجبیل تازه با عسل و لیمو"},
    {"e": "🍃", "n": "نعناع", "about": "نعناع گیاه خنک و معطری است که بیشتر برای گوارش و تازگی دهان شناخته می‌شود.",
     "benefits": ["کاهش نفخ", "حس خنکی بعد از غذا", "کاهش موقت بوی بد دهان"],
     "harms": ["در ریفلاکس شدید گاهی علائم را بدتر می‌کند", "اسانس خالص نباید بلعیده شود"],
     "how": "دم‌کرده بعد از غذا"},
    {"e": "🌼", "n": "بابونه", "about": "بابونه گل آرامش‌بخش کلاسیک طب سنتی است و برای خواب و آرام کردن معده به کار می‌رود.",
     "benefits": ["کمک به آرامش و خواب", "تسکین التهاب خفیف معده", "آرام‌بخش اضطراب روزمره"],
     "harms": ["حساسیت در آلرژی به کاسنی", "خواب‌آلودگی در مصرف زیاد"],
     "how": "دم‌کرده شب قبل خواب"},
    {"e": "🌰", "n": "شیرین‌بیان", "about": "شیرین‌بیان ریشهٔ شیرین دارویی است که برای گلو و معده شهرت دارد؛ مصرفش باید محدود باشد.",
     "benefits": ["تسکین گلودرد", "آرامش مخاط معده خفیف"],
     "harms": ["افزایش فشار خون در مصرف طولانی", "برای فشارخونی و باردار خطرناک‌تر"],
     "how": "دم‌کرده رقیق کوتاه‌مدت"},
    {"e": "🌿", "n": "رزماری", "about": "رزماری گیاه مدیترانه‌ای معطر است برای تمرکز و گردش خون.",
     "benefits": ["کمک به هوشیاری و تمرکز", "بهبود گردش خون موضعی"],
     "harms": ["اسانس غلیظ در بارداری و صرع ممنوع", "مصرف خوراکی خیلی زیاد تحریک‌کننده"],
     "how": "دم‌کرده صبحگاهی رقیق"},
    {"e": "🍃", "n": "اسطوخودوس", "about": "اسطوخودوس با عطر آرامش‌بخش برای استرس و خواب محبوب است.",
     "benefits": ["کاهش استرس", "کمک به خواب", "تسکین سردرد تنش‌زا"],
     "harms": ["اسانس خالص خوراکی نیست", "حساسیت پوستی در برخی"],
     "how": "کیسه خشک کنار بالش یا بخور ملایم"},
    {"e": "🌱", "n": "زردچوبه", "about": "زردچوبه ادویه طلایی ضدالتهاب است؛ کورکومین آن بیشتر مورد توجه است.",
     "benefits": ["کمک به کاهش التهاب خفیف", "پشتیبانی از مفاصل", "آنتی‌اکسیدان غذایی"],
     "harms": ["تداخل با ضد انعقاد", "در سنگ کیسه صفرا احتیاط"],
     "how": "با فلفل سیاه و کمی روغن در غذا"},
    {"e": "🌿", "n": "گزنه", "about": "گزنه غنی از مواد معدنی است و در طب سنتی برای خون‌سازی معروف است.",
     "benefits": ["منبع گیاهی آهن", "ادرارآور ملایم"],
     "harms": ["برگ تازه پوست را می‌سوزاند", "تداخل با ادرارآورها"],
     "how": "دم‌کرده برگ خشک دوره‌ای"},
    {"e": "🌼", "n": "گل گاوزبان", "about": "گل گاوزبان در فرهنگ ایرانی نماد آرامش اعصاب است.",
     "benefits": ["آرام‌بخش ملایم اعصاب", "دمنوش عصرگاهی"],
     "harms": ["مصرف طولانی بدون وقفه توصیه نمی‌شود", "در بارداری محدود"],
     "how": "دم‌کرده با لیموترش"},
    {"e": "🍃", "n": "پونه", "about": "پونه عطر تند دارد و در آش ایرانی برای گوارش به کار می‌رود.",
     "benefits": ["کاهش نفخ", "کمک در سرماخوردگی خفیف"],
     "harms": ["اسانس غلیظ سمی است", "در بارداری ممنوع"],
     "how": "دم‌کرده ملایم بعد از غذا"},
    {"e": "🌱", "n": "دارچین", "about": "دارچین ادویه گرم خوش‌عطر است که با قند خون و گرمی بدن پیوند دارد.",
     "benefits": ["کمک به پاسخ بهتر قند خون همراه غذا", "گرم‌کننده و ضدنفخ ملایم"],
     "harms": ["کاسیا کومارین بالا دارد", "در بارداری زیاده‌روی نشود"],
     "how": "تکه کوچک در چای"},
    {"e": "🌿", "n": "شوید", "about": "شوید سبزی سفره و گیاه سنتی برای آرام کردن شکم است.",
     "benefits": ["کاهش نفخ", "کمک به هضم غذای سنگین"],
     "harms": ["دانه خیلی زیاد ممکن است حساسیت دهد"],
     "how": "دم‌کرده تخم یا برگ بعد از غذا"},
    {"e": "🌱", "n": "رازیانه", "about": "رازیانه طعم شیرین انیسون‌مانند دارد و برای گوارش به کار می‌رود.",
     "benefits": ["کاهش نفخ و اسپاسم روده", "کمک به هضم"],
     "harms": ["سرطان‌های حساس به هورمون: مشورت پزشک"],
     "how": "دم‌کرده دانه"},
    {"e": "🍃", "n": "بادرنجبویه", "about": "بادرنجبویه عطر لیمویی دارد و برای اضطراب و خواب استفاده می‌شود.",
     "benefits": ["کاهش اضطراب خفیف", "کمک به خواب آرام‌تر"],
     "harms": ["تداخل احتمالی با داروهای تیروئید"],
     "how": "دم‌کرده شب"},
    {"e": "🌼", "n": "گل محمدی", "about": "گل محمدی برای آرامش و طراوت روح و پوست در طب سنتی جایگاه دارد.",
     "benefits": ["آرام‌بخش ملایم خلق", "عطر درمانی"],
     "harms": ["گلاب تقلبی مفید نیست"],
     "how": "دم‌کرده گلبرگ یا گلاب اصل"},
    {"e": "🌿", "n": "مرزنجوش", "about": "مرزنجوش گیاه معطر برای سرفه و آرامش تنفسی است.",
     "benefits": ["کمک به راحتی تنفس در سرماخوردگی خفیف", "ضدنفخ ملایم"],
     "harms": ["در بارداری زیاده‌روی نشود"],
     "how": "دم‌کرده رقیق"},
    {"e": "🌱", "n": "زیره سبز", "about": "زیره سبز ادویه اصلی آشپزی ایرانی است و برای نفخ شهرت دارد.",
     "benefits": ["کاهش نفخ بعد از غذا", "کمک به هضم حبوبات"],
     "harms": ["خیلی زیاد سوزش سر دل می‌دهد"],
     "how": "دم‌کرده بعد از غذا"},
    {"e": "🍃", "n": "به‌لیمو", "about": "به‌لیمو عطر لیموی لطیف دارد و دمنوش محبوب عصر است.",
     "benefits": ["کاهش تنش عصبی", "کمک به خواب سبک"],
     "harms": ["حساسیت نادر"],
     "how": "دم‌کرده عصر یا شب"},
    {"e": "🌼", "n": "گل ختمی", "about": "گل ختمی برای نرم کردن مخاط گلو در سرفه‌های خشک معروف است.",
     "benefits": ["تسکین خشکی گلو", "کمک به سرفه خشک"],
     "harms": ["ممکن است جذب دارو را کم کند"],
     "how": "دم‌کرده یا خیساندن سرد"},
    {"e": "🌱", "n": "سیاه‌دانه", "about": "سیاه‌دانه در متون سنتی برای ایمنی و التهاب جایگاه دارد.",
     "benefits": ["پشتیبانی از پاسخ ایمنی", "ضدالتهاب سنتی"],
     "harms": ["بارداری: خودسرانه نه"],
     "how": "نصف قاشق چای‌خوری با عسل"},
    {"e": "🍃", "n": "تخم کتان", "about": "تخم کتان منبع امگا۳ گیاهی و فیبر است.",
     "benefits": ["کمک به نظم اجابت مزاج", "فیبر مفید"],
     "harms": ["بدون آب کافی مشکل‌ساز است"],
     "how": "یک قاشق خیس‌شده صبح با آب زیاد"},
    {"e": "🌿", "n": "مریم‌گلی", "about": "مریم‌گلی برای غرغره گلودرد و کاهش تعریق شناخته شده است.",
     "benefits": ["غرغره گلودرد", "کاهش تعریق زیاد"],
     "harms": ["مصرف خوراکی طولانی خطرناک است"],
     "how": "غرغره دم‌کرده رقیق"},
    {"e": "🌱", "n": "هل", "about": "هل ادویه خوش‌عطر برای هضم و خوشبویی دهان است.",
     "benefits": ["کاهش بوی بد دهان", "کمک به هضم"],
     "harms": ["سنگ صفرا: احتیاط"],
     "how": "دانه در چای"},
    {"e": "🍃", "n": "چای سبز", "about": "چای سبز نوشیدنی آنتی‌اکسیدانی با کافئین ملایم است.",
     "benefits": ["آنتی‌اکسیدان کاتچین", "هوشیاری ملایم"],
     "harms": ["کافئین برای بی‌خوابی‌ها مشکل است", "ناشتا گاهی سوزش معده"],
     "how": "آب داغ نه جوش؛ ۱–۲ فنجان بین وعده‌ها"},
]

STYLES = [
    "امروز دربارهٔ این گیاه بیشتر بدانیم:",
    "آشنایی دقیق‌تر با یک گیاه پرکاربرد:",
    "راهنمای کاربردی و ایمن برای مصرف:",
    "از خواص تا احتیاط‌ها در یک نگاه:",
    "نکات مهم قبل از مصرف این گیاه:",
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
    data.setdefault("used", [])
    data.setdefault("last_hour_key", None)
    data.setdefault("sent_count", 0)
    data.setdefault("sent_hours", {})
    return data


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def build_text(herb, style):
    b = random.choice(herb["benefits"])
    h = random.choice(herb["harms"])
    others = [x for x in herb["benefits"] if x != b][:2]
    text = (
        f"{herb['e']} {herb['n']}\n\n"
        f"{style}\n\n"
        f"{herb['about']}\n\n"
        f"✅ خواص و موارد مفید:\n• {b}\n"
        + "".join(f"• {x}\n" for x in others)
        + f"\n⚠️ مضرات و احتیاط‌ها:\n• {h}\n"
        + f"\n📌 روش مصرف پیشنهادی:\n{herb['how']}\n\n"
        f"💬 جنبهٔ آموزشی دارد و جایگزین تشخیص و درمان پزشکی نیست.\n\n"
        f"🔗 کانال گیاهان دارویی ارسباران:\n{CHANNEL_LINK}"
    )
    key = hashlib.md5(f"{herb['n']}|{style}|{b}|{h}".encode()).hexdigest()[:16]
    return key, text


def pick_post(state):
    used = set(state.get("used", []))
    herbs = list(HERBS)
    random.shuffle(herbs)
    for herb in herbs:
        for style in STYLES:
            key, text = build_text(herb, style)
            if key not in used:
                return key, text, herb["n"]
    state["used"] = []
    herb = random.choice(HERBS)
    style = random.choice(STYLES)
    key, text = build_text(herb, style)
    return key, text, herb["n"]


def send_text(token, chat_id, text):
    url = f"https://botapi.rubika.ir/v3/{token}/sendMessage"
    resp = requests.post(
        url, json={"chat_id": chat_id, "text": text}, timeout=API_TIMEOUT
    )
    print("Trying", chat_id, "HTTP", resp.status_code, resp.text[:300])
    try:
        data = resp.json()
    except Exception:
        return False
    return data.get("status") == "OK" or bool(
        (data.get("data") or {}).get("message_id")
    )


def main():
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        print("ERROR: BOT_TOKEN is missing")
        return 1

    force = os.environ.get("FORCE", "").strip() in ("1", "true", "yes")
    now = tehran_now()
    print("Tehran now:", now.isoformat(), "force=", force)

    if not force and not is_active(now):
        print("SKIP: outside active hours (8:00–23:00 Tehran)")
        return 0

    hk = hour_key(now)
    print("Current hour key:", hk)

    state = load_state()
    if not force and state.get("last_hour_key") == hk:
        print("SKIP: already posted for this hour")
        return 0

    key, text, name = pick_post(state)
    print("Herb:", name, "key:", key)
    print("preview:", text[:160])

    ok = False
    tried = []
    for chat_id in DESTINATIONS:
        if not chat_id or chat_id in tried:
            continue
        tried.append(chat_id)
        if send_text(token, chat_id, text):
            print("Posted to", chat_id)
            ok = True
            break

    if not ok:
        print("ERROR: could not send")
        return 1

    state.setdefault("used", []).append(key)
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
    print("State saved. sent_count=", state["sent_count"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
