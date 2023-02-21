import os, re, time, logging
from aiogram import types, Bot, Dispatcher, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from dotenv import load_dotenv
import read_data as rd
import database as db


count_BIK, count_BPI, count_BIS, count_BIN = 0, 0, 0, 0
message_id, class_u, last_id = 0, 0, 0
number, full_name, name = '', '', ''


#Configuration logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='app.log',
    filemode='w+'
)


#connect bot, load .env
load_dotenv()
bot = Bot(token=os.environ.get('TOKEN'))
dispatcher = Dispatcher(bot)
logging.info("Start bot")


#Run bot after /start
@dispatcher.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    try:
        # initialization phat to photo, phrase to text, 
        path_photo = 'img\\start.png'
        phrase = rd.get_standart_phrase("welcome")
        user_id = message.from_user.id

        #create keyboard continue
        keyboard = [[InlineKeyboardButton(text="Продолжить", callback_data="start_registration")]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.send_photo(user_id, open(path_photo, 'rb'), caption=phrase, reply_markup=reply_markup)

        #Variable for insert database
        global message_id, last_id , full_name
        message_id = message.message_id
        full_name = message.from_user.username

        #log about start session
        logging.info("User %s started the conversation.", full_name)

        await db.connection_database()
        logging.info(f'connected database')

        last_id = await db.insert_telegram_info([full_name, time.asctime()])
        logging.info(f"Insert {full_name} successfull time: {time.asctime()}")

    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_handler')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_handler')
        await bot.send_message(text="Error found key")


#Send excel file with database info
@dispatcher.message_handler(commands=['excel'])
async def get_excel(message: types.Message):
    try:
        global full_name
        passwd = message.get_full_command()[1]
        if passwd == os.environ.get('PASSWORD'):
            await db.sql_to_excel()
            await bot.send_document(message.chat.id, InputFile("data\\user.xlsx"))
            logging.info("user info send")
            await bot.send_document(message.chat.id, InputFile("data\\telegram_info.xlsx"))
            logging.info("telegram info send")

        else:
            await bot.send_message(message.chat.id, text="Incorrect password")
            logging.info(f"{full_name} incorrect input password: {passwd}")

    except FileNotFoundError:
        logging.error(f'Path xlsx is found')

#input number command handler
@dispatcher.message_handler(commands=['number'])
async def get_number(message: types.Message):
    #Variable for insert database and edit message
    global message_id, number

    #if command it number phone and not empty, number save and logging
    if bool(re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                message.get_full_command()[1])) and message.get_full_command()[1] != '':

        phrase = rd.get_standart_phrase('get_class')
        await bot.edit_message_caption(message.chat.id, message_id, None, phrase)
        number = message.get_full_command()[1]

        logging.info(f'Input number {number}')

    #if number incorrect, please reply
    else:
        logging.info('None number')
        phrase = rd.get_standart_phrase('reply_number')
        await bot.edit_message_caption(message.chat.id, message_id, None, phrase)


#input name command handler
@dispatcher.message_handler(commands=['name'])
async def get_name(message: types.Message):
    #Variable for insert database and edit message
    global message_id, name

    #if command it not empty, name save, logging
    if message.get_full_command()[1] != '':
        name = message.get_full_command()[1]

        logging.info(f'Input name {message.get_full_command()[1]}')

        phrase = rd.get_standart_phrase('get_number')
        await bot.edit_message_caption(message.chat.id, message_id, None, phrase)

    #if name incorrect, please reply
    else:
        logging.info("None name")

        error = rd.get_standart_phrase('reply_full_name')
        await bot.edit_message_caption(message.chat.id, message_id, None, error)


#input class command handler
@dispatcher.message_handler(commands=['class'])
async def get_name(message: types.Message):
    try:
        #Variable for insert database and edit message
        global message_id, class_u
        
        #if class it integer and not empty, save class, logging
        if message.get_full_command()[1] != '' and bool(re.match(r'[0-9]', message.get_full_command()[1])):
            class_u = message.get_full_command()[1]

            logging.info(f'Input class {message.get_full_command()[1]}')

            phrase = rd.get_standart_phrase('begin_test')
            keyboard = [[InlineKeyboardButton(text="Продолжить", callback_data="start_test")]]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            await bot.edit_message_caption(message.chat.id, message_id, None, phrase, reply_markup=reply_markup)

        #if class incorrect, please reply
        else:
            logging.info("None class")
            error = rd.get_standart_phrase('reply_class')
            await bot.edit_message_caption(message.chat.id, message_id, None, error)

    except KeyError:
        logging.error(f'{phrase} is found key in start_handler')
        await bot.send_message(text="Error found key")


@dispatcher.callback_query_handler(text="count_BIK_test_1") #Plus to BIK after test 1 and run test 2
async def count_BIK_test_1(callback: types.CallbackQuery):
    global count_BIK
    count_BIK += 1
    await start_test_2(callback)


