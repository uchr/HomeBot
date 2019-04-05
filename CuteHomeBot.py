from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging
import json
import vlc

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

with open("settings/botSettings.json", "r") as settings:
    botSettings = json.loads(settings.read())

with open("settings/seriesSettings.json", "r") as settings:
    seriesSettings = json.loads(settings.read())

class VLCPlayer:
    def play(self, path, name):
        self.player = vlc.MediaPlayer(path)
        self.name = name
        self.player.toggle_fullscreen()
        self.player.set_rate(1.3)
        self.player.play()
    
    def pause(self):
        self.player.pause()
    
    def stop(self):
        self.player.stop()

vlcPlayer = VLCPlayer()

def getListOfSeriesMessage():
    keyboard = []
    for i in range(len(seriesSettings["series"])):
        mark = "✅" if seriesSettings["series"][i]["watched"] else "❌"
        name = seriesSettings["series"][i]["name"]
        text = mark + name[name.find("S"):name.find("E")+3]
        keyboard.append([InlineKeyboardButton(text = text, callback_data=str(i))])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return {"text": "Choose a series:", "reply_markup": reply_markup}

def getPlayMessage():
    global vlcPlayer

    keyboard = [[InlineKeyboardButton(text = "⏸️ Pause", callback_data="Pause")],
                [InlineKeyboardButton(text = "⏹️ Stop", callback_data="Stop")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return {"text": vlcPlayer.name, "reply_markup": reply_markup}

def getPauseMessage():
    global vlcPlayer

    vlcPlayer.pause()
    keyboard = [[InlineKeyboardButton(text = "▶️ Play", callback_data="Play")],
                [InlineKeyboardButton(text = "⏹️ Stop", callback_data="Stop")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return {"text": vlcPlayer.name, "reply_markup": reply_markup}

def getSelectSeriesMessage():
    global vlcPlayer

    keyboard = [[InlineKeyboardButton(text = "⏸️ Pause", callback_data="Pause")],
                [InlineKeyboardButton(text = "⏹️ Stop", callback_data="Stop")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return {"text": vlcPlayer.name, "reply_markup": reply_markup}

def start(update, context):
    message = getListOfSeriesMessage()
    update.message.reply_text(message["text"], reply_markup=message["reply_markup"])

def button(update, context):
    global vlcPlayer

    query = update.callback_query
    if query.data == "Play":
        print("Play")
        vlcPlayer.pause()
        message = getPlayMessage()
        query.edit_message_text(message["text"], reply_markup=message["reply_markup"])

    elif query.data == "Pause":
        print("Pause")
        vlcPlayer.pause()
        message = getPauseMessage()
        query.edit_message_text(message["text"], reply_markup=message["reply_markup"])

    elif query.data == "Stop":
        vlcPlayer.stop()
        message = getListOfSeriesMessage()
        query.edit_message_text(message["text"], reply_markup=message["reply_markup"])

    else:
        seriesNumber = int(query.data)
        name = seriesSettings["series"][seriesNumber]["name"]
        messageName = name[:name.find("-") - 1] + " - " + name[name.find("(") + 1:name.find(")")]
        vlcPlayer.play(seriesSettings["path"] + "/" + name, messageName)

        seriesSettings["series"][seriesNumber]["watched"] = True
        with open('settings/seriesSettings.json', 'w') as settings:
            json.dump(seriesSettings, settings)

        message = getSelectSeriesMessage()

        query.edit_message_text(message["text"], reply_markup=message["reply_markup"])

def play(update, context):
    vlcPlayer.pause()
    message = getPlayMessage()
    update.message.reply_text(message["text"], reply_markup=message["reply_markup"])

def pause(update, context):
    vlcPlayer.pause()
    message = getPauseMessage()
    update.message.reply_text(message["text"], reply_markup=message["reply_markup"])

def stop(update, context):
    vlcPlayer.stop()
    message = getListOfSeriesMessage()
    update.message.reply_text(message["text"], reply_markup=message["reply_markup"])

def main():
    updater = Updater(token=botSettings["token"], use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('play', play))
    dp.add_handler(CommandHandler('pause', pause))
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
