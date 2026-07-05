from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import (
    add_category, get_categories, remove_category, users_count
)
from keyboards import admin_menu_keyboard, cancel_keyboard, categories_remove_keyboard
from git_sync import sync_database_to_github

admin_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminStates(StatesGroup):
    waiting_name = State()
    waiting_price = State()
    waiting_payment_link = State()
    waiting_channel_link = State()


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


@admin_router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


@admin_router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


# ============================================================
# KATEGORIYA QO'SHISH (4 bosqichli FSM)
# ============================================================

@admin_router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.waiting_name)
    await callback.message.edit_text(
        "📝 Kategoriya nomini yuboring (masalan: <b>Anime kolleksiyasi</b>):",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(AdminStates.waiting_name)
async def process_category_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStates.waiting_price)
    await message.answer(
        "💰 Narxini yuboring (masalan: <b>15 000 so'm</b>):",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(AdminStates.waiting_price)
async def process_category_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(price=message.text.strip())
    await state.set_state(AdminStates.waiting_payment_link)
    await message.answer(
        "💳 To'lov havolasini yuboring (Click/Payme link):",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(AdminStates.waiting_payment_link)
async def process_category_payment_link(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(payment_link=message.text.strip())
    await state.set_state(AdminStates.waiting_channel_link)
    await message.answer(
        "🔗 Ushbu kategoriya uchun (to'lovdan keyin beriladigan) kanal havolasini yuboring:",
        reply_markup=cancel_keyboard()
    )


@admin_router.message(AdminStates.waiting_channel_link)
async def process_category_channel_link(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    name = data.get("name")
    price = data.get("price")
    payment_link = data.get("payment_link")
    channel_link = message.text.strip()

    await add_category(name, price, payment_link, channel_link)
    await state.clear()

    await sync_database_to_github(f"Kategoriya qo'shildi: {name}")

    await message.answer(f"✅ \"{name}\" kategoriyasi qo'shildi!")
    await message.answer("🛠 Admin panel:", reply_markup=admin_menu_keyboard())


# ============================================================
# KATEGORIYALAR RO'YXATI / O'CHIRISH
# ============================================================

@admin_router.callback_query(F.data == "admin_list_categories")
async def admin_list_categories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    categories = await get_categories()
    if not categories:
        await callback.answer("Hozircha kategoriya qo'shilmagan.", show_alert=True)
        return
    await callback.message.edit_text(
        "📃 Kategoriyalar (o'chirish uchun bosing):",
        reply_markup=categories_remove_keyboard(categories)
    )


@admin_router.callback_query(F.data.startswith("remove_cat_"))
async def admin_remove_category(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    category_id = int(callback.data.replace("remove_cat_", ""))
    await remove_category(category_id)
    await sync_database_to_github(f"Kategoriya o'chirildi: {category_id}")
    categories = await get_categories()
    if categories:
        await callback.message.edit_text(
            "📃 Kategoriyalar (o'chirish uchun bosing):",
            reply_markup=categories_remove_keyboard(categories)
        )
    else:
        await callback.message.edit_text(
            "Ro'yxat bo'sh.\n\n🛠 Admin panel:",
            reply_markup=admin_menu_keyboard()
        )
    await callback.answer("🗑 O'chirildi")


# ============================================================
# STATISTIKA
# ============================================================

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    u_count = await users_count()
    categories = await get_categories()
    await callback.answer()
    await callback.message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👤 Foydalanuvchilar soni: {u_count}\n"
        f"📃 Kategoriyalar soni: {len(categories)}"
    )
