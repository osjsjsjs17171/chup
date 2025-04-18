
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from utils.account_manager import add_account, get_accounts, is_account_ready
from utils.scraper import start_scraping

BOT_TOKEN = "7256838089:AAEP9dHG_X8Sd5IyGWJ2XAcAdymSWNCOYcI"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_data = {}

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("➕ Add New Account"))
main_menu.add(KeyboardButton("✅ List Active Accounts"))
main_menu.add(KeyboardButton("⚙️ Set Groups and Delay"))
main_menu.add(KeyboardButton("🚀 Start Member Adding"))

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Welcome to Telegram Multi-Account Scraper Bot!", reply_markup=main_menu)

@dp.message_handler(lambda msg: msg.text == "➕ Add New Account")
async def add_account_start(message: types.Message):
    await message.answer("Send the phone number (with country code):")
    user_data[message.from_user.id] = {"step": "awaiting_phone"}

@dp.message_handler(lambda msg: user_data.get(msg.from_user.id, {}).get("step") == "awaiting_phone")
async def receive_phone(message: types.Message):
    phone = message.text.strip()
    user_data[message.from_user.id] = {"phone": phone, "step": "awaiting_code"}
    await add_account(phone)
    await message.answer("Code sent! Please enter the code (e.g. 12345):")

@dp.message_handler(lambda msg: user_data.get(msg.from_user.id, {}).get("step") == "awaiting_code")
async def receive_code(message: types.Message):
    code = message.text.strip()
    phone = user_data[message.from_user.id]["phone"]
    success = await add_account(phone, code=code)
    if success:
        await message.answer("Account added successfully!", reply_markup=main_menu)
    else:
        await message.answer("Login failed. Try again.")

@dp.message_handler(lambda msg: msg.text == "✅ List Active Accounts")
async def list_accounts(message: types.Message):
    accounts = get_accounts()
    ready = [a for a in accounts if is_account_ready(a)]

@dp.message_handler(lambda msg: msg.text == "⚙️ Set Groups and Delay")
async def configure(message: types.Message):
    await message.answer("Send source_group target_group delay (e.g. mysource mytarget 10):")
    user_data[message.from_user.id] = {"step": "configuring"}

@dp.message_handler(lambda msg: user_data.get(msg.from_user.id, {}).get("step") == "configuring")
async def receive_config(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) == 3:
        source, target, delay = parts
        user_data[message.from_user.id] = {"source": source, "target": target, "delay": int(delay)}
        await message.answer("Configuration saved!", reply_markup=main_menu)
    else:
        await message.answer("Invalid format. Use: source target delay")

@dp.message_handler(lambda msg: msg.text == "🚀 Start Member Adding")
async def start_scrape_add(message: types.Message):
    conf = user_data.get(message.from_user.id, {})
    if not all(k in conf for k in ("source", "target", "delay")):
        await message.answer("Please configure source, target and delay first.")
        return
    await message.answer("Starting...")
    await start_scraping(conf["source"], conf["target"], conf["delay"])
    await message.answer("Done.")
