from telegram import BotCommand, BotCommandScopeChat, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonCommands, \
    Message
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from env import buttons_dict


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    """Посылает в чат текстовое сообщение"""
    if text.count('_') % 2 != 0:
        message = f'Строка "{text}" является невалидной с точки зрения markdown. Воспользуйтесь методом send_html()'
        print(message)
        return await update.message.reply_text(message)
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


async def send_text_buttons(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        buttons: dict[str, str],
) -> Message:
    """Посылает в чат текстовое сообщение, и добавляет к нему кнопки"""
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(text=value, callback_data=key)
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=text,
        reply_markup=reply_markup,
        message_thread_id=update.effective_message.message_thread_id,
    )


async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> Message:
    """Посылает в чат фотографию выбранной команды"""
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict[str, str]) -> None:
    """Отображает команду и главное меню"""
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(
        commands=command_list,
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id),
    )
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)


def load_message(name: str) -> str:
    """Загружает сообщение из папки  /resources/messages/"""
    with open(f'resources/messages/{name}.txt', 'r', encoding='utf8') as file:
        return file.read()


def load_prompt(name: str) -> str:
    """Загружает промпт из папки  /resources/messages/"""
    with open(f'resources/prompts/{name}.txt', 'r', encoding='utf8') as file:
        return file.read()


async def commands_processing(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> None:
    """По ключу команды загружает фото и отправляет текст"""
    await send_image(update, context, command)
    await send_text(update, context, load_message(command))


async def buttons_processing(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> None:
    """По ключу команды посылает в чат текстовое сообщение, и добавляет к нему кнопки"""
    await send_text_buttons(
        update=update,
        context=context,
        text=buttons_dict[command][0],
        buttons=buttons_dict[command][1],
    )


class Dialog:
    """Вспомогательный класс для хранения данных по командам"""
    mode: str | None
    talk_person: str | None
    quiz_theme: str | None
    quiz_question: str | None
    correct_answers: int
    total_questions: int
    education_for_resume: str | None
    work_experience_for_resume: str | None
    skills_for_resume: str | None

    def __init__(self):
        self.mode = self.talk_person = self.quiz_theme = self.quiz_question = None
        self.correct_answers = self.total_questions = 0
        self.education_for_resume = self.work_experience_for_resume = self.skills_for_resume = None
