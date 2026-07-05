from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import (
    add_user, get_categories, get_category,
    create_request, get_request, update_request_status
)
from keyboards import categories_keyboard, category_detail_keyboard, admin_review_keyboard

user_router = Router()


class UserStates(StatesGroup):
    waiting_screenshot = State()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )
    categories = await get_categories()

    if not categories:
        await message.answer("Hozircha kategoriyalar mavjud emas. Keyinroq urinib ko'ring.")
        return

    await message.answer(
        "👋 Assalomu alaykum! Quyidagi kategoriyalardan birini tanlang:",
        reply_markup=categories_keyboard(categories)
    )


@user_router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    categories = await get_categories()
    await callback.message.edit_text(
        "Quyidagi kategoriyalardan birini tanlang:",
        reply_markup=categories_keyboard(categories)
    )


@user_router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery):
    category_id = int(callback.data.replace("cat_", ""))
    category = await get_category(category_id)
    if category is None:
        await callback.answer("Bu kategoriya topilmadi.", show_alert=True)
        return

    _, name, price, payment_link, channel_link = category
    await callback.message.edit_text(
        f"🎬 <b>{name}</b>\n"
        f"💰 Narxi: {price}\n\n"
        f"To'lovni amalga oshiring, so'ngra to'lov chekini (skrinshotini) yuborish uchun "
        f"pastdagi <b>📤 Chek yuborish</b> tugmasini bosing.",
        reply_markup=category_detail_keyboard(category_id, payment_link)
    )


@user_router.callback_query(F.data.startswith("pay_"))
async def ask_screenshot(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.replace("pay_", ""))
    await state.update_data(category_id=category_id)
    await state.set_state(UserStates.waiting_screenshot)
    await callback.message.answer(
        "📸 Endi to'lov chekining skrinshotini (rasm sifatida) shu yerga yuboring."
    )


@user_router.message(UserStates.waiting_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    category_id = data.get("category_id")
    category = await get_category(category_id)
    await state.clear()

    if category is None:
        await message.answer("⚠️ Kategoriya topilmadi. Qaytadan /start bosing.")
        return

    _, name, price, payment_link, channel_link = category
    screenshot_file_id = message.photo[-1].file_id

    request_id = await create_request(message.from_user.id, category_id, screenshot_file_id)

    await message.answer("✅ Chekingiz qabul qilindi, admin tekshirib chiqadi. Iltimos kuting.")

    caption = (
        f"🆕 <b>Yangi to'lov so'rovi</b>\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name} "
        f"(@{message.from_user.username or 'username yo\u2019q'})\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"🎬 Kategoriya: {name}\n"
        f"💰 Narxi: {price}\n"
        f"🔢 So'rov ID: {request_id}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id,
                screenshot_file_id,
                caption=caption,
                reply_markup=admin_review_keyboard(request_id)
            )
        except Exception:
            continue


@user_router.message(UserStates.waiting_screenshot)
async def wrong_screenshot_format(message: Message):
    await message.answer("⚠️ Iltimos, chekni <b>rasm (screenshot)</b> sifatida yuboring.")


# ---------- ADMIN TASDIQLASH / RAD ETISH (foydalanuvchiga ta'sir qiladigan qism) ----------

@user_router.callback_query(F.data.startswith("approve_"))
async def approve_request(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        return
    request_id = int(callback.data.replace("approve_", ""))
    request = await get_request(request_id)

    if request is None:
        await callback.answer("So'rov topilmadi.", show_alert=True)
        return

    _, user_id, category_id, screenshot_file_id, status = request
    if status != "pending":
        await callback.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    category = await get_category(category_id)
    await update_request_status(request_id, "approved")

    if category:
        _, name, price, payment_link, channel_link = category
        try:
            await bot.send_message(
                user_id,
                f"✅ To'lovingiz tasdiqlandi!\n\n🎬 {name}\n\n🔗 Kanalga qo'shilish uchun havola:\n{channel_link}"
            )
        except Exception:
            pass

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
        reply_markup=None
    )
    await callback.answer("Tasdiqlandi ✅")


@user_router.callback_query(F.data.startswith("reject_"))
async def reject_request(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        return
    request_id = int(callback.data.replace("reject_", ""))
    request = await get_request(request_id)

    if request is None:
        await callback.answer("So'rov topilmadi.", show_alert=True)
        return

    _, user_id, category_id, screenshot_file_id, status = request
    if status != "pending":
        await callback.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    await update_request_status(request_id, "rejected")

    try:
        await bot.send_message(
            user_id,
            "❌ To'lovingiz tasdiqlanmadi. Agar xato bo'lsa, admin bilan bog'laning."
        )
    except Exception:
        pass

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
        reply_markup=None
    )
    await callback.answer("Rad etildi ❌")
