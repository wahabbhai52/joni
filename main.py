# Don't Remove Credit Tg - @RIYA40X
# Ask Doubt on telegram @RIYA40X

import os
import re
import sys
import json
import time
import aiohttp
import asyncio
import requests
import subprocess
import urllib.parse
import cloudscraper
import datetime
import random
import ffmpeg
import logging 
import yt_dlp
from aiohttp import web
from core import *
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
import yt_dlp as youtube_dl
import cloudscraper
import m3u8
import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput
from pytube import YouTube
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://fibegi:8oV4fjNNVasSfcoY@cluster0.jp8thup.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "PremiumBot"
COLLECTION_NAME = "PremiumUsers"

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
premium_collection = db[COLLECTION_NAME]

# Logging channel
LOG_CHANNEL = -1002962523737  # Replace with your actual log channel ID

cookies_file_path = os.getenv("COOKIES_FILE_PATH", "youtube_cookies.txt")

# Image URLs
cpimg = "https://graph.org/file/5ed50675df0faf833efef-e102210eb72c1d5a17.jpg"  
hacker_img = "https://graph.org/file/d7d9dbb5f8b14c3f0e5b5.jpg"  # Hacker style image

async def show_random_emojis(message):
    emojis = ['🎊', '🔮', '😎', '⚡️', '🚀', '✨', '💥', '🎉', '🥂', '🍾', '🦠', '🤖', '❤️‍🔥', '🕊️', '💃', '🥳','🐅','🦁']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message
    
# Define the owner's user ID
OWNER_ID = 7660860610  # Replace with the actual owner's user ID

# List of sudo users (initially empty or pre-populated)
SUDO_USERS = [6103594386, 7545056722, 5854926266]

AUTH_CHANNEL = -1002962523737
# Premium system functions
def is_premium_user(user_id: int) -> bool:
    """Check if user is premium"""
    user = premium_collection.find_one({"user_id": user_id})
    if user:
        expiry_date = user.get("expiry_date")
        if expiry_date and datetime.datetime.now() < expiry_date:
            return True
    return False

async def add_premium_user(user_id: int, days: int):
    """Add premium user with expiry date"""
    expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
    premium_collection.update_one(
        {"user_id": user_id},
        {"$set": {"expiry_date": expiry_date}},
        upsert=True
    )

async def remove_premium_user(user_id: int):
    """Remove premium user"""
    premium_collection.delete_one({"user_id": user_id})

async def get_premium_users():
    """Get all premium users"""
    return list(premium_collection.find({}))

# Function to check if a user is authorized
def is_authorized(user_id: int) -> bool:
    return (user_id == OWNER_ID or 
            user_id in SUDO_USERS or 
            user_id == AUTH_CHANNEL or 
            is_premium_user(user_id))

async def log_to_channel(bot: Client, text: str):
    """Log messages to the log channel"""
    try:
        await bot.send_message(LOG_CHANNEL, text)
    except Exception as e:
        print(f"Failed to log to channel: {e}")

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)

