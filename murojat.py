import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Environment variable dan token o'qish (xavfsiz)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1002180407386")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Murojaat(StatesGroup):
    ism = State()
    familiya = State()
    sharif = State()
    tel = State()
    manzil = State()
    shikoyat = State()

# Murojaat yuborish tugmasi
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📝 Murojaat yuborish")]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! Murojaat qoldirish uchun quyidagi tugmani bosing.",
        reply_markup=start_keyboard
    )

@dp.message(F.text.contains("Murojaat") | F.text == "📝 Murojaat yuborish")
async def start_form(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Murojaat.ism)
    await message.answer(
        "Ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Murojaat.ism)
async def process_ism(message: types.Message, state: FSMContext):
    await state.update_data(ism=message.text)
    await state.set_state(Murojaat.familiya)
    await message.answer("Familiyangizni kiriting:")

@dp.message(Murojaat.familiya)
async def process_familiya(message: types.Message, state: FSMContext):
    await state.update_data(familiya=message.text)
    await state.set_state(Murojaat.sharif)
    await message.answer("Sharifingizni kiriting:")

@dp.message(Murojaat.sharif)
async def process_sharif(message: types.Message, state: FSMContext):
    await state.update_data(sharif=message.text)
    await state.set_state(Murojaat.tel)
    await message.answer("Telefon raqamingizni kiriting:")

@dp.message(Murojaat.tel)
async def process_tel(message: types.Message, state: FSMContext):
    await state.update_data(tel=message.text)
    await state.set_state(Murojaat.manzil)
    await message.answer("Manzilingizni kiriting:\n(Masalan: Do'stlik MFY, Do'stlik ko'chasi, 11-uy)")

@dp.message(Murojaat.manzil)
async def process_manzil(message: types.Message, state: FSMContext):
    await state.update_data(manzil=message.text)
    await state.set_state(Murojaat.shikoyat)
    await message.answer("Shikoyat yoki murojaatingizni batafsil yozishingiz mumkin:")

@dp.message(Murojaat.shikoyat)
async def process_done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    fio = f"{data['familiya']} {data['ism']} {data['sharif']}"
    report_text = (
        f"F.I.O: {fio}\n"
        f"Tel: {data['tel']}\n"
        f"Manzil: {data['manzil']}\n"
        f"Shikoyat: {message.text}"
    )

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=report_text)
        await message.answer(
            "✅ Murojaat Rishton tumani Hokimiga yuborildi, "
            "sizga shikoyatingiz bo'yicha 5 ish kunida bog'lanishadi!",
            reply_markup=start_keyboard
        )
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("❌ Xatolik! Bot kanal adminligini tekshiring.")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())