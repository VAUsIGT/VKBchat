#
# ФАЙЛ С ОБРАБОТКОЙ СООБЩЕНИЙ
#



from libs import *
from admin_doings import adm_mes
init()

logger.disable("vkbottle")  # логи отключены
bot=Bot(token=token) # токен из config
OPEN = open("KD.txt", "r") #счётчик всех диалогов
KD = int(OPEN.readline())
OPEN.close()
searching = []  # массив ищущих общения
talking = []  # массив разговаривающих
all_one = []  # все юзеры хоть раз искавшие за сегодня
current_time = datetime.datetime.now().time()  # текущее время

# создаем текстовые файлы с айди собеседника
async def create_talk_file(user_id,send_txt_to_user_id):
    # файл нашедшего собеседника
    file = open(f"text/{user_id}.txt","w")
    file.write(send_txt_to_user_id)  # запись айди найденного
    file.close()
    # файл найденного собеседника
    file1 = open(f"text/{send_txt_to_user_id}.txt", "w")
    file1.write(user_id)  # запись айди нашедшего
    file1.close()
    # для отслеживания действий
    print(Fore.LIGHTGREEN_EX+f"[был создан файл диалога {user_id}]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")

# получение узер_айди собеседника
def get_talk_user_id(user_id):
    file = open(f"text/{user_id}.txt", "r")
    send_txt_to_user_id = file.readline()
    file.close()
    return int(send_txt_to_user_id)

# отправка сообщения собеседнику
async def send_msg_to(user_id,msg):
    # открываем файл автора сообщения
    file = open(f"text/{str(user_id)}.txt","r")
    to_send_user_id = file.readline()  # получаем айди собеседника
    # отправляем сообщение
    if msg.reply_message != None:
        msg.text = "\n\n>" + msg.reply_message.text[0:] + "\n👤: "+ msg.text
    elif (msg.fwd_messages != []):
        msg.text = "\n\n>" + msg.fwd_messages[0].text + "\n👤: " + msg.text
    else:
        msg.text ="👤: "+msg.text
    await bot.api.messages.send(peer_id=int(to_send_user_id), message=msg.text, random_id=getrandbits(64), keyboard=KEYBOARD_DIALOG)
    file.close()
@bot.on.private_message(attachment="audio_message")
async def audio_message_answer(message: Message):
    audio_uploader = VoiceMessageUploader (bot.api)
    #   проверка на наличие юзера в диалоге
    if str(message.from_id) in talking:
        # создание папки голосовых отправителя
        from pathlib import Path
        Path(f'data/audio_msg/{message.from_id}/').mkdir(parents=True, exist_ok=True)
        current_time = datetime.datetime.now().time()
        # получаем ссылку на голосовое
        url = message.attachments[0].audio_message.link_ogg
        # сохраняем голос
        urllib.request.urlretrieve(url,f"data/audio_msg/{str(message.from_id)}/{str(current_time).replace(':', '-')}.ogg")
        # отладка
        print(Fore.LIGHTGREEN_EX + f"[загружено голосовое]" + Style.RESET_ALL + f" [{str(current_time)[:8]}]")
        # загрузка голос в сообщения от бота
        audio = await audio_uploader.upload(
            file_source=f"data/audio_msg/{message.from_id}/{str(current_time).replace(':', '-')}.ogg",
            peer_id=message.peer_id,
            title=f"{str(current_time).replace(':', '-')}"
        )
        # отправка
        await bot.api.messages.send(peer_id=get_talk_user_id(message.from_id),
                                    attachment=audio,
                                    random_id=getrandbits(64))
        # уведомление отправителя об отправке голос
        await message.answer("🤖 Голосовое отправлено", keyboard=KEYBOARD_DIALOG)
    # ответ на отсутствие диалога
    else:
        await message.answer("🤖 Вы не в диалоге", keyboard=KEYBOARD_FIRST)

@bot.on.private_message(attachment="video")
async def video_message_answer(message: Message):
    await message.answer("Видео невозможно отправить")
    print("Пользователь отправил видео")

#-----------------------------------------------------------------
@bot.on.private_message(attachment="photo")
async def photo_answer(message: Message):
    #print(message.attachments)  # проверка настроек фото
    photo_uploader = PhotoMessageUploader(bot.api)
