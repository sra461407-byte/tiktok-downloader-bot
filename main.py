import telebot
import requests

API_TOKEN = '8643345893:AAEG8UNOaOUYTslLV8oAkjMQTNoEWoOlVQY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ሰላም! የቲክቶክ ቪዲዮ ሊንክ ላኩልኝ፣ ያለምንም watermark አውርጄ እልክላችኋለሁ።")

@bot.message_handler(func=lambda message: 'tiktok.com' in message.text)
def handle_tiktok(message):
    url = message.text
    bot.reply_to(message, "በመካሄድ ላይ ነው... እባክዎ ትንሽ ይጠብቁ")
    
    try:
        response = requests.get(f"https://www.tikwm.com/api/?url={url}").json()
        video_url = response['data']['play']
        bot.send_video(message.chat.id, video_url, caption="በ @የአንተ_ቻናል_ስም የተዘጋጀ")
    except Exception as e:
        bot.reply_to(message, "ይቅርታ፣ ቪዲዮውን ማግኘት አልቻልኩም። ሊንኩ ትክክል መሆኑን ያረጋግጡ።")

if __name__ == "__main__":
    bot.infinity_polling()
