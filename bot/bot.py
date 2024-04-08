import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from config_reader import config
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
'''

# Где-то в другом месте
# Например, в точке входа в приложение
from datetime import datetime
from aiogram.filters.command import Command

'''

logging.basicConfig(level=logging.INFO) # Включаем логирование, чтобы не пропустить важные сообщения
bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML)) # Для записей с типом Secret* необходимо вызывать метод get_secret_value(), чтобы получить настоящее содержимое вместо '*******'
dp = Dispatcher() # Диспетчер


###BODY###
# тут читаем из базы список отслеживаемых ютуб плэйлистов
rutube_playlists = ['какой то плэйлист1', 'какой то плэйлист2',]

def add_playlist_to_db(rutube_playlist):
	'''
	Метод добавляет переданную ссылку в базу отслеживаемых плэйлистов
	'''
	pass

'''
# Хэндлер на команду /start
@dp.message(Command("start"))
async def start(message: Message):
	await message.answer(f"Hello, <b>{message.from_user.first_name}</b>")
'''

@dp.message(Command(commands=["show", "show_list", "show_links"])) # несколько команд делают одно и то же
async def get_random_number(message: Message):
	for link in rutube_playlists:
		await message.answer(f"<b>{link}</b>")

def link_validator(arg):
	'''
	Валидация переданной юзером ссылки на плэйлист ютуба с помощью регулярки
	Пока я нашел три варианта ссылок:
	https://rutube.ru/video/8e9315f724a70b1798d8694b92d12176/?playlist=330005
	https://rutube.ru/plst/330005/
	https://rutube.ru/video/8e9315f724a70b1798d8694b92d12176/?playlist=330005&playlistPage=1
	'''
	print(f'Тут мы валидируем переданную ссылку{arg}')
	return True

@dp.message(Command("add"))
async def set_link_to_seek(message: Message, command: CommandObject):
	if link_validator(command.args):
		rutube_playlists.append(command.args)
		add_playlist_to_db(command.args)
		await message.reply(f'{command.args} добавлен в список отслеживаемого контента')

@dp.message(Command("kill"))
async def delete_link(message: Message, command: CommandObject):
	rutube_playlists.remove(command.args)
	await message.reply(f'{command.args} удален из списка отслеживаемого контента')

async def main() -> None:
	# Отключить все апдейты, пока бот не запущен
	await bot.delete_webhook(drop_pending_updates=True)
	# Запуск процесса поллинга новых апдейтов
	await dp.start_polling(bot, mylist=[1, 2, 3])

if __name__ == "__main__":
	asyncio.run(main())

'''
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
	mylist.append(7)
	await message.answer("Добавлено число 7")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
	await message.answer(f"Ваш список: {mylist}")


@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
	await message.answer(f"Бот запущен {started_at}")

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
	await message.answer("Hello!")

# Хэндлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
	await message.reply("Test 1")


# Если не указать фильтр F.text, то хэндлер сработает даже на картинку с подписью /test
@dp.message(F.text, Command("test"))
async def any_message(message: Message):
	await message.answer("Hello, <b>world</b>!")
	await message.answer("Сообщение с <u>HTML-разметкой</u>")
	await message.answer("Сообщение без <s>какой-либо разметки</s>", parse_mode=None)


'''

