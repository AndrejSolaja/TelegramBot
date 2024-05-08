import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import constants
import requests
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def download_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0]
    try:
        response = requests.get(url, stream=True)
        if response.ok:
            img_data = requests.get(url).content
            with open('images/' + url.split('/')[-1], 'wb') as handler:
                handler.write(img_data)
            await context.bot.send_photo(chat_id=update.effective_chat.id,
                                         photo=open('images/' + url.split('/')[-1], 'rb'))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Failed to download the media. Please make sure you provide a valid URL.")
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="An error occurred. Please try again later.")


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0]
    try:
        response = requests.get(url, stream=True)
        if response.ok:
            ydl_opts = {
                'outtmpl': 'videos/' + "%(id)s.%(ext)s",
                'format_sort': ['res:1080', 'ext:mp4:m4a']
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                vid_id = info.get('id', "placeholder")
                ext = info.get('ext', "placeholder")

            await context.bot.send_video(chat_id=update.effective_chat.id,
                                         video=open('videos/' + f"{vid_id}.{ext}", 'rb'))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Failed to download the media. Please make sure you provide a valid URL.")
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="An error occurred. Please try again later.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(constants.myToken).build()

    start_handler = CommandHandler('start', start)
    image_handler = CommandHandler('image', download_image)
    video_handler = CommandHandler('video', download_video)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(image_handler)
    application.add_handler(video_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
