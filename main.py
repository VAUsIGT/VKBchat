from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle import PhotoMessageUploader
from keyb import KEYBOARD_SEARCH,KEYBOARD_FIRST, KEYBOARD_DIALOG
from config import token
from loguru import logger
from colorama import init
from random import getrandbits
init()
from colorama import Fore, Back, Style
import datetime
class AdminRule(ABCRule[Message]):  # кастомное правило
    def __init__(self, admins: list):
        self.admins = admins
    async def check(self, event: Message):
        return event.from_id in self.admins

logger.disable("vkbottle")  # логи отключены
bot=Bot(token=token) # токен из config
bot.labeler.custom_rules["is_admin"] = AdminRule

async def text_to_file(user_id, msg):
    file = open(f"text/{user_id}.txt","a")
    file.write(msg+"\n")
    file.close()
    print("[текст записан]")

#@bot.on.private_message() #   НЕ РАБОТАЕТ
#async def

# DA = 225589402
# VY = 747292616
@bot.on.private_message(is_admin = [])  # админка
async def admin_exe(message: Message):
    await message.answer(f"🤖 Админ написал:\n{message.text}")
    print(Fore.LIGHTMAGENTA_EX + f"Админ: {str(message.from_id)} Сообщение: {str(message.text)}")  # логи

searching = []  # массив ищущих общения
talking = []  # массив разговаривающих

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
    print(Fore.LIGHTGREEN_EX+"был создан файл"+Style.RESET_ALL)

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
    await bot.api.messages.send(peer_id=int(to_send_user_id), message=msg, random_id=getrandbits(64), keyboard=KEYBOARD_DIALOG)
    # бета\not ready -> запись диалога в текстовый файл
    # file.write(f"send: {str(msg)}")
    file.close()

async def adm_mes(user_id,message):
    current_time = datetime.datetime.now().time()  # текущее время
    print(Fore.LIGHTRED_EX+f"ЖАЛОБА от [{user_id}]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")

@bot.on.private_message()  # обрабатывает ВСЕ сообщения
async def main(message: Message):  # ассинхронная функция принимающая тип message
    current_time = datetime.datetime.now().time()  # текущее время
# -----------проверка на наличие собеседника\диалога
    if str(message.from_id) in talking:
            # остановки диалога
        if message.text.lower() == "!выход" or message.text.lower() == "!стоп":
            # останавливаем у автора !стоп
            await message.answer("🤖 Диалог остановлен. 😞\nЧтобы начать новый, напишите !поиск или !п", keyboard=KEYBOARD_FIRST)
            talking.pop(talking.index(str(message.from_id)))
            # останавливаем диалог у собеседника
            await bot.api.messages.send(peer_id=int(get_talk_user_id(message.from_id)), message="🤖 Собеседник прекратил диалог😞\nЧтобы начать новый, напишите !поиск или !п", random_id=getrandbits(64),keyboard=KEYBOARD_FIRST)
            talking.pop(talking.index(str(get_talk_user_id(message.from_id))))
            # для отслеживания действий
            print(Fore.LIGHTRED_EX + "[пользователь прекратил диалог]" + Style.RESET_ALL+f" [{str(current_time)[:8]}]")
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
            print(Fore.LIGHTCYAN_EX+"[сообщение в диалоге]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")
            # отправка сообщения собеседнику
            await send_msg_to(message.from_id, message.text)
# -----------поиск собеседника после команды !поиск
    elif message.text.lower() == "!поиск" or message.text.lower() == "!п":
#       проверка наличия в поиске
        if message.from_id not in searching:
            await message.answer(f"🤖 Мы ищем собеседника для вас!\nАктивных диалогов: {len(talking)}",keyboard=KEYBOARD_SEARCH) #ответ
            # для отслеживания действий
            print(Fore.LIGHTYELLOW_EX + "[пользователем инициализирован поиск]" + Style.RESET_ALL + f" [{str(current_time)[:8]}]")
        #   если есть ищущий собеседника
            if len(searching) > 0 :
                # для отслеживания действий
                print(Fore.LIGHTGREEN_EX+"[создан диалог]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")
                # создаем файл с айди собеседников
                await create_talk_file(str(message.from_id), str(searching[0]))
                # перемещаем из ищущих в разговаривающих
                talking.append(str(searching[0]))
                talking.append(str(message.from_id))
                # уведомление первого о нахождении собеседника
                await bot.api.messages.send(peer_id=searching[0], message="🤖 Собеседник найден.\nОбщайтесь! :)\n!стоп — остановить диалог", random_id=getrandbits(64), keyboard=KEYBOARD_DIALOG)
                # убираем ищущего из массива
                searching.pop(0)
                # уведомление второго о собеседнике
                await message.answer("🤖 Собеседник найден.\nОбщайтесь! :)\n!стоп — остановить диалог",keyboard=KEYBOARD_DIALOG)
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
        await adm_mes(message.from_id,message.text)

#   обработка левых сообщений:
    else:
#       во время поиска
        if message.from_id in searching:
            await message.answer("🤖 Подождите", keyboard=KEYBOARD_SEARCH)
#       не во время поиска
        else:
            await message.answer("🤖 Чтобы найти собеседника, нажмите на соответствующую кнопку.\n Либо напишите !поиск или !п", keyboard=KEYBOARD_FIRST)  # эхо
        print(Fore.LIGHTBLUE_EX + f"Пользователь:  {str(message.from_id)} Сообщение: {str(message.text)}"+Style.RESET_ALL + f" [{str(current_time)[:8]}]")    # логи
        # await bot.api.messages.send(peer_id=225589402, message=message.text,random_id=getrandbits(64))

current_time = datetime.datetime.now().time()  # текущее время
print(Fore.YELLOW + f"-------------------Бот запущен в {str(current_time)[:8]}-------------------")
bot.run_forever()
