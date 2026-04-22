import telebot
import requests
from telebot import types

API_TOKEN = '8643345893:AAEG8UNOaOUYTslLV8oAkjMQTNoEWoOlVQY'
bot = telebot.TeleBot(API_TOKEN)
CHANNEL_USERNAME = "@TokSaveHub"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to TikTok Downloader Bot!**\n\n"
        "Send me any TikTok video link, and I will download it for you without watermark.\n\n"
        f"📢 **Join our channel:** {CHANNEL_USERNAME}"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: 'tiktok.com' in message.text)
def handle_tiktok(message):
    url = message.text
    msg = bot.reply_to(message, "⏳ **Processing your link... Please wait.**", parse_mode='Markdown')
    
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()
        
        if response['code'] == 0:
            video_data = response['data']
            video_id = video_data['id']
            # እዚህ ጋር ለጊዜው No Watermark ሊንኩን እናስቀምጣለን
            no_wm_url = video_data['play']
            wm_url = video_data['wmplay']
            
            markup = types.InlineKeyboardMarkup()
            # ዳታውን በ callback_data በኩል እናስተላልፋለን
            btn1 = types.InlineKeyboardButton("🚀 No Watermark (HD)", callback_data=f"dl_no_{video_id}")
            btn2 = types.InlineKeyboardButton("🎬 Original (Watermark)", callback_data=f"dl_wm_{video_id}")
            markup.add(btn1, btn2)
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text="✅ **Video Found! Choose your preferred quality:**",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text("❌ **Invalid link or Video not found.**", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("⚠️ **Error occurred while fetching video.**", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def handle_download(call):
    video_id = call.data.split('_')[2]
    type_choice = call.data.split('_')[1] # 'no' ወይም 'wm'
    
    bot.answer_callback_query(call.id, "Downloading video...")
    
    # ተጠቃሚው የመረጠውን ለማግኘት በድጋሚ API እንጠይቃለን (ቀላሉ መንገድ ይሄ ነው)
    try:
        # መጀመሪያ "Sending" የሚለውን መልእክት እናሳይ
        status_msg = bot.send_message(call.message.chat.id, "📥 **Downloading to our server...**", parse_mode='Markdown')
        
        # የቪዲዮውን ሊንክ በ ID ማግኘት ስላልቻልን በቪዲዮው ኦሪጅናል ሊንክ ፋንታ ቀጥታ API እንጠቀማለን
        # ማሳሰቢያ፡ ለተሟላ ስራ የቪዲዮውን ሊንክ ለጊዜው በዳታቤዝ መያዝ ይመረጣል
        # ግን አሁን ለሙከራ ያህል ቀጥታ ቪዲዮውን ለመላክ እንሞክር
        
        api_url = f"https://www.tikwm.com/api/?id={video_id}" # በ ID ለመጠየቅ
        res = requests.get(api_url).json()
        
        if type_choice == 'no':
            final_video = res['data']['play']
        else:
            final_video = res['data']['wmplay']
            
        bot.send_video(
            call.message.chat.id, 
            final_video, 
            caption=f"✅ **Success!**\n\n📢 Join: {CHANNEL_USERNAME}",
            parse_mode='Markdown'
        )
        bot.delete_message(call.message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ **Sorry, I couldn't send the video. Try again later.**")

if __name__ == "__main__":
    bot.infinity_polling()
