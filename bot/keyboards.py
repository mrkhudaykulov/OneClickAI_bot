from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Main menus
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📷 Расм орқали хизматлар")],
        [KeyboardButton(text="💪 Фитнес-камера")],
    ], resize_keyboard=True
)

photo_services_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍔 Калория аниқлаш")],
        [KeyboardButton(text="🍽 Таомни таниш + рецепт бериш")],
        [KeyboardButton(text="🧾 Матнни OCR орқали текстга айлантириш")],
        [KeyboardButton(text="🛍 Объект/товарни таниш")],
        [KeyboardButton(text="🔙 Орқага")],
    ], resize_keyboard=True
)

fitness_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Танани анализ қилиш (расм орқали)")],
        [KeyboardButton(text="🍛 Таом калорияси ва парҳез")],
        [KeyboardButton(text="📏 BMI / вазн / қад ҳисоблаш")],
        [KeyboardButton(text="🏃 Машқ тавсиялари")],
        [KeyboardButton(text="📅 Фитнес-режа тузиш")],
        [KeyboardButton(text="🔙 Орқага")],
    ], resize_keyboard=True
)

# Inline keyboards for post-actions

def calories_post_actions():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Яна таом юбориш", callback_data="calories_again")],
        [InlineKeyboardButton(text="📊 Қўшимча маълумот", callback_data="calories_more")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="back_photo_menu")],
    ])


def recipe_post_actions():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍛 Калория текшириш", callback_data="recipe_check_calories")],
        [InlineKeyboardButton(text="🔁 Бошқа расм юбориш", callback_data="recipe_again")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="back_photo_menu")],
    ])


def ocr_post_actions():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 PDF/Word файл қилиш", callback_data="ocr_make_files")],
        [InlineKeyboardButton(text="🌐 Таржима қилиш", callback_data="ocr_translate")],
        [InlineKeyboardButton(text="✂️ Таҳрирлаш", callback_data="ocr_edit")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="back_photo_menu")],
    ])


def product_post_actions():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Нархи / онлайн дўконлар", callback_data="product_price")],
        [InlineKeyboardButton(text="ℹ️ Техник маълумот", callback_data="product_specs")],
        [InlineKeyboardButton(text="🔁 Яна расм юбориш", callback_data="product_again")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="back_photo_menu")],
    ])


def pose_post_actions():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Яна расм юбориш", callback_data="pose_again")],
        [InlineKeyboardButton(text="🔙 Орқага", callback_data="back_fitness_menu")],
    ])


# Monetization CTA
def monet_cta_keyboard(bot_username: str = ""):
    buttons = []
    # Placeholder premium link/button (could be to payment or instructions)
    buttons.append([InlineKeyboardButton(text="⭐ Premium обуна", url="https://t.me/" + (bot_username or ""))])
    # Suggest adding to a new group
    if bot_username:
        buttons.append([InlineKeyboardButton(text="➕ Гуруҳга қўшиш", url=f"https://t.me/{bot_username}?startgroup=true")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
