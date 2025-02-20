import os

CHAT_GPT_TOKEN = os.getenv('CHAT_GPT_TOKEN')
BOT_TOKEN = os.getenv('BOT_TOKEN')

commands = {
    'start': 'Главное меню ',
    'random': 'Узнать случайный интересный факт 🧠',
    'gpt': 'Задать вопрос чату GPT 🤖',
    'talk': 'Поговорить с известной личностью 👤',
    'quiz': 'Поучаствовать в квизе ❓',
    'resume': 'Составление резюме 👷',
}

persons_buttons = {
    'talk_cobain': 'Курт Кобейн',
    'talk_hawking': 'Стивен Хокинг',
    'talk_nietzsche': 'Фридрих Ницше',
    'talk_queen': 'Королева Елизавета II',
    'talk_tolkien': 'Дж.Р.Р. Толкин',
}

quiz_buttons = {
    'quiz_prog': 'Программирование на языке Python',
    'quiz_math': 'Математические теории',
    'quiz_biology': 'Биология',
}

quiz_process_buttons = {
    'quiz_more': 'Задать еще вопрос',
    'change_theme': 'Сменить тему',
    'finish': 'Закончить квиз',
}

buttons_dict = {
    'random': ['Вот такой вот случайный факт! Как тебе?',
               {'finish': 'Закончить', 'want_another_fact': 'Хочу ещё факт'}],
    'quiz': ['Выбери тему, на которую будешь играть:', quiz_buttons],
    'finish_resume': ['Чтобы завершить нажмите кнопку "Закончить"', {'finish': 'Закончить'}],
    'talk': ['Необходимо выбрать собеседника', persons_buttons],
    'finish_talk': ['Можно продолжить разговор или выбрать другого собеседника. '
                    'Чтобы завершить нажмите кнопку "Закончить"',
                    {'finish': 'Закончить', 'another_talk': 'Выбрать другого собеседника'}],
}
