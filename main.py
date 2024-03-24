from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from config import token
from loguru import logger
from colorama import init
from random import getrandbits
init()
from colorama import Fore, Back, Style

class AdminRule(ABCRule[Message]): #кастомное правило
    def __init__(self, admins: list):
        self.admins = admins
    async def check(self, event: Message):
        return event.from_id in self.admins

logger.disable("vkbottle") #логи отключены
bot=Bot(token=token) #токен из config
bot.labeler.custom_rules["is_admin"] = AdminRule

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


# DA = 225589402
# VY = 747292616
@bot.on.private_message(is_admin=[])  # 747292616]) #админка
async def admin_exe(message: Message):
    await message.answer(f"Админ написал:\n{message.text}")
    print(Fore.LIGHTMAGENTA_EX + f"Админ: {str(message.from_id)} Сообщение: {str(message.text)}")  # логи


searching = []  # массив ищущих общения
talking = []  # массив разговаривающих

# создаем текстовые файлы с айди собеседника
async def create_talk_file(user_id, send_txt_to_user_id):
    # файл нашедшего собеседника
    file = open(f"text/{user_id}.txt", "w")
    file.write(send_txt_to_user_id)  # запись айди найденного
    file.close()
    # файл найденного собеседника
    file1 = open(f"text/{send_txt_to_user_id}.txt", "w")
    file1.write(user_id)  # запись айди нашедшего
    file1.close()
    # для отслеживания действий
    #print("file created")


# отправка сообщения собеседнику
async def send_msg_to(user_id, msg):
    # открываем файл автора сообщения
    file = open(f"text/{str(user_id)}.txt", "r")
    to_send_user_id = file.readline()  # получаем айди собеседника
    # отправляем сообщение
    await bot.api.messages.send(peer_id=int(to_send_user_id), message=msg, random_id=getrandbits(64))
    # бета\not ready -> запись диалога в текстовый файл
    # file.write(f"send: {str(msg)}")
    file.close()


@bot.on.private_message()  # обрабатывает ВСЕ сообщения
async def main(message: Message):  # ассинхронная функция принимающая тип message
    if message.text.lower() == "!поиск":
        await message.answer("Вы добавлены в очередь!")  # ответ
        # для отслеживания действий
        print(f"[пользователем инициализирован поиск]")
        # если есть ищущий собеседника
        if (len(searching) >= 1):
            print("[создан диалог]") # для отслеживания действий
            try:
                await create_talk_file(str(message.from_id), str(searching[0]))# создаем файл с айди собеседников
                talking.append(str(searching[0]))# перемещаем из ищущих в разговаривающих
                talking.append(str(message.from_id))
                await bot.api.messages.send(peer_id=searching[0], message="Собеседник найден!", random_id=getrandbits(64))# уведомление первого о нахождении собеседника
                searching.pop(0)# убираем ищущего из массива
                await message.answer("Собеседник найден!")# уведомление второго о собеседнике
                print(Fore.LIGHTGREEN_EX+"file has been created"+Style.RESET_ALL)
            except:
                print(Fore.LIGHTRED_EX+"file not created"+Style.RESET_ALL)
        elif message.text.lower() == "!стоп":
            searching.pop(0)  # убираем ищущего из массива
            await message.answer("Поиск прекращён")
        else:
            searching.append(message.from_id)# если ищущих нет, то добавляем в массив ищущих
            #print(searching, talking)

    # проверка на наличие в разговаривающих
    elif (str(message.from_id) in talking):
        # для отслеживания действий
        print("[сообщение в диалоге]")
        # отправка сообщения собеседнику
        await send_msg_to(message.from_id, message.text)

    # ---------------------------------------------
    else:
        await message.answer("Чтобы найти собеседника, напишите !поиск")  # эхо
        print(Fore.LIGHTBLUE_EX + f"Пользователь:  {str(message.from_id)} Сообщение: {str(message.text)}" + Style.RESET_ALL)  # логи
        #await bot.api.messages.send(peer_id=747292616, message=message.text,random_id=getrandbits(64))

print(Fore.YELLOW + "-------------------Бот запущен-------------------" + Style.RESET_ALL)
bot.run_forever()