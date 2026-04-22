import telebot
import requests
import re
from telebot import types

API_TOKEN = '8643345893:AAEG8UNOaOUYTslLV8oAkjMQTNoEWoOlVQY'
bot = telebot.TeleBot(API_TOKEN)
CHANNEL_ID = "@TokSaveHub" # ያንተ ቻናል

# ተጠቃሚው ቻናሉን መቀላቀሉን የሚያረጋግጥ ተግባር
def is_subscribed(user_id):
    try:
        # ቦቱ በቻናሉ ላይ አድሚን መሆን አለበት
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        # ስህተት ከተፈጠረ (ለምሳሌ ቦቱ አድሚን ካልሆነ) ለጊዜው እንዲያልፍ እናደርገዋለን
        print(f"Sub check error: {e}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to TokSave Downloader!**\n\n"
        "Download TikTok videos without watermark for free.\n\n"
        f"📢 **Note:** You MUST join {CHANNEL_ID} to use this bot!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    
    # 1. ቻናሉን መቀላቀሉን ማረጋገጥ
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✨ Join Our Channel ✨", url=f"https://t.me/TokSaveHub")
        markup.add(btn)
        
        bot.reply_to(
            message, 
            f"⚠️ **Access Denied!**\n\nYou must join our channel {CHANNEL_ID} to use this bot. After joining, try sending the link again.", 
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return

    # 2. ሊንኩን መፈለግ
    links = re.findall(r'(https?://[^\s]+)', message.text)
    if not links or 'tiktok.com' not in links[0]:
        if message.text != "/start":
            bot.reply_to(message, "❌ **Please send a valid TikTok link.**")
        return

    url = links[0]
    processing_msg = bot.reply_to(message, "⏳ **Processing your video...**")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url).json()
        
        if res['code'] == 0:
            video_url = res['data']['play']
            bot.delete_message(message.chat.id, processing_msg.message_id)
            
            bot.send_video(
                message.chat.id, 
                video_url, 
                caption=f"✅ **Downloaded Successfully!**\n\n🚀 Join: {CHANNEL_ID}",
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text("❌ **Error: Video not found.**", message.chat.id, processing_msg.message_id)
    except Exception as e:
        bot.edit_message_text("⚠️ **Connection error. Try again.**", message.chat.id, processing_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