@dispatcher.callback_query_handler(text="count_ALL_test_1") #Plus to ALL except BIK after test 1 and run test 2
async def count_ALL_test_1(callback: types.CallbackQuery):    
    global count_BIN, count_BPI, count_BIS
    count_BIN += 1
    count_BIS += 1
    count_BPI += 1
    await start_test_2(callback)


@dispatcher.callback_query_handler(text="count_BIS_test_2") #Plus to BIS after test 2 and run test 3
async def count_BIS_test_2(callback: types.CallbackQuery):
    global count_BIS
    count_BIS += 1
    await start_test_3(callback)


@dispatcher.callback_query_handler(text="count_BIN_test_2") #Plus to BIN after test 2 and run test 3
async def count_BIN_test_2(callback: types.CallbackQuery):
    global count_BIN
    count_BIN += 1
    await start_test_3(callback)


@dispatcher.callback_query_handler(text="count_BPI_test_2") #Plus to BPI after test 2 and run test 3
async def count_BPI_test_2(callback: types.CallbackQuery):
    global count_BPI
    count_BPI += 1
    await start_test_3(callback)


@dispatcher.callback_query_handler(text="count_BPI_test_3") #Plus to BPI after test 3 and run test 4
async def count_BPI_test_3(callback: types.CallbackQuery):
    global count_BPI
    count_BPI += 1
    await start_test_4(callback)


@dispatcher.callback_query_handler(text="count_BIS_test_3") #Plus to BIS after test 3 and run test 4
async def count_BIS_test_3(callback: types.CallbackQuery):
    global count_BIS
    count_BIS += 1
    await start_test_4(callback)


@dispatcher.callback_query_handler(text="count_BIN_test_3") #Plus to BIN after test 3 and run test 4
async def count_BIN_test_3(callback: types.CallbackQuery):
    global count_BIN
    count_BIN += 1
    await start_test_4(callback)


@dispatcher.callback_query_handler(text="count_BIK_test_3") #Plus to BIK after test 3 and run test 4
async def count_BIK_test_3(callback: types.CallbackQuery):
    global count_BIK
    count_BIK += 1
    await start_test_4(callback)


@dispatcher.callback_query_handler(text="count_BPI_test_4") #Plus to BPI after test 4 and run test 5
async def count_BPI_test_4(callback: types.CallbackQuery):
    global count_BPI
    count_BPI += 1
    await start_test_5(callback)


@dispatcher.callback_query_handler(text="count_BIS_test_4") #Plus to BIS after test 4 and run test 5
async def count_BIS_test_4(callback: types.CallbackQuery):
    global count_BIS
    count_BIS += 1
    await start_test_5(callback)


@dispatcher.callback_query_handler(text="count_BIN_test_4") #Plus to BIN after test 4 and run test 5
async def count_BIN_test_4(callback: types.CallbackQuery):
    global count_BIN
    count_BIN += 1
    await start_test_5(callback)


@dispatcher.callback_query_handler(text="count_BIK_test_4") #Plus to BIK after test 4 and run test 5
async def count_BIK_test_4(callback: types.CallbackQuery):
    global count_BIK
    count_BIK += 1
    await start_test_5(callback)



@dispatcher.callback_query_handler(text="count_BPI_test_5")  #Plus to BPI after test 5 and run finish
async def count_BPI_test_5(callback: types.CallbackQuery):
    global count_BPI
    count_BPI += 1
    await finish(callback)


@dispatcher.callback_query_handler(text="count_BIS_test_5") #Plus to BIS after test 5 and run finish
async def count_BIS_test_5(callback: types.CallbackQuery):
    global count_BIS
    count_BIS += 1
    await finish(callback)


@dispatcher.callback_query_handler(text="count_BIN_test_5") #Plus to BIN after test 5 and run finish
async def count_BIN_test_5(callback: types.CallbackQuery):
    global count_BIN
    count_BIN += 1
    await finish(callback)


@dispatcher.callback_query_handler(text="count_BIK_test_5") #Plus to BIK after test 5 and run finish
async def count_BIK_test_5(callback: types.CallbackQuery):
    global count_BIK
    count_BIK += 1
    await finish(callback)


#start test if callback_data = start_test
@dispatcher.callback_query_handler(text="start_test")
async def start_test_1(callback: types.CallbackQuery):
    try:
        path_photo = 'img\\test1.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_test('phrase_1')
        answers = rd.get_answers('answers_phrase_1')

        keyboard = [
                [
                    InlineKeyboardButton(text=answers["answer_1"], callback_data="count_BIK_test_1"),
                    InlineKeyboardButton(text=answers["answer_2"], callback_data="count_ALL_test_1")
                ]
            ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await callback.message.edit_caption(phrase, reply_markup=reply_markup)

    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_1')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_1')
        await bot.send_message(text="Error found key")


