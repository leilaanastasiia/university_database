from aiogram import types
from aiogram.dispatcher import FSMContext

from app.bot import bot, dp, LIST_OF_ADMINS
from app.db import get_topics_list, get_row, delete_rows, delete_row, insert_row
from app.states import Admin


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    Shows greeting.
    """
    await message.reply('Привіт!\n'
                        'Я бот кафедри біології рослин 🌻\n'
                        'Введи назву лекції, що буде для мене ключем '
                        'для пошуку потрібної тобі інформації.')


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """
    Shows explanations what could be done wrong.
    """
    await message.reply('🌱 Будь-яке повідомлення, що почнається без "/(назва команди)", '
                        'я сприймаю як назву тему для пошуку матеріалів. '
                        'Якщо потрібні інші дії - використай меню команд або надрукуй їх.\n\n'
                        '🌱 Найважливіше - вводь теми для пошуку, що вказані у відповіді команди /topics. '
                        'Без будь-яких додаткових знаків. Це зменшить кількість можливих помилок. \n\n'
                        '\n📍 Якщо все одно виникає помилка - заскрінь свої дії та скинь напряму '
                        'розробниці: @leilaanastasiia\nНамагатимусь допомогти 🪴')


@dp.message_handler(commands=['topics'])
async def send_topics(message: types.Message):
    """
    Shows list of available topics.
    """
    output = ''
    topics = get_topics_list()
    if not topics:
        await message.reply('У базі поки що немає доступних тем.')
        return

    for topic in topics:
        output += topic + '\n'
    await message.reply(f'{output}')


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    """
    Gives access only for admins.
    """
    user_id = str(message.from_user.id)
    if user_id in LIST_OF_ADMINS:
        keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
        text_and_data = (
            ('Додати тему ✅', 'add'),
            ('Видалити тему ❌', 'delete'),
            ('Очистити всю базу ⛔', 'clear'),
        )
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
        keyboard_markup.add(*row_btns)
        await message.reply('Доступ дозволено 🌾\n'
                            'Оберіть, будь ласка, що потрібно зробити:', reply_markup=keyboard_markup)
    else:
        await message.reply('Ти не пройдьош!')


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allows user to cancel any action.
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Ви вийшли з меню для викладачів.')


@dp.callback_query_handler(text='add')
async def callback_add_topic(query: types.CallbackQuery):
    """
    Callback for 'add' button.
    """
    await Admin.add.set()
    text = 'Щоб додати тему у базу, введіть всі дані одним повідомленням. ' \
           'Розділювач - новий рядок.\n\n' \
           '📍 Дотримуйтесь послідовності:\n- Назва теми\n- Посилання на презентацію лекції\n' \
           '- Посилання на відеозапис л/р\n' \
           '- Посилання на протокол л/р\n- Коментарі викладача\n\n' \
           'Щоб вийти з меню додавання тем, на будь-якому його етапі відправте /cancel'
    await query.answer('Введіть дані 🌸')
    await bot.send_message(query.from_user.id, text)


@dp.message_handler(state=Admin.add)
async def add_topic(message: types.Message, state: FSMContext):
    """
    Adds topics to the database.
    """
    topics = get_topics_list()
    data = message.text.split('\n')
    if len(data) < 5:
        await message.reply('Здається, не всі поля заповнені 🤔\n'
                            'Будь ласка, вводьте данні у форматі, що вказаний вище.')
        return
    if len(data) > 5:
        await message.reply('Здається, введено занадто багато даних 🤔\n'
                            'Будь ласка, вводьте данні у форматі, що вказаний вище.')
        return
    elif data[0] in topics:
        await message.reply(f'Тема "{data[0]}" вже є в базі.\n')
        return

    insert_row(message.text)
    await message.reply(f'Тема "{data[0]}" успішно додана до сховища!')
    await state.finish()


@dp.callback_query_handler(text='delete')
async def callback_delete_topic(query: types.CallbackQuery):
    """
    Callback for 'delete' button.
    """
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    text_and_data = (
        ('Так, видалити 😈', 'real_delete'),
    )
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.add(*row_btns)
    text = 'Ви впевнені, що хочете видалити тему з бази?\n\n' \
           'Якщо це помилка - просто продовжуйте роботу у звичайному режимі.\n\n' \
           'Меню викладачів: /admin\nПошук тем: /start'
    await query.answer('Ви впевнені?')
    await bot.send_message(query.from_user.id, text, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='real_delete')
async def callback_real_delete_topic(query: types.CallbackQuery):
    """
    Callback for real 'delete' button.
    """
    await Admin.delete.set()
    text = 'Щоб видалити тему, введіть її назву.\n' \
           'Щоб вийти з цього меню - /cancel'
    await query.answer('Введіть назву теми 🍂')
    await bot.send_message(query.from_user.id, text)


@dp.message_handler(state=Admin.delete)
async def delete_topic(message: types.Message, state: FSMContext):
    """
    Deletes topics from the database.
    """
    topics = get_topics_list()
    if message.text not in topics:
        await message.reply(f'Тема "{message.text}" у базі не знайдена.\n')
        return

    delete_row(message.text)
    await message.reply(f'Тема "{message.text}" успішно видалена зі сховища!')
    await state.finish()


@dp.callback_query_handler(text='clear')
async def callback_clear(query: types.CallbackQuery):
    """
    Delete all rows in the table.
    """
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    text_and_data = (
        ('Так, очистити 📂', 'real_clear'),
    )
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.add(*row_btns)
    text = 'Ви впевнені, що хочете очистити всю базу?\n\n' \
           'Якщо це помилка - просто продовжуйте роботу у звичайному режимі.\n\n' \
           'Меню викладачів: /admin\nПошук тем: /start'
    await query.answer('Ви впевнені?')
    await bot.send_message(query.from_user.id, text, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='real_clear')
async def callback_real_clear(query: types.CallbackQuery):
    """
    Real delete all rows in the table.
    """
    delete_rows()
    text = 'Базу повністю очищено!'
    await query.answer(text)
    await bot.send_message(query.from_user.id, text)


@dp.message_handler()
async def send_reply(message: types.Message):
    """
    Searches the name of the topic and sends data if exists.
    """
    themes = get_topics_list()
    if message.text in themes:
        row = get_row(message.text)
        await message.reply(f'Тема: {row[0][0]}\n\n'
                             f'Посилання на лекцію: {row[0][1]}\n\n'
                             f'Посилання на відеозапис лабораторної работи: {row[0][2]}\n\n'
                             f'Посилання на протокол лобораторної роботи: {row[0][3]} \n\n'
                             f'Коментарі викладача: {row[0][4]}\n\n'
                             'Успіхів!')
    else:
        await message.reply(f'Такої теми в базі не знайдено 🤔')
