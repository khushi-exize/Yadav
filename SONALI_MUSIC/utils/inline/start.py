from pyrogram.types import InlineKeyboardButton

import config
from SONALI_MUSIC import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            
            InlineKeyboardButton(text=_["S_B_4"], callback_data="MAIN_CP"),
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID),
            InlineKeyboardButton("⌯ ᴧʙσυт ⌯", callback_data="ALLBOT_CP"),
        ],
        [
            InlineKeyboardButton("⌯ ʏᴛ-ᴀᴘɪ ⌯", callback_data="bot_info_data"),
        ],
    ]
    return buttons
