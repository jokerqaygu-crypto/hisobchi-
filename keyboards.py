from aiogram.utils.keyboard import InlineKeyboardBuilder


def categories_keyboard(categories):
    """categories: [(id, name, price, payment_link, channel_link), ...]"""
    builder = InlineKeyboardBuilder()
    for cat_id, name, price, payment_link, channel_link in categories:
        builder.button(text=f"{name} — {price}", callback_data=f"cat_{cat_id}")
    builder.adjust(1)
    return builder.as_markup()


def category_detail_keyboard(category_id: int, payment_link: str):
    builder = InlineKeyboardBuilder()
    if payment_link:
        builder.button(text="💳 To'lov qilish", url=payment_link)
    builder.button(text="📤 Chek yuborish", callback_data=f"pay_{category_id}")
    builder.button(text="⬅️ Orqaga", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()


def admin_review_keyboard(request_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"approve_{request_id}")
    builder.button(text="❌ Rad etish", callback_data=f"reject_{request_id}")
    builder.adjust(2)
    return builder.as_markup()


def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Kategoriya qo'shish", callback_data="admin_add_category")
    builder.button(text="📃 Kategoriyalar ro'yxati", callback_data="admin_list_categories")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="admin_cancel")
    return builder.as_markup()


def categories_remove_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for cat_id, name, price, payment_link, channel_link in categories:
        builder.button(text=f"🗑 {name}", callback_data=f"remove_cat_{cat_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()