# Premium commands
@bot.on_message(filters.command("addpremium") & filters.user(OWNER_ID))
async def add_premium_cmd(bot: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("**Usage:** `/addpremium <user_id> <days>`")
            return

        user_id = int(args[1])
        days = int(args[2])
        
        await add_premium_user(user_id, days)
        await message.reply_text(f"✅ User {user_id} added as premium for {days} days.")
        await log_to_channel(bot, f"#PREMIUM_ADD\nUser: {user_id}\nDays: {days}\nBy: {message.from_user.id}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@bot.on_message(filters.command("removepremium") & filters.user(OWNER_ID))
async def remove_premium_cmd(bot: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("**Usage:** `/removepremium <user_id>`")
            return

        user_id = int(args[1])
        await remove_premium_user(user_id)
        await message.reply_text(f"✅ User {user_id} removed from premium.")
        await log_to_channel(bot, f"#PREMIUM_REMOVE\nUser: {user_id}\nBy: {message.from_user.id}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@bot.on_message(filters.command("premiumlist") & filters.user(OWNER_ID))
async def premium_list_cmd(bot: Client, message: Message):
    try:
        premium_users = await get_premium_users()
        if not premium_users:
            await message.reply_text("No premium users found.")
            return

        text = "**Premium Users List:**\n\n"
        for user in premium_users:
            user_id = user["user_id"]
            expiry = user.get("expiry_date", "No expiry date")
            text += f"User ID: `{user_id}`\nExpiry: `{expiry}`\n\n"

        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        # Sudo command to add/remove sudo users
@bot.on_message(filters.command("sudo"))
async def sudo_command(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        await message.reply_text("**🚫 You are not authorized to use this command.**")
        return

    try:
        args = message.text.split(" ", 2)
        if len(args) < 2:
            await message.reply_text("**Usage:** `/sudo add <user_id>` or `/sudo remove <user_id>`")
            return

        action = args[1].lower()
        target_user_id = int(args[2])

        if action == "add":
            if target_user_id not in SUDO_USERS:
                SUDO_USERS.append(target_user_id)
                await message.reply_text(f"**✅ User {target_user_id} added to sudo list.**")
                await log_to_channel(bot, f"#SUDO_ADD\nUser: {target_user_id}\nBy: {message.from_user.id}")
            else:
                await message.reply_text(f"**⚠️ User {target_user_id} is already in the sudo list.**")
        elif action == "remove":
            if target_user_id == OWNER_ID:
                await message.reply_text("**🚫 The owner cannot be removed from the sudo list.**")
            elif target_user_id in SUDO_USERS:
                SUDO_USERS.remove(target_user_id)
                await message.reply_text(f"**✅ User {target_user_id} removed from sudo list.**")
                await log_to_channel(bot, f"#SUDO_REMOVE\nUser: {target_user_id}\nBy: {message.from_user.id}")
            else:
                await message.reply_text(f"**⚠️ User {target_user_id} is not in the sudo list.**")
        else:
            await message.reply_text("**Usage:** `/sudo add <user_id>` or `/sudo remove <user_id>`")
    except Exception as e:
        await message.reply_text(f"**Error:** {str(e)}")

# Inline keyboard for start command
keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🇮🇳ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ🇮🇳", url=f"https://t.me/RIYA40X") ],
                    [
                    InlineKeyboardButton("🔔ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ🔔", url="https://t.me/RIYA40X") ],
                    [
                    InlineKeyboardButton("🦋ғᴏʟʟᴏᴡ ᴜs🦋", url="https://t.me/RIYA40X")                              
                ],           
            ]
      )
    
# Image URLs for the random image feature
image_urls = [
    "https://graph.org/file/996d4fc24564509244988-a7d93d020c96973ba8.jpg",
    "https://graph.org/file/96d25730136a3ea7e48de-b0a87a529feb485c8f.jpg",
    "https://graph.org/file/6593f76ddd8c735ae3ce2-ede9fa2df40079b8a0.jpg",
    # Add more image URLs as needed
]
random_image_url = random.choice(image_urls)  # kept as-is
# We will use hacker_img (defined earlier) for start photo

# Caption for the image
caption = (
        "**ʜᴇʟʟᴏ👋**\n\n"
        "➠ **ɪ ᴀᴍ ᴛxᴛ ᴛᴏ ᴠɪᴅᴇᴏ ᴜᴘʟᴏᴀᴅᴇʀ ʙᴏᴛ.**\n"
        "➠ **ғᴏʀ ᴜsᴇ ᴍᴇ sᴇɴᴅ /gaurav.\n"
        "➠ **ғᴏʀ ɢᴜɪᴅᴇ sᴇɴᴅ /help."
)
    
# Start command handler (send hacker image)
@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    await bot.send_photo(chat_id=message.chat.id, photo=hacker_img, caption=caption, reply_markup=keyboard)
    
# Stop command handler
@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    if not is_authorized(m.from_user.id):
        await m.reply_text("**🚫 You are not authorized to use this command.**")
        return
        
    await m.reply_text("**𝗦𝘁𝗼𝗽𝗽𝗲𝗱**🚦", True)
    await log_to_channel(bot, f"#BOT_STOPPED\nBy: {m.from_user.id}")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command("restart"))
async def restart_handler(_, m):
    if not is_authorized(m.from_user.id):
        await m.reply_text("**🚫 You are not authorized to use this command.**")
        return
    await m.reply_text("🔮Restarted🔮", True)
    await log_to_channel(bot, f"#BOT_RESTARTED\nBy: {m.from_user.id}")
    os.execl(sys.executable, sys.executable, *sys.argv)
    COOKIES_FILE_PATH = "youtube_cookies.txt"

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    if not is_authorized(m.from_user.id):
        await m.reply_text("🚫 You are not authorized to use this command.")
        return
        
    await m.reply_text("𝗣𝗹𝗲𝗮𝘀𝗲 𝗨𝗽𝗹𝗼𝗮𝗱 𝗧𝗵𝗲 𝗖𝗼𝗼𝗸𝗶𝗲𝘀 𝗙𝗶𝗹𝗲 (.𝘁𝘅𝘁 𝗳𝗼𝗿𝗺𝗮𝘁).", quote=True)

    try:
        input_message: Message = await client.listen(m.chat.id)

        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()

        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(COOKIES_FILE_PATH, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text("✅ 𝗖𝗼𝗼𝗸𝗶𝗲𝘀 𝗨𝗽𝗱𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆.\n\𝗻📂 𝗦𝗮𝘃𝗲𝗱 𝗜𝗻 youtube_cookies.txt.")
        await log_to_channel(bot, f"#COOKIES_UPDATED\nBy: {m.from_user.id}")
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command('e2t'))
async def edit_txt(client, message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply_text("🚫 You are not authorized to use this command.")
        return

    await message.reply_text(
        "🎉 **Welcome to the .txt File Editor!**\n\n"
        "Please send your `.txt` file containing subjects, links, and topics."
    )

    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.document:
        await message.reply_text("🚨 **Error**: Please upload a valid `.txt` file.")
        return

    file_name = input_message.document.file_name.lower()
    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file_name)
    uploaded_file = await input_message.download(uploaded_file_path)

    await message.reply_text(
        "🔄 **Send your .txt file name, or type 'd' for the default file name.**"
    )

    user_response: Message = await bot.listen(message.chat.id)
    if user_response.text:
        user_response_text = user_response.text.strip().lower()
        if user_response_text == 'd':
            final_file_name = file_name
        else:
            final_file_name = user_response_text + '.txt'
    else:
        final_file_name = file_name

    try:
        with open(uploaded_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
    except Exception as e:
        await message.reply_text(f"🚨 **Error**: Unable to read the file.\n\nDetails: {e}")
        return

    subjects = {}
    current_subject = None
    for line in content:
        line = line.strip()
        if line and ":" in line:
            title, url = line.split(":", 1)
            title, url = title.strip(), url.strip()

            if title in subjects:
                subjects[title]["links"].append(url)
            else:
                subjects[title] = {"links": [url], "topics": []}

            current_subject = title
        elif line.startswith("-") and current_subject:
            subjects[current_subject]["topics"].append(line.strip("- ").strip())

    sorted_subjects = sorted(subjects.items())
    for title, data in sorted_subjects:
        data["topics"].sort()

    try:
        final_file_path = os.path.join(UPLOAD_FOLDER, final_file_name)
        with open(final_file_path, 'w', encoding='utf-8') as f:
            for title, data in sorted_subjects:
                for link in data["links"]:
                    f.write(f"{title}:{link}\n")
                for topic in data["topics"]:
                    f.write(f"- {topic}\n")
    except Exception as e:
        await message.reply_text(f"🚨 **Error**: Unable to write the edited file.\n\nDetails: {e}")
        return

    try:
        await message.reply_document(
            document=final_file_path,
            caption="📥**𝗘𝗱𝗶𝘁𝗲𝗱 𝗕𝘆 ➤ Gaurav**"
        )
        await log_to_channel(bot, f"#TXT_EDITED\nBy: {message.from_user.id}")
    except Exception as e:
        await message.reply_text(f"🚨 **Error**: Unable to send the file.\n\nDetails: {e}")
    finally:
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)
            from pytube import Playlist
import youtube_dl

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Utility Functions ---
def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

def get_videos_with_ytdlp(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                title = result.get('title', 'Unknown Title')
                videos = {}
                for entry in result['entries']:
                    video_url = entry.get('url', None)
                    video_title = entry.get('title', None)
                    if video_url:
                        videos[video_title if video_title else "Unknown Title"] = video_url
                return title, videos
            return None, None
    except Exception as e:
        logging.error(f"Error retrieving videos: {e}")
        return None, None

def save_to_file(videos, name):
    filename = f"{sanitize_filename(name)}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        for title, url in videos.items():
            if title == "Unknown Title":
                file.write(f"{url}\n")
            else:
                file.write(f"{title}: {url}\n")
    return filename

# --- Bot Command ---
@bot.on_message(filters.command('yt2txt'))
async def ytplaylist_to_txt(client: Client, message: Message):
    user_id = message.chat.id
    if user_id != OWNER_ID:
        await message.reply_text("**🚫 You are not authorized to use this command.\n\n🫠 This Command is only for owner.**")
        return

    await message.delete()
    editable = await message.reply_text("📥 **Please enter the YouTube Playlist Url :**")
    input_msg = await client.listen(editable.chat.id)
    youtube_url = input_msg.text
    await input_msg.delete()
    await editable.delete()

    title, videos = get_videos_with_ytdlp(youtube_url)
    if videos:
        file_name = save_to_file(videos, title)
        await message.reply_document(
            document=file_name, 
            caption=f"`{title}`\n\n📥 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤ Gaurav"
        )
        await log_to_channel(bot, f"#YT2TXT\nURL: {youtube_url}\nBy: {message.from_user.id}")
        os.remove(file_name)
    else:
        await message.reply_text("⚠️ **Unable to retrieve videos. Please check the URL.**")

# List users command
@bot.on_message(filters.command("userlist") & filters.user(SUDO_USERS))
async def list_users(client: Client, msg: Message):
    if SUDO_USERS:
        users_list = "\n".join([f"User ID : `{user_id}`" for user_id in SUDO_USERS])
        await msg.reply_text(f"SUDO_USERS :\n{users_list}")
    else:
        await msg.reply_text("No sudo users.")

# Help command
@bot.on_message(filters.command("help"))
async def help_command(client: Client, msg: Message):
    help_text = (
        "`/start` - Start the bot⚡\n\n"
        "`/gaurav` - Download and upload files (sudo)🎬\n\n"
        "`/restart` - Restart the bot🔮\n\n" 
        "`/stop` - Stop ongoing process🛑\n\n"
        "`/cookies` - Upload cookies file🍪\n\n"
        "`/e2t` - Edit txt file📝\n\n"
        "`/yt2txt` - Create txt of yt playlist (owner)🗃️\n\n"
        "`/sudo add` - Add user or group or channel (owner)🎊\n\n"
        "`/sudo remove` - Remove user or group or channel (owner)❌\n\n"
        "`/userlist` - List of sudo user or group or channel📜\n\n"
        "`/addpremium` - Add premium user (owner)💰\n\n"
        "`/removepremium` - Remove premium user (owner)🚫\n\n"
        "`/premiumlist` - List premium users (owner)📋\n\n"
    )
    await msg.reply_text(help_text)
 @bot.on_message(filters.command("gaurav"))
 async def gaurav_command(bot: Client, m: Message):
    if not is_authorized(m.from_user.id):
        await m.reply_text("🚫 You are not authorized to use this command.")
        return

    await m.reply_text("📂 **Please send the TXT file with links.**")
    input1 = await bot.listen(m.chat.id)

    if not input1.document or not input1.document.file_name.endswith(".txt"):
        await m.reply_text("⚠️ Please upload a valid `.txt` file.")
        return

    txt_path = await input1.download()

    await m.reply_text("📜 **Send the starting index (e.g., 1):**")
    input2 = await bot.listen(m.chat.id)
    raw_text = input2.text

    await m.reply_text("🎥 **Enter quality (e.g., 720, 480):**")
    input3 = await bot.listen(m.chat.id)
    raw_text2 = input3.text

    await m.reply_text("💬 **Enter batch name:**")
    input4 = await bot.listen(m.chat.id)
    b_name = input4.text

    await m.reply_text("🔑 **Enter token/pwtoken if needed:**")
    input5 = await bot.listen(m.chat.id)
    raw_text4 = input5.text

    await m.reply_text("🖼 **Enter thumbnail URL or 'no':**")
    input6 = await bot.listen(m.chat.id)

    # Read links from txt
    with open(txt_path, "r", encoding="utf-8") as file:
        content = file.read().splitlines()
    links = []
    for line in content:
        if ":" in line:
            title, link = line.split(":", 1)
            links.append((title.strip(), link.strip()))

    # Send hacker image as process start notification
    await bot.send_photo(chat_id=m.chat.id, photo=hacker_img, caption=f"💻 **Batch `{b_name}` starting...**\n\n🔢 From Index: {raw_text}")

    # Download loop
    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb == "no"

    failed_count = 0
    count = int(raw_text) if len(links) > 1 else 1

    try:
        for i in range(count - 1, len(links)):
            V = links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
            url = "https://" + V if not V.startswith("http") else V

            # --- Injected API priority handling ---
            if "media-cdn.classplusapp.com/drm/" in url or "/master.mpd" in url or "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                try:
                    # 1st API
                    api_url = f"https://drm-api-one.vercel.app/api?url={url}&token={raw_text4}"
                    resp = requests.get(api_url, timeout=15)
                    if resp.status_code != 200 or not resp.text.strip():
                        # 2nd API
                        api_url = f"https://drm-api-one.vercel.app/api?url={url}&token={raw_text4}"
                        resp = requests.get(api_url, timeout=15)
                    if resp.status_code != 200 or not resp.text.strip():
                        # 3rd API
                        api_url = f"https://drm-api-one.vercel.app/api?url={url}&token={raw_text4}}"
                        resp = requests.get(api_url, timeout=15)

                    final_url = resp.text.strip()
                    if final_url:
                        url = final_url
                        await bot.send_photo(chat_id=m.chat.id, photo=hacker_img, caption=f"💻 DRM Extracted\n🔗 `{url}`")
                    else:
                        await m.reply_text("❌ DRM extraction failed from all APIs.")
                        continue
                except Exception as e:
                    await m.reply_text(f"⚠️ API Error: {str(e)}")
                    continue
                 elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                elif 'Key-Pair-Id' in url:
                    url = None
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)

            elif 'drmcdni' in url or 'drm/wv' in url:
                Show = f"<i><b>⚡Fast Video Downloading</b></i>\n<blockquote><b>{str(count).zfill(3)}) {links[i][0]}</b></blockquote>"
                prog = await bot.send_message(m.chat.id, Show, disable_web_page_preview=True)

            elif 'khansirvod4.pc.cdn.bitgravity.com' in url:               
                parts = url.split('/')               
                part1 = parts[1]
                part2 = parts[2]
                part3 = parts[3] 
                part4 = parts[4]
                part5 = parts[5]
                url = f"https://kgs-v4.akamaized.net/kgs-cv/{part3}/{part4}/{part5}"

            # Format selector
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            # Brightcove auth fix
            if "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=...<AUTH TOKEN>...'
                url = url.split("bcov_auth")[0]+bcov

            # yt-dlp command builder
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
                cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
             # Execute download
            try:
                process = subprocess.Popen(cmd, shell=True)
                process.wait()

                # Send downloaded file
                if os.path.exists(f"{name}.mp4"):
                    await m.reply_video(video=f"{name}.mp4", caption=f"✅ {name}")
                    os.remove(f"{name}.mp4")
                else:
                    await m.reply_text(f"⚠️ Download failed for {name}")
                    failed_count += 1

                count += 1

            except Exception as e:
                await m.reply_text(f'‼️ Download Failed: {name}\nError: {str(e)}')
                count += 1
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(str(e))
        await log_to_channel(bot, f"#ERROR\nError in /gaurav command\nError: {str(e)}\nBy: {m.from_user.id}")
    
    await m.reply_text(f"`✨𝗕𝗔𝗧𝗖𝗛 𝗦𝗨𝗠𝗠𝗔𝗥𝗬✨\n\n"
                       f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                       f"📛𝗜𝗻𝗱𝗲𝘅 𝗥𝗮𝗻𝗴𝗲 » ({raw_text} to {len(links)})\n"
                       f"📚𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 » {b_name}\n\n"
                       f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                       f"✨𝗧𝗫𝗧 𝗦𝗨𝗠𝗠𝗔𝗥𝗬✨ : {len(links)}\n"
                       f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                       f"🔹𝗩𝗶𝗱𝗲𝗼 » {count - failed_count}\n🔹𝗙𝗮𝗶𝗹𝗲𝗱 𝗨𝗿𝗹 » {failed_count}\n\n"
                       f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                       f"✅𝗦𝗧𝗔𝗧𝗨𝗦 » 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗`")
    await m.reply_text(f"<pre><code>📥 Extracted By ➤『Gaurav』</code></pre>")
    await log_to_channel(bot, f"#BATCH_COMPLETED\nUser: {m.from_user.id}\nBatch: {b_name}\nTotal: {len(links)}\nFailed: {failed_count}")

bot.run()
if __name__ == "__main__":
    asyncio.run(main())      
