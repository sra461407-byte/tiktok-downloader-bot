import telebot
import requests
import re
from telebot import types
import os

# የቦት መለያ (Token)
API_TOKEN = '8643345893:8560255786:AAHp95uRgo9GRFKkF3pOw7wCXVPZFXVLQqs'
bot = telebot.TeleBot(API_TOKEN)

# ያንተ መረጃዎች
CHANNEL_ID = "@TokSaveHub" 
ADMIN_ID = 8157391333 # እዚህ ጋር በ @userinfobot ያገኘኸውን ያንተን ID ተካው

# ተጠቃሚዎችን ለመመዝገብ የሚያገለግል ፋይል
USER_FILE = "users.txt"

def register_user(user_id):
    """አዲስ ተጠቃሚ ሲመጣ በፋይል ውስጥ ይመዘግባል"""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            pass
    
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

def is_subscribed(user_id):
    """ተጠቃሚው ቻናሉን መቀላቀሉን ያረጋግጣል"""
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    register_user(message.from_user.id)
    welcome_text = (
        "👋 **እንኳን ወደ መጀመሪያው የኢትዮጵያ ቲክቶክ ማውረጃ ቦት በደህና መጡ! 🇪🇹**\n\n"
        "ማንኛውንም የቲክቶክ ቪዲዮ ያለ ምንም የውሃ ምልክት (Watermark) በነፃ ማውረድ ይችላሉ።\n\n"
        f"⚠️ **ማሳሰቢያ:** ቦቱን ለመጠቀም መጀመሪያ ቻናላችንን {CHANNEL_ID} መቀላቀል አለብዎት!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """ለአድሚን ብቻ የሰዎችን ብዛት ያሳያል"""
    if message.from_user.id == ADMIN_ID:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as f:
                count = len(f.read().splitlines())
            bot.reply_to(message, f"📊 **የቦቱ ጠቅላላ ተጠቃሚዎች ብዛት፦ {count}**")
        else:
            bot.reply_to(message, "📊 የቦቱ ተጠቃሚዎች ገና አልተመዘገቡም።")
    else:
        bot.reply_to(message, "❌ ይህ ትዕዛዝ ለአድሚን ብቻ ነው።")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    register_user(user_id)
    
    # 1. ቻናሉን መቀላቀሉን ማረጋገጥ
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✨ ቻናላችንን ይቀላቀሉ ✨", url=f"https://t.me/TokSaveHub")
        markup.add(btn)
        
        bot.reply_to(
            message, 
            f"⚠️ **ይቅርታ! መጀመሪያ ቻናላችንን መቀላቀል አለብዎት።**\n\nእባክዎ {CHANNEL_ID} ይቀላቀሉ እና ሊንኩን ደግመው ይላኩ።", 
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return

    # 2. ሊንኩን መፈለግ
    links = re.findall(r'(https?://[^\s]+)', message.text)
    if not links or 'tiktok.com' not in links[0]:
        if message.text != "/start":
            bot.reply_to(message, "❌ **እባክዎ ትክክለኛ የቲክቶክ ሊንክ ይላኩ።**")
        return

    url = links[0]
    processing_msg = bot.reply_to(message, "⏳ **ቪዲዮውን በማዘጋጀት ላይ ነኝ... እባክዎ ይጠብቁ**")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url).json()
        
        if res['code'] == 0:
            video_url = res['data']['play']
            bot.delete_message(message.chat.id, processing_msg.message_id)
            
            bot.send_video(
                message.chat.id, 
                video_url, 
                caption=f"✅ **ቪዲዮው በተሳካ ሁኔታ ወርዷል!**\n\n🚀 Join: {CHANNEL_ID}\n🤖 Bot: @TokSaverXBot",
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text("❌ **ይቅርታ ቪዲዮው አልተገኘም።**", message.chat.id, processing_msg.message_id)
    except Exception:
        bot.edit_message_text("⚠️ **የኢንተርኔት መቆራረጥ አጋጥሟል። እባክዎ ደግመው ይሞክሩ።**", message.chat.id, processing_msg.message_id)

if __name__ == "__main__":
    print("ቦቱ ስራ ጀምሯል...")
    bot.infinity_polling()