async def start_test_2(callback):
    try:
        path_photo = 'img\\test2.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_test('phrase_2')
        answers = rd.get_answers('answers_phrase_2')

        keyboard = [
                    [InlineKeyboardButton(text=answers["answer_1"], callback_data="count_BIS_test_2")],
                    [InlineKeyboardButton(text=answers["answer_2"], callback_data="count_BIN_test_2")],
                    [InlineKeyboardButton(text=answers["answer_3"], callback_data="count_BPI_test_2")],
                    [InlineKeyboardButton(text=answers["answer_4"], callback_data="count_BPI_test_2")]
                
            ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await callback.message.edit_caption(phrase, reply_markup=reply_markup)

    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_2')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_2')
        await bot.send_message(text="Error found key")


async def start_test_3(callback):
    try:
        path_photo = 'img\\test3.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_test('phrase_3')
        answers = rd.get_answers('answers_phrase_3')

        keyboard = [
                    [InlineKeyboardButton(text=answers["answer_1"], callback_data="count_BIK_test_3")],
                    [InlineKeyboardButton(text=answers["answer_2"], callback_data="count_BIS_test_3")],
                    [InlineKeyboardButton(text=answers["answer_3"], callback_data="count_BIN_test_3")],
                    [InlineKeyboardButton(text=answers["answer_4"], callback_data="count_BPI_test_3")]
            ]

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await callback.message.edit_caption(phrase, reply_markup=reply_markup)

    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_3')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_3')
        await bot.send_message(text="Error found key")


async def start_test_4(callback):
    try:
        path_photo = 'img\\test4.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_test('phrase_4')
        answers = rd.get_answers('answers_phrase_4')

        keyboard = [
                    [InlineKeyboardButton(text=answers["answer_1"], callback_data="count_BIK_test_4")],
                    [InlineKeyboardButton(text=answers["answer_2"], callback_data="count_BIS_test_4")],
                    [InlineKeyboardButton(text=answers["answer_3"], callback_data="count_BIN_test_4")],
                    [InlineKeyboardButton(text=answers["answer_4"], callback_data="count_BPI_test_4")]
            ]
            
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await callback.message.edit_caption(phrase, reply_markup=reply_markup)

    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_4')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_4')
        await bot.send_message(text="Error found key")


async def start_test_5(callback):
    try:
        path_photo = 'img\\test5.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_test('phrase_5')
        answers = rd.get_answers('answers_phrase_5')

        keyboard = [
                    [InlineKeyboardButton(text=answers["answer_1"], callback_data="count_BIN_test_5")],
                    [InlineKeyboardButton(text=answers["answer_2"], callback_data="count_BIS_test_5")],
                    [InlineKeyboardButton(text=answers["answer_3"], callback_data="count_BPI_test_5")],
                    [InlineKeyboardButton(text=answers["answer_4"], callback_data="count_BIK_test_5")]
            ]
            
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await callback.message.edit_caption(phrase, reply_markup=reply_markup)

    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_5')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_5')
        await bot.send_message(text="Error found key")


def speciality():
    global count_BIK, count_BIN, count_BIS, count_BPI
    if count_BIK > (count_BPI and count_BIN and count_BIS):
        return rd.get_speciality('BIK')
    elif count_BPI > (count_BIK and count_BIN and count_BIS):
        return rd.get_speciality('BPI')
    elif count_BIN > (count_BIK and count_BPI and count_BIS):
        return rd.get_speciality('BIN')
    elif count_BIS > (count_BIK and count_BIN and count_BPI):
        return rd.get_speciality('BIS')
    else:
        return "Супер редкость, ты будешь хорош во всём!"


async def finish(callback):
    try:
        path_photo = 'img\\start.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_standart_phrase('goodbye')
        spec = speciality()
        goodbye_1 = phrase['goodbye1']
        goodbye_2 = phrase['goodbye2']
        await callback.message.edit_caption(f'{goodbye_1} {spec} {goodbye_2}')
        await db.insert_user(name, class_u, str(number), last_id, spec)
    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_1')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_1')
        await bot.send_message(text="Error found key")


# start registration
@dispatcher.callback_query_handler(text="start_registration")
async def start_registartion(callback: types.CallbackQuery):
    try:
        path_photo = 'img\\start.png'

        await callback.message.edit_media(media=InputMediaPhoto(open(path_photo, 'rb')))

        phrase = rd.get_standart_phrase('get_full_name')

        await callback.message.edit_caption(phrase)
        global message_id
        message_id = callback.message.message_id
    except FileNotFoundError:
        logging.error(f'{path_photo} is found directory in start_test_1')
        await bot.send_message(text="Error path photo")

    except KeyError:
        logging.error(f'{phrase} is found key in start_test_1')
        await bot.send_message(text="Error found key")

if __name__ == '__main__':
    executor.start_polling(dispatcher)