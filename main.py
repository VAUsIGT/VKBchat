from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle.api import API
from config import token
from loguru import logger
from colorama import init
from random import getrandbits
init()
from colorama import Fore, Back, Style
#для своего бота
api = API(token)

class AdminRule(ABCRule[Message]): #кастомное правило
    def __init__(self, admins: list):
        self.admins = admins
    async def check(self, event: Message):
        return event.from_id in self.admins

logger.disable("vkbottle") #логи отключены
bot=Bot(api=api) #токен из config
bot.labeler.custom_rules["is_admin"] = AdminRule



async def text_to_file(user_id, msg):
    file = open(f"text/{user_id}.txt","a")
    file.write(msg+"\n")
    file.close()

    print("текст записан")

@bot.on.private_message(attachment="photo") #   НЕ РАБОТАЕТ
async def photo_answer(message: Message):
    await message.answer("Фото отправлено")
    from pathlib import Path
    Path(f'data/photo/{message.from_id}/').mkdir(parents=True, exist_ok=True)
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'data/photo/{message.chat.id}/' + file_info.file_path.replace('data/photo/', '')
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

#DA = 225589402
#VY = 747292616
@bot.on.private_message(is_admin=[])#747292616]) #админка
async def admin_exe(message: Message):
    await message.answer(f"Админ написал:\n{message.text}")
    print(Fore.LIGHTMAGENTA_EX + f"Админ: {str(message.from_id)} Сообщение: {str(message.text)}")  # логи

searching = [] #массив ищущих общения
talking = [] #массив разговаривающих

#создаем текстовые файлы с айди собеседника
async def create_talk_file(user_id,send_txt_to_user_id):
    #файл нашедшего собеседника
    file = open(f"text/{user_id}.txt","w")
    file.write(send_txt_to_user_id) #запись айди найденного
    file.close()
    #файл найденного собеседника
    file1 = open(f"text/{send_txt_to_user_id}.txt", "w")
    file1.write(user_id) #запись айди нашедшего
    file1.close()
    #для отслеживания действий
    print(Fore.LIGHTGREEN_EX+"file has been created"+Style.RESET_ALL)

#получение узер_айди собеседника
def get_talk_user_id(user_id):
    file = open(f"text/{user_id}.txt", "r")
    send_txt_to_user_id = file.readline()
    file.close()
    return int(send_txt_to_user_id)

#отправка сообщения собеседнику
async def send_msg_to(user_id,msg):
    #открываем файл автора сообщения
    file = open(f"text/{str(user_id)}.txt","r")
    to_send_user_id = file.readline() #получаем айди собеседника
    #отправляем сообщение
    await bot.api.messages.send(peer_id=int(to_send_user_id), message=msg, random_id=getrandbits(64))
    #бета\not ready -> запись диалога в текстовый файл
    #file.write(f"send: {str(msg)}")
    file.close()


@bot.on.private_message() #обрабатывает ВСЕ сообщения
async def main(message: Message): #ассинхронная функция принимающая тип message
#-----------проверка на наличие собеседника\диалога
    if(str(message.from_id) in talking):
#       остановки диалога
        if(message.text.lower()=="!выход" or message.text.lower()=="!стоп"):
            #останавливаем у автора !стоп
            await message.answer("Диалог прекращен")
            talking.pop(talking.index(str(message.from_id)))
            #останавливаем диалог у собеседника
            await bot.api.messages.send(peer_id=int(get_talk_user_id(message.from_id)), message="Собеседник прекратил диалог", random_id=getrandbits(64))
            talking.pop(talking.index(str(get_talk_user_id(message.from_id))))
            # для отслеживания действий
            print(Fore.LIGHTRED_EX + "[пользователь прекратил диалог]" + Style.RESET_ALL)
#       попытка выйти в поиск во время диалога
        elif(message.text.lower() == "!поиск"):
             await message.answer("Вы в диалоге, поэтому поиск не возможен")
#       обработка ввода неправильной команды во время диалога
        elif(str(message.text).startswith('!')):
            await message.answer("Неизвестная команда")
#       отправка сообщения собеседнику
        else:
            # для отслеживания действий
            print(Fore.LIGHTCYAN_EX+"[сообщение в диалоге]"+Style.RESET_ALL)
            # отправка сообщения собеседнику
            await send_msg_to(message.from_id, message.text)
#-----------поиск собеседника после команды !поиск
    elif message.text.lower()=="!поиск":
#       проверка наличия в поиске
        if(message.from_id not in searching):
            await message.answer("Мы ищем собеседника для вас!") #ответ
            #для отслеживания действий
            print(Fore.LIGHTYELLOW_EX +"[пользователем инициализирован поиск]"+Style.RESET_ALL)
        #   если есть ищущий собеседника
            if(len(searching) > 0 ):
                # для отслеживания действий
                print(Fore.LIGHTGREEN_EX+"[создан диалог]"+Style.RESET_ALL)
                #создаем файл с айди собеседников
                await create_talk_file(str(message.from_id), str(searching[0]))
                #перемещаем из ищущих в разговаривающих
                talking.append(str(searching[0]))
                talking.append(str(message.from_id))
                #уведомление первого о нахождении собеседника
                await bot.api.messages.send(peer_id=searching[0], message="Собеседник найден!", random_id=getrandbits(64))
                #убираем ищущего из массива
                searching.pop(0)
                #уведомление второго о собеседнике
                await message.answer("Собеседник найден!")
        #   если ищущих нет, то добавляем в массив ищущих
            else:
                searching.append(message.from_id)
#       если человек в поиске
        else:
            await message.answer("Вы уже в поиске")
#-----------выход из поиска собеседника
    elif(message.text == "!стоп" and message.from_id in searching):
        searching.pop(searching.index(message.from_id))
        await message.answer("Вы прекратили поиск")
        print(Fore.LIGHTYELLOW_EX + "[пользователь вышел из поиска]"+Style.RESET_ALL)


#-----------обработка левых сообщений:
    else:
#       во время поиска
        if(message.from_id in searching):
            await message.answer("Подождите")
#       не во время поиска
        else:
            await message.answer("Чтобы найти собеседника, нажмите на соответствующую кнопку.\n Или напишите !поиск")  # эхо
        print(Fore.LIGHTBLUE_EX +f"Пользователь:  {str(message.from_id)} Сообщение: {str(message.text)}"+Style.RESET_ALL)    #логи
        #await bot.api.messages.send(peer_id=225589402, message=message.text,random_id=getrandbits(64))


print(Fore.YELLOW +"-------------------Бот запущен-------------------"+Style.RESET_ALL )
bot.run_forever()