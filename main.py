import telebot
import requests
import re
from telebot import types

API_TOKEN = '8643345893:AAEG8UNOaOUYTslLV8oAkjMQTNoEWoOlVQY'
bot = telebot.TeleBot(API_TOKEN)
CHANNEL_ID = "@TokSaveHub" # የቻናልህ USERNAME

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to TokSave Downloader!**\n\n"
        "I can download TikTok videos without watermark for free.\n\n"
        f"❗ **Note:** You must join {CHANNEL_ID} to use this bot."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    # 1. Check Subscription
    if not check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        bot.reply_to(message, f"⚠️ **Please join our channel first to use the bot!**\nOnce joined, send your link again.", reply_markup=markup)
        return

    # 2. Extract Link (ተጨማሪ ጽሑፎችን ለማጽዳት)
    links = re.findall(r'(https?://[^\s]+)', message.text)
    if not links or 'tiktok.com' not in links[0]:
        if message.text != "/start":
            bot.reply_to(message, "❌ **Please send a valid TikTok link.**")
        return

    url = links[0]
    msg = bot.reply_to(message, "⏳ **Processing...**")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url).json()
        
        if res['code'] == 0:
            video_data = res['data']
            video_url = video_data['play'] # No Watermark video
            
            bot.edit_message_text("📥 **Sending video to you...**", message.chat.id, msg.message_id)
            
            bot.send_video(
                message.chat.id, 
                video_url, 
                caption=f"✅ **Downloaded by @{bot.get_me().username}**\n\n🚀 **Join:** {CHANNEL_ID}",
                parse_mode='Markdown'
            )
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ **Video not found or link expired.**", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("⚠️ **Connection error. Please try again.**", message.chat.id, msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
