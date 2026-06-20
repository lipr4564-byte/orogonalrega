"""
Обработчик команды /start и главного меню
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType

from config import SUPPORT_BOT, PROJECT_CHANNEL
from database import register_user_start, get_user_registration
from membership import check_member
from keyboards import main_menu_kb
from logger import log_start
from premium_emoji import pe, ce

router = Router()

# ВАЖНО: только личка — без этого бот будет отвечать в группах!
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

HELLO_EMOJI = ce("5292219459015042800", "👋")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработка /start только в личке"""
    await state.clear()

    user = message.from_user
    bot = message.bot

    # Проверка членства в группе
    is_member = await check_member(bot, user.id)
    if not is_member:
        await message.answer(
            f"{pe('⛔')} Для начала вступите в <b>Rise of Europe!</b>\n\n"
            f"{pe('🤖')} Бот поддержки — {SUPPORT_BOT}\n"
            f"{pe('🔗')} Канал проекта — {PROJECT_CHANNEL}",
            parse_mode="HTML"
        )
        return

    # Регистрируем пользователя в базе (первый вход / обновление данных)
    register_user_start(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or str(user.id)
    )

    await log_start(bot, user.id, user.username or "", user.full_name or "")

    current_reg = get_user_registration(user.id)

    if current_reg:
        extra = (
            f"\n\n{pe('📍')} Ты сейчас зарегистрирован за: "
            f"<b>{current_reg['slot_flag']} {current_reg['slot_name']}</b>"
        )
    else:
        extra = ""

    await message.answer(
        f"{HELLO_EMOJI} Приветствую! Я бот регистрации "
        f"величайшего проекта <b>Rise of Europe</b>.\n\n"
        f"Что привело тебя сюда?{extra}",
        parse_mode="HTML",
        reply_markup=main_menu_kb(has_registration=bool(current_reg))
    )


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = callback.from_user

    current_reg = get_user_registration(user.id)
    if current_reg:
        extra = (
            f"\n\n{pe('📍')} Ты сейчас зарегистрирован за: "
            f"<b>{current_reg['slot_flag']} {current_reg['slot_name']}</b>"
        )
    else:
        extra = ""

    await callback.message.edit_text(
        f"{HELLO_EMOJI} Приветствую! Я бот регистрации "
        f"величайшего проекта <b>Rise of Europe</b>.\n\n"
        f"Что привело тебя сюда?{extra}",
        parse_mode="HTML",
        reply_markup=main_menu_kb(has_registration=bool(current_reg))
    )
    await callback.answer()
