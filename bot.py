from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, \
    ConversationHandler, MessageHandler, filters

from env import BOT_TOKEN, CHAT_GPT_TOKEN, commands, persons_buttons, quiz_buttons, quiz_process_buttons
from gpt import ChatGptService
from util import Dialog, buttons_processing, commands_processing, load_prompt, send_image, send_text, send_text_buttons, \
    show_main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вызов главного меню"""
    dialog.mode = 'main'
    await commands_processing(update, context, 'main')
    await show_main_menu(update=update, context=context, commands=commands)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вызов команды "Случайный факт" """
    dialog.mode = 'gpt'
    await commands_processing(update, context, 'random')
    await gpt_dialog(update, context, load_prompt('random'), 'Сообщи любой случайный факт')
    await buttons_processing(update, context, 'random')


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вызов ChatGPT"""
    dialog.mode = 'gpt'
    await commands_processing(update, context, 'gpt')


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вызов команды "Поговорить с известной личностью" """
    dialog.mode = 'talk'
    await commands_processing(update, context, 'talk')
    await buttons_processing(update, context, 'talk')


async def another_talk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выбрать другого собеседника"""
    await buttons_processing(update, context, 'talk')


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вызов команды "Поучаствовать в квизе" """
    dialog.mode = 'quiz'
    dialog.correct_answers = dialog.total_questions = 0
    await commands_processing(update, context, 'quiz')
    await quiz_themes(update, context)


async def gpt_dialog(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        prompt_text: str,
        message_text: str = None,
) -> str:
    """Переключение в режим диалога с ChatGPT"""
    message_text = message_text if message_text else update.message.text
    answer = await chat_gpt.send_question(prompt_text=prompt_text, message_text=message_text)
    await send_text(update, context, answer)
    return answer


async def talk_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик диалога с известной личностью"""
    dialog.mode = 'talk'
    dialog.talk_person = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(dialog.talk_person))
    await send_image(update, context, dialog.talk_person)
    await send_text(update, context, f'Привет, я {persons_buttons[dialog.talk_person]}! Задай свой вопрос!')


async def quiz_themes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выбор темы для квиза"""
    dialog.mode = 'quiz'
    dialog.correct_answers = dialog.total_questions = 0
    await buttons_processing(update, context, 'quiz')


async def quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_theme: str = None) -> None:
    """Генерация вопроса на выбранную тему"""
    dialog.mode = 'quiz'
    quiz_theme = update.callback_query.data if not quiz_theme else quiz_theme
    correct_quiz_theme = quiz_theme in [key for key in quiz_buttons.keys()] + ['quiz_more']
    dialog.quiz_theme = quiz_theme if correct_quiz_theme else dialog.quiz_theme
    if dialog.total_questions == 0:
        await send_text(update, context, f'Генерация вопроса на тему *"{quiz_buttons[dialog.quiz_theme]}"*')
        question = await gpt_dialog(update, context, load_prompt('quiz'), dialog.quiz_theme)
    else:
        question = await chat_gpt.add_message(message_text=dialog.quiz_theme)
        await send_text(update, context, question)
    dialog.quiz_question = question


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ответа на вопрос квиза"""
    dialog.mode = 'quiz'
    answer = update.message.text
    response = await chat_gpt.add_message(message_text=f'Проверь ответ: {answer} на вопрос: {dialog.quiz_question}')
    await send_text(update, context, response)
    if "Правильно!" in response:
        dialog.correct_answers += 1
    dialog.total_questions += 1


"""Этапы диалога по составлению резюме"""
EDUCATION, EXPERIENCE, SKILLS = range(3)


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога по составлению резюме, запрос данных об образовании"""
    dialog.mode = 'resume'
    dialog.education_for_resume = dialog.work_experience_for_resume = dialog.skills_for_resume = None
    await commands_processing(update, context, 'resume')
    await send_text(
        update=update,
        context=context,
        text='*Привет! Пожалуйста, расскажите мне о своем образовании в формате:*'
             '\n- Название учебного заведения\n- Специальность\n- Год окончания',
    )
    await buttons_processing(update, context, 'finish_resume')
    return EDUCATION


