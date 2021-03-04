from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from io import BytesIO
import datetime, random, requests, json

from opener import getIcons, getUsers, saveUsers

from api.config import botToken

class ChurchStuff:
    def __init__(self):
        self.icon = None
        self.pray = None

    def updateUsername(self, user_id=None, username=None):
        users = getUsers()
        users[user_id]['username'] = username
        saveUsers(users)

    def addCandle(self, to_user=None):
        users = getUsers()
        user_id = None

        for id in list(users.keys()):
            if users[id]['username'] == to_user:
                user_id = id
                break

        if user_id != None:
            users[user_id]['candles']+=1
            saveUsers(users)
            return True

        return False

    def newUser(self, user_id=None, username=None):
        users = getUsers()

        users[user_id] = {'username': username, 'candles': 0, 'parents': {'mother': None, 'father': None}, 'children': []}

        saveUsers(users)

        return True
    

    def getPray(self):
        time = datetime.datetime.now().hour+3

        try:
            self.pray =  open(f'resourses/night-pray{random.randint(1,9)}.ogg', 'rb') if time in [22,23,24,1,2,3] else open(f'resourses/pray{random.randint(1,34)}.ogg', 'rb')
            return True
        except:
            return False

    def getIcon(self):
        icons = getIcons()
        try:
            self.icon = BytesIO(requests.get(icons[str(random.randint(1,74))]).content)
            return True
        except:
            return False

    def setParent(self, mother=None, father=None, user_id=None):
        if mother != None:
            users = getUsers()
            
            mother_id = None

            for id in list(users.keys()):
                if users[id]['username'] == mother:
                    mother_id = id
                    break

            if mother_id in users.keys():
                users[user_id]['parents']['mother'] = mother_id
                users[mother_id]['children'].append(user_id)
                saveUsers(users)
            else:
                return False

            return True

        if father != None:
            users = getUsers()
            
            father_id = None

            for id in list(users.keys()):
                if users[id]['username'] == father:
                    father_id = id
                    break

            if father_id in users.keys():
                users[user_id]['parents']['father'] = father_id
                users[father_id]['children'].append(user_id)
                saveUsers(users)
            else:
                return False

            return True

churchBot = Bot(token=botToken)
dp = Dispatcher(churchBot, storage=MemoryStorage())

cancelInline = types.InlineKeyboardMarkup()
cancelInlineButton1 = types.InlineKeyboardButton("Отменить", callback_data="cancel")
cancelInline.add(cancelInlineButton1)

mainMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

mainMenuButton0 = types.KeyboardButton("Моя информация")
mainMenuButton1 = types.KeyboardButton("Выбрать крёстного")
mainMenuButton2 = types.KeyboardButton("Выбрать крёстную")
mainMenuButton3 = types.KeyboardButton(emojize("Поставить свечку :candle:"))
mainMenuButton4 = types.KeyboardButton(emojize("Приложиться к иконе :pray:"))
mainMenuButton5 = types.KeyboardButton("Послушать молитву")
mainMenuButton6 = types.KeyboardButton("Исповедаться в грехах")
mainMenu.add(mainMenuButton0).add(mainMenuButton1, mainMenuButton2).add(mainMenuButton3).add(mainMenuButton4).add(mainMenuButton5).add(mainMenuButton6)

class Candle(StatesGroup):
    waiting_for_username = State()

class Sins(StatesGroup):
    waiting_for_sin = State()

class Father(StatesGroup):
    waiting_for_father = State()

class Mother(StatesGroup):
    waiting_for_mother = State()

STICKERS = ['CAACAgIAAxkBAAEBTMhfVASIM3dkm7H4Uc3fOiHIVerrpAACPAADriBoF2CridLuNMdlGwQ','CAACAgIAAxkBAAEBS6VfUrcEBgelsMbCe2ksOBPyIpdxbgACOwADriBoF1tQ5OMSWIh-GwQ', 'CAACAgIAAxkBAAEBTMpfVAaNtlrco4_wv0uafGWRPOacEQACPQADriBoF7NPgsefhA5CGwQ']

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id, username = str(message['from']['id']), message['from']['username']
    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)

    if user_id not in users.keys():
        churchOptions.newUser(user_id=user_id,username=username)
        await message.reply(f'Добро пожаловать в Карманную Церковь, @{username}!', reply_markup=mainMenu)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)
        await message.reply(f'@{username}, ты уже состоишь в Церкви!', reply_markup=mainMenu)

@dp.callback_query_handler(lambda c: c.data and c.data == "cancel", state='*')
async def results(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_id, username = str(callback_query.message['chat']['id']), callback_query.message['chat']['username']

    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)

    await churchBot.send_message(user_id, "Чего желаете?", reply_markup=mainMenu)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Mother.waiting_for_mother)
async def mother(message: types.Message, state: FSMContext):
    await state.finish()
    
    user_id, username = str(message['from']['id']), message['from']['username']

    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)

    if message['text'][0] == '@':
        text = message['text'][1:]
    else: text = message['text']

    if text in ['Моя информация', 'Выбрать крёстного', 'Выбрать крёстную', emojize("Поставить свечку :candle:"), emojize("Приложиться к иконе :pray:"), 'Послушать молитву', 'Исповедаться в грехах']:
        await message.reply("Чего желаете?", reply_markup=mainMenu)
        return

    churchOptions = ChurchStuff()
    result = churchOptions.setParent(mother=text, user_id=user_id)

    if result:
        await message.reply(f"@{text} теперь твоя крёстная мать. Поздравляем!", reply_markup=mainMenu)
    else:
        await message.reply(f'@{text} - в церковнных записях нет такой верующей...', reply_markup=mainMenu)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Sins.waiting_for_sin)