#   проверка на наличие юзера в диалоге
    if str(message.from_id) in talking:
        # создание папки фото отправителя
        from pathlib import Path
        Path(f'data/photo/{message.from_id}/').mkdir(parents=True, exist_ok=True)
        photo_cacha = []  # для отправки нескольких фото разом
        # проходим по вложениям
        for i in range(len(message.attachments)):
            current_time = datetime.datetime.now().time()
            # получаем ссылку на фото
            url = message.attachments[i].photo.sizes[len(message.attachments[i].photo.sizes)-1].url
            # сохраняем фото
            urllib.request.urlretrieve(url,f"data/photo/{str(message.from_id)}/{str(current_time).replace(':','-')}.png")
            # отладка
            print(Fore.LIGHTGREEN_EX + f"[загружено фото]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")
            # загрузка фото в сообщения от бота
            photo = await photo_uploader.upload(
                file_source=f"data/photo/{message.from_id}/{str(current_time).replace(':','-')}.png",
                peer_id=message.peer_id,
            )
            # добавляем в массив фото
            photo_cacha.append(photo)
        # отправка нескольких фото разом
        #await message.answer(attachment = photo_cacha)
        await bot.api.messages.send(peer_id=get_talk_user_id(message.from_id), attachment=photo_cacha, random_id=getrandbits(64))
        # уведомление отправителя об отправке фото
        await message.answer("🤖 Фото отправлено", keyboard=KEYBOARD_DIALOG)
    # ответ на отсутствие диалога
    else:
        await message.answer("🤖 Вы не в диалоге", keyboard=KEYBOARD_FIRST)

@bot.on.private_message(attachment="sticker") # обработка стикеров
async def sticker_answer(message: Message):
    #print(message.attachments)  # проверка настроек стикера
    photo_uploader = PhotoMessageUploader(bot.api)
    import urllib.request
    # проверка на наличие юзера в диалоге
    if str(message.from_id) in talking:
        # создание папки стикеров отправителя
        from pathlib import Path
        Path(f'data/stickers/{message.from_id}/').mkdir(parents=True, exist_ok=True)
        #print("папка")
        current_time = datetime.datetime.now().time()
        # получаем ссылку на стикер
        url = message.attachments[0].sticker.images[1].url
        #print(url)  # проверка данных url
        # сохраняем стикер
        urllib.request.urlretrieve(url,
                                   f"data/stickers/{str(message.from_id)}/{str(current_time).replace(':', '-')}.png")
        # отладка
        print(Fore.LIGHTBLUE_EX + f"[отправлен стикер {message.from_id}]" + Style.RESET_ALL + f" [{str(current_time)[:8]}]")
        # загрузка стикера в сообщения от бота
        sticker = await photo_uploader.upload(file_source=f"data/stickers/{message.from_id}/{str(current_time).replace(':', '-')}.png", peer_id=message.peer_id)
        await bot.api.messages.send(peer_id=get_talk_user_id(message.from_id), attachment=sticker, random_id=getrandbits(64))
    # ответ на отсутствие диалога
    else:
        await message.answer("🤖 Вы не в диалоге", keyboard=KEYBOARD_FIRST)

@bot.on.private_message()  # обрабатывает ВСЕ сообщения
async def text_msg(message: Message):  # асинхронная функция принимающая тип message
    global KD

    current_time = datetime.datetime.now().time()  # текущее время
    #print(message.attachments) #проверка настроек сообщения
# -----------проверка на наличие собеседника\диалога
    if str(message.from_id) in talking:
            # остановки диалога
        if message.text.lower() == "!выход" or message.text.lower() == "!стоп":
            OPEN = open("KD.txt", "w")  # сохраняем в файл кол-ва диалогов
            KD += 1
            OPEN.write(str(KD))
            OPEN.close()
            # останавливаем у автора !стоп
            await message.answer(f"🤖 Диалог №{KD} остановлен. 😞\nЧтобы начать новый, напишите !поиск или !п", keyboard=KEYBOARD_FIRST)
            talking.pop(talking.index(str(message.from_id)))
            # останавливаем диалог у собеседника
            await bot.api.messages.send(peer_id=int(get_talk_user_id(message.from_id)), message=f"🤖 Собеседник прекратил диалог №{KD} 😞\nЧтобы начать новый, напишите !поиск или !п", random_id=getrandbits(64),keyboard=KEYBOARD_FIRST)
            talking.pop(talking.index(str(get_talk_user_id(message.from_id))))
            # для отслеживания действий
            print(Fore.LIGHTRED_EX + f"[пользователь {message.from_id} прекратил диалог {KD}]" + Style.RESET_ALL+f" [{str(current_time)[:8]}]")
#       попытка выйти в поиск во время диалога
        elif message.text.lower() == "!поиск":
             await message.answer("🤖 Вы в диалоге, поэтому поиск не возможен", keyboard=KEYBOARD_DIALOG)
             # обработка жалоб в диалоге
        elif message.text == "!админ" or message.text == "!жалоба":
            await message.answer("🤖 Номер этого диалога отправлен админам", keyboard=KEYBOARD_DIALOG)
            await adm_mes(message.from_id, message.text)
#       обработка ввода неправильной команды во время диалога
        elif str(message.text).startswith('!'):
            await message.answer("🤖 Неизвестная команда", keyboard=KEYBOARD_DIALOG)
