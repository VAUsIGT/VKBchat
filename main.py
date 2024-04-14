#
# ФАЙЛ С БИБЛИОТЕКАМИ -> libs.py
# ФАЙЛ С АДМИНСКИМИ УТЕХАМИ -> admin_doings.py
# ФАЙЛ С ОБРАБОТКОЙ СООБЩЕНИЙ -> msg_reaction.py
#

from msg_reaction import *
from admin_doings import *

#приложения к сообщению
@bot.on.private_message(attachment="audio_message")
async def audio_message(message: Message):
    await audio_message_answer(message)
@bot.on.private_message(attachment="video")
async def video(message: Message):
    await video_message_answer(message)
@bot.on.private_message(attachment="sticker")
async def sticker(message: Message):
    await sticker_answer(message)
@bot.on.private_message(attachment="photo")
async def photo(message: Message):
    await photo_answer(message)
#текст
@bot.on.private_message()
async def text(message: Message):
    await text_msg(message)
#админские утехи
@bot.on.private_message(is_admin = [191685935])  # админка
async def admin(message: Message):
    admin_exe(message)

#вывод в консоль
current_time = datetime.datetime.now().time()  # текущее время
print(Fore.YELLOW + f"-------------------Бот запущен в {str(current_time)[:8]}-------------------")
bot.run_forever()