async def sins(message: types.Message, state: FSMContext):
    await state.finish()

    user_id, username = str(message['from']['id']), message['from']['username']

    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)

    await message.reply(emojize(f"Я прощаю @{message['from']['username']}, вся согрешения твоя: властию Моей, прощаю и разрешаю тя от всех грехов твоих, во Имя Меня, и моего Сына, и Святаго Духа. Аминь. а теперь приложись к этому кресту :relieved:"))
    await churchBot.send_sticker(message['from']['id'], 'CAACAgIAAxkBAAEBTVZfVNhjWLHhlVdGfu0tz4Fy_T9QpgACPwADriBoF7g-XaOOmZLzGwQ', reply_markup=mainMenu)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Candle.waiting_for_username)
async def candle(message: types.Message, state: FSMContext):
    await state.finish()

    user_id, username = str(message['from']['id']), message['from']['username']

    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)

    if message['text'][0] == '@':
        text = message['text'][1:]
    else: text = message['text']

    if text in ['Моя информация', 'Выбрать крёстного', 'Выбрать крёстную', emojize("Поставить свечку :candle:"), emojize("Приложиться к иконе :pray:"), 'Послушать молитву', 'Исповедаться в грехах']:
        await message.reply("Чего желаете?", reply_markup=mainMenu)
        return

    churchOptions = ChurchStuff()
    result = churchOptions.addCandle(to_user=text)

    if result:
        await churchBot.send_sticker(user_id, STICKERS[random.randint(0,len(STICKERS)-1)])
        await message.reply(f"Свечка была поставлена для @{text}", reply_markup=mainMenu)
    else:
        await message.reply(f"@{text} не числиться в наших архивах...", reply_markup=mainMenu)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Father.waiting_for_father)
async def father(message: types.Message, state: FSMContext):
    await state.finish()
    
    user_id, username = str(message['from']['id']), message['from']['username']

    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)

    if message['text'][0] == '@':
        text = message['text'][1:]
    else: text = message['text']

    if text in ['Моя информация', 'Выбрать крёстного', 'Выбрать крёстную', emojize("Поставить свечку :candle:"), emojize("Приложиться к иконе :pray:"), 'Послушать молитву', 'Исповедаться в грехах']:
        await message.reply("Чего желаете?", reply_markup=mainMenu)
        return

    churchOptions = ChurchStuff()
    result = churchOptions.setParent(father=text, user_id=user_id)

    if result:
        await message.reply(f"@{text} теперь твой крёстный отец. Поздравляем!", reply_markup=mainMenu)
    else:
        await message.reply(f'@{text} - в церковнных записях нет такого верующего...', reply_markup=mainMenu)

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def main(message: types.Message):
    user_id, username, text = str(message['from']['id']), message['from']['username'], message['text']
    
    users = getUsers()

    churchOptions = ChurchStuff()
    if user_id not in list(users.keys()):
        churchOptions.newUser(user_id=user_id,username=username)
    else:
        churchOptions.updateUsername(user_id=user_id,username=username)
    
    if text == 'Моя информация':
        users = getUsers()
        await message.answer(emojize(f"За меня поставлено {users[user_id]['candles']} :candle:."))
        if users[user_id]['parents']['mother'] == None or users[user_id]['parents']['father'] == None:
            await message.answer("Ты пока не выбрал своих родителей...", reply_markup=mainMenu)
        else:
            await message.answer(f"Мои крёстные родители - @{users[users[user_id]['parents']['mother']]['username']} и @{users[users[user_id]['parents']['father']]['username']}")
        if users[user_id]['children'] == []:
            await message.answer("Пока я не являюсь ни чьим родителем...", reply_markup=mainMenu)
        else:
            await message.answer(f"А также я родитель {', '.join(['@'+users[i]['username'] for i in users[user_id]['children']])}", reply_markup=mainMenu)
    if text == "Выбрать крёстного":
        await message.reply("Как зовут твоего крёстного (проверь, чтобы он состоял в Церкви)?", reply_markup=cancelInline)
        await Father.waiting_for_father.set()
    if text == "Выбрать крёстную":
        await message.reply("Как зовут твою крёстную (проверь, чтобы она состояла в Церкви)?", reply_markup=cancelInline)
        await Mother.waiting_for_mother.set()
    if text == emojize("Поставить свечку :candle:"):
        users = getUsers()
        await message.reply("А кому мы ставим свечку (проверь, чтобы он(а) состоял(а) в Церкви)?", reply_markup=cancelInline)
        await Candle.waiting_for_username.set()
    if text == emojize("Приложиться к иконе :pray:"):
        churchOptions = ChurchStuff()
        result = churchOptions.getIcon()
        if result:
            await message.reply("Бог направляет вас к нужной иконе...")
            await churchBot.send_photo(user_id, photo=churchOptions.icon, reply_markup=mainMenu)
        else:
            await message.reply("К сожалению, иконы сейчас на реставрации!...", reply_markup=mainMenu)
    if text == "Послушать молитву":
        churchOptions = ChurchStuff()
        result = churchOptions.getPray()
        if result:
            await message.reply("Выбираем вам наиболее подходящую молитву и отправляем ее...")
            await churchBot.send_voice(user_id, churchOptions.pray, reply_markup=mainMenu)
        else:
            await message.reply("Хор уехал на время в тур - зайди позже...", reply_markup=mainMenu)
    if text == "Исповедаться в грехах":
        await message.reply(emojize("Бог твой стоит невидимо перед тобою, принимая исповедь твою. не стыдись и небойся, скажи Мне все :raised_hands:"), reply_markup=cancelInline)
        await Sins.waiting_for_sin.set()

executor.start_polling(dp, skip_updates=False)