async def education(update: Update, context: CallbackContext) -> int:
    """Сохранение данных об образовании, запрос данных об опыте работы для составления резюме"""
    if dialog.mode == 'main':
        return ConversationHandler.END
    dialog.education_for_resume = update.message.text
    await send_text(
        update=update,
        context=context,
        text='*Спасибо! Теперь расскажите о вашем опыте работы в формате:*'
             '\n- Название компании/организации\n- Должность\n- Основные обязанности и достижения\n- Период работы',
    )
    await buttons_processing(update, context, 'finish_resume')
    return EXPERIENCE


async def experience(update: Update, context: CallbackContext) -> int:
    """Сохранение данных об опыте работы, запрос данных о навыках для составления резюме"""
    if dialog.mode == 'main':
        return ConversationHandler.END
    dialog.work_experience_for_resume = update.message.text
    await send_text(
        update=update,
        context=context,
        text='*Отлично! Какие у вас навыки?* Например, знание языков программирования, '
             'работа с определёнными программами, навыки управления, знание иностранных языков и т.д.',
    )
    await buttons_processing(update, context, 'finish_resume')
    return SKILLS


async def skills(update: Update, context: CallbackContext) -> int:
    """Сохранение данных о навыхах, генерация резюме"""
    if dialog.mode == 'main':
        return ConversationHandler.END
    dialog.skills_for_resume = update.message.text
    await send_text(update, context, 'Спасибо! Я сохранил вашу информацию. Вот что вы мне рассказали:')
    resume_request = (
        f'*Образование:* {dialog.education_for_resume}\n*Опыт работы:* {dialog.work_experience_for_resume}'
        f'\n*Навыки:* {dialog.skills_for_resume}')
    await send_text(update, context, resume_request)
    await send_text(update, context, f'По Вашему запросу генерируется текст резюме. _Пожалуйста подождите.._')
    await gpt_dialog(
        update=update,
        context=context,
        prompt_text=load_prompt('resume'),
        message_text=f'Сгенерируй резюме по следующим параметрам. {resume_request}',
    )
    return ConversationHandler.END


async def main_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Основные кнопки для разных команд"""
    dialog.mode = 'main'
    action = {
        'finish': start,
        'want_another_fact': random,
        'change_theme': quiz_themes,
        'another_talk': another_talk,
    }[update.callback_query.data]
    await action(update, context)


async def main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context, load_prompt('gpt'))
    elif dialog.mode == 'talk':
        await gpt_dialog(update, context, load_prompt(dialog.talk_person))
        await buttons_processing(update, context, 'finish_talk')
    elif dialog.mode == 'quiz':
        await quiz_answer(update, context)
        await send_text_buttons(
            update=update,
            context=context,
            text=f'Всего вопросов: {dialog.total_questions}. Правильных ответов: {dialog.correct_answers}',
            buttons=quiz_process_buttons,
        )
    else:
        await send_image(update, context, 'main')


dialog = Dialog()
chat_gpt = ChatGptService(token=CHAT_GPT_TOKEN)
app = ApplicationBuilder().token(token=BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('talk', talk))

resume_handler = ConversationHandler(
    entry_points=[CommandHandler('resume', resume)],
    states={
        EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, education)],
        EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
        SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, skills)],
    },
    fallbacks=[CommandHandler('start', start)],
)
app.add_handler(resume_handler)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main))
app.add_handler(CallbackQueryHandler(talk_processing, pattern='talk_*'))
app.add_handler(CallbackQueryHandler(quiz_question, pattern='quiz_*'))
app.add_handler(CallbackQueryHandler(main_buttons,
                                     pattern='finish|want_another_fact|change_theme|quiz_more|another_talk'))

app.run_polling()