#       отправка сообщения собеседнику
        else:
            # для отслеживания действий
            print(Fore.LIGHTCYAN_EX+f"[сообщение в диалоге {message.from_id}]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")
            # отправка сообщения собеседнику
            await send_msg_to(message.from_id, message)
# -----------поиск собеседника после команды !поиск
    elif message.text.lower() == "!поиск" or message.text.lower() == "!п":
        f = await bot.api.groups.is_member("anon_chat_bt",message.from_id)
        if f:
            await message.answer("Подпишитесь на группу или НАСЛАЖДАЙСЯ ЭТИМ СООБЩЕНИЕМ!")
        all_one.append(str(message.from_id)+"\n")  # добавление в список юзеров за запуск
#       проверка наличия в поиске
        if message.from_id not in searching:
            await message.answer(f"🤖 Мы ищем собеседника для вас!\nАктивных диалогов: {len(talking)//2}", keyboard=KEYBOARD_SEARCH) #ответ
            # для отслеживания действий
            print(Fore.LIGHTYELLOW_EX + f"[пользователем {message.from_id} инициализирован поиск]" + Style.RESET_ALL + f" [{str(current_time)[:8]}]")
        #   если есть ищущий собеседника
            if len(searching) > 0:
                # для отслеживания действий
                print(Fore.LIGHTGREEN_EX+f"[пользователем {message.from_id} создан диалог {KD}]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")
                # создаем файл с айди собеседников
                await create_talk_file(str(message.from_id), str(searching[0]))
                # перемещаем из ищущих в разговаривающих
                talking.append(str(searching[0]))
                talking.append(str(message.from_id))
                try:  # всё хорошо, создаёт диалог
                    # уведомление первого о нахождении собеседника
                    await bot.api.messages.send(peer_id=searching[0], message="🤖 Собеседник найден.\nОбщайтесь! :)\n!стоп — остановить диалог", random_id=getrandbits(64), keyboard=KEYBOARD_DIALOG)
                    # убираем ищущего из массива
                    searching.pop(0)
                    # уведомление второго о собеседнике
                    await message.answer("🤖 Собеседник найден.\nОбщайтесь! :)\n!стоп — остановить диалог", keyboard=KEYBOARD_DIALOG)
                except:  # защита, если 1 пользователь заблочит бота
                    await message.answer("🤖 Мы нашли вам собеседника, но он запретил боту отправку сообщений. Вновь добавили вас в очередь.", keyboard=KEYBOARD_DIALOG)
                    print(Fore.LIGHTRED_EX + f"[пользователь {str(searching[0])} заблокировал бота в поиске]" + Style.RESET_ALL + f" [{str(current_time)[:8]}]")
                    searching.pop(0)
                    talking.pop(talking.index(str(message.from_id)))
                    talking.pop(talking.index(str(get_talk_user_id(message.from_id))))
                    searching.append(message.from_id)
                    print(Fore.LIGHTRED_EX + "[ошибка пропущена]" + Style.RESET_ALL + f" [{str(current_time)[:8]}]")
        #   если ищущих нет, то добавляем в массив ищущих
            else:
                searching.append(message.from_id)
#       если человек в поиске
        else:
            await message.answer("🤖 Вы уже в поиске", keyboard=KEYBOARD_SEARCH)
#   выход из поиска собеседника
    elif (message.text == "!стоп" or message.text == "!с") and message.from_id in searching:
        searching.pop(searching.index(message.from_id))
        await message.answer("🤖 Вы прекратили поиск", keyboard=KEYBOARD_FIRST)
        print(Fore.LIGHTYELLOW_EX + f"[пользователь вышел из поиска]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")
#   репорт в диалоге
    elif message.text == "!админ" or message.text == "!жалоба":
        await message.answer("🤖 Номер вашего последнего диалога отправлен админам", keyboard=KEYBOARD_FIRST)
        await adm_mes(message.from_id, message.text)

#   обработка левых сообщений:
    else:
#       во время поиска
        if message.from_id in searching:
            await message.answer("🤖 Вы находитесь в очереди, пожалуйста подождите", keyboard=KEYBOARD_SEARCH)
#       не во время поиска
        else:
            await message.answer("🤖 Чтобы найти собеседника, нажмите на соответствующую кнопку.\n Либо напишите !поиск или !п", keyboard=KEYBOARD_FIRST)  # эхо
        print(Fore.LIGHTBLUE_EX + f"Пользователь:  {str(message.from_id)} Сообщение: {str(message.text)}"+Style.RESET_ALL + f" [{str(current_time)[:8]}]")    # логи
        # await bot.api.messages.send(peer_id=225589402, message=message.text,random_id=getrandbits(64))
