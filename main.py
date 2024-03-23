from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from config import token
from loguru import logger
from colorama import init
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

@bot.on.private_message(is_admin=[])#747292616]) #админка
async def admin_exe(message: Message):
    await message.answer(f"Админ написал:\n{message.text}")
    print(Fore.LIGHTMAGENTA_EX + f"Админ: {str(message.from_id)} Сообщение: {str(message.text)}")  # логи

@bot.on.private_message() #обрабатывает ВСЕ сообщения
async def main(message: Message): #ассинхронная функция принимающая тип message

    if message.text.lower()=="!поиск":
        await message.answer("Мы ищем собеседника для вас!\nВаш собеседник найден!\nМожете общаться!") #ответ

    else:
        await message.answer("Чтобы найти собеседника, нажмите на соответствующую кнопку.\n Или напишите !поиск")  # эхо
        print(Fore.LIGHTBLUE_EX +f"Пользователь:  {str(message.from_id)} Сообщение: {str(message.text)}")    #логи


print(Fore.YELLOW +"-------------------Бот запущен-------------------", )
bot.run_forever()