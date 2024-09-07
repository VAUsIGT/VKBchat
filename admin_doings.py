#
# ФАЙЛ С АДМИНСКИМИ УТЕХАМИ
#





from libs import *
init()

class AdminRule(ABCRule[Message]):  # кастомное правило
    def __init__(self, admins: list):
        self.admins = admins
    async def check(self, event: Message):
        return event.from_id in self.admins


current_time = datetime.datetime.now().time()  # текущее время
logger.disable("vkbottle")  # логи отключены
bot=Bot(token=token) # токен из config
bot.labeler.custom_rules["is_admin"] = AdminRule
OPEN = open("KD.txt", "r") #счётчик всех диалогов
KD = int(OPEN.readline())
OPEN.close()
searching = []  # массив ищущих общения
talking = []  # массив разговаривающих
all_one = []  # все юзеры хоть раз искавшие за сегодня

# DA = 225589402
# EL = 747292616
@bot.on.private_message(is_admin = [191685935])  # админка
async def admin_exe(message: Message):
    print(Fore.LIGHTMAGENTA_EX + f"Админ: {str(message.from_id)} Сообщение: {str(message.text)}")  # логи
    if message.text.lower()[:8] == "написать":  # например: "написать 225589402 тралаЛА"
        pripiska = "[сообщение от админа]: "
        await bot.api.messages.send(peer_id=int(message.text[9:18]), message=pripiska+message.text[19:], random_id=getrandbits(64))
    elif message.text.lower() == "статистика":
        await message.answer(f"Ку, ищут: {len(searching)}, в диалоге: {len(talking)}.")
    elif message.text.lower()[:5] == "поиск":  # добавление юзера
        searching.append(int(message.text.lower()[6:15]))
        await message.answer(f"Пользователь {str(message.text.lower()[6:15])} добавлен.")
    elif message.text.lower()[:6] == "беседа":  # добавление юзера
        talking.append(int(message.text.lower()[7:16]))
        await message.answer(f"Пользователь {str(message.text.lower()[7:16])} добавлен.")
    elif message.text.lower() == "кто":  # выдаёт списки в поиске и диалоге
        await message.answer(f"в поиске: {searching} \nв диалоге: {talking}")
    elif message.text.lower() == "сохранить":  # сохраняет сегодняшних пользователей
        with open('all_users.txt') as OPEN:
            for line in OPEN:
                all_one.append(line)
            all_users = set(all_one)
        with open('all_users.txt', 'w') as OPEN:   #842584665 225589402
            for i in all_users:
                OPEN.writelines(str(i))
            await message.answer("Успешно")
    elif message.text.lower()[:8] == "рассылка":  # письмо всем пользователям
        with open('all_users.txt') as OPEN:
            for line in OPEN:
                try: await bot.api.messages.send(peer_id=int(line), message="🤖 Рассылка: "+message.text[8:], random_id=getrandbits(64))
                except: pass
    else:
        await message.answer(f"[админка] Команды: \n'статистика',\n'написать [id] [message]', \n'поиск [message]', \n'беседа [message]', \n'кто', \n'рассылка [message]', \n'сохранить'")

#сообщение админа для юзера
async def adm_mes(user_id,message):
    current_time = datetime.datetime.now().time()  # текущее время
    print(Fore.LIGHTRED_EX+f"ЖАЛОБА от [{user_id}]"+Style.RESET_ALL+f" [{str(current_time)[:8]}]")



