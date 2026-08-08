import logging
from functools import wraps
from json_storage import *
import telebot
from telebot import types
import os
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_command(func):
    """Логирует все команды пользователя"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user = message.from_user
        log_msg = (f"Команда от user_id={user.id}, "
                   f"username=@{user.username or 'None'}, "
                   f"name={user.first_name} {user.last_name or ''}, "
                   f"text={message.text}")
        logger.info(log_msg)
        return func(message, *args, **kwargs)
    return wrapper

TOKEN = '8853191354:AAFryzSmYLw2Ushho4UK9cQqUTiESDhc50M'



bot = telebot.TeleBot(TOKEN)

#ID Одноклассников,но будь внимательней,это не Username который начинается на @,узнать его можно в спец боте
id_admins_list = [
    1790228432, #Ксюша Шаркеева
    1618280314, # Я
    6686184657, # Марина
    5265246785 # Классуха 
]


school_class_letter = "9A"

class my_bot:
    @staticmethod
    def show_menu(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Расписание')
        btn2 = types.KeyboardButton('ДЗ')
        btn3 = types.KeyboardButton('Важное')
        btn4 = types.KeyboardButton('Мероприятия')
        btn5 = types.KeyboardButton('История ДЗ')
        btn6 = types.KeyboardButton('ПОМОЩЬ!!')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

    @staticmethod
    @log_command
    def start(message):
        text = f'Привет, я бот 🤖 для группы {school_class_letter} класса'
        bot.send_message(message.chat.id, text)

    @staticmethod
    @log_command
    def help(message):
        admins_text = '\n'.join(
            [f'• [Админ](tg://user?id={user_id})' for user_id in id_admins_list]
        )
        text = (
            f' **Бот классной группы 🤖 {school_class_letter} **\n'
            ' **МЕНЮ:**\n'
            '`/menu` — Выскочит меню с кнопками\n'
            '`ДЗ` - Высветится последнее записаное ДЗ\n'
            '`История ДЗ` - Нет,это не ДЗ по истории,это последнии 5 ДЗ записанных в память\n'
            '`ПОМОЩЬ!!` - Выскочит это меню в котором ты сейчас это читаешь\n'
            '`Важное` - Высветится последнее важное объявление\n'
            '`Расписание` - Высветится школьное расписание записанное в памяти\n'
            '`Мероприятия` - Высветится последнее объявленое мероприятие записанное в памяти\n'
            '\n'
            ' **Админам:**\n'
            '`!дз <текст>` — обновить ДЗ\n'
            '`!важно <текст>` — обновить объявление\n'
            '**АДМИНЫ** \n'
            f' {admins_text} '
        )
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @staticmethod
    @log_command
    def add_dz(message):
        user_id = message.from_user.id
        if user_id not in id_admins_list:
            bot.send_message(message.chat.id, "Ты не состоишь в списке администраторов, ты не можешь редактировать Д/З", parse_mode='Markdown')
            return
        
        new_dz = message.text[4:].strip()
        if not new_dz:
            bot.send_message(message.chat.id, "Напиши текст Д/З после команды. Пример: `!дз математика стр 5`", parse_mode='Markdown')
            return

        data = load_data()
        now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
        data['dz_history'].append({'timestamp': now_str, 'text': new_dz})
        save_data(data)

        # Логируем действие админа
        logger.warning(f"АДМИН {user_id} обновил ДЗ: {new_dz[:50]}...")

        bot.send_message(
            message.chat.id,
            f'✅ **Д/З обновлено ({now_str}):**\n{new_dz}',
            parse_mode='Markdown',
        )

    @staticmethod
    @log_command
    def show_dz(message):
        data = load_data()
        history = data.get('dz_history', [])
        if not history:
            bot.send_message(message.chat.id, 'Д/З пока не задано.')
            return
        last_entry = history[-1]
        text = f"**🕐 Актуальное Д/З** (от {last_entry['timestamp']}):\n\n{last_entry['text']}"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @staticmethod
    @log_command
    def show_dz_history(message):
        data = load_data()
        history = data.get('dz_history', [])
        if not history:
            bot.send_message(message.chat.id, '🌵 История Д/З пуста.')
            return
        recent = history[-5:][::-1]
        lines = []
        for item in recent:
            lines.append(f"📌 **{item['timestamp']}**\n{item['text']}\n")
        text = '📜 **История последних обновлений Д/З:**\n\n' + '\n'.join(lines)
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @staticmethod
    @log_command
    def add_important(message):
        user_id = message.from_user.id
        if user_id not in id_admins_list:
            bot.send_message(message.chat.id, 'Ты не состоишь в списке администраторов!', parse_mode='Markdown')
            return

        text = message.text[7:].strip()
        if not text:
            bot.send_message(
                message.chat.id,
                'Напиши текст после команды. Пример: `!важно Завтра сокращенный день`',
                parse_mode='Markdown',
            )
            return

        data = load_data()
        now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
        data.setdefault('vazhnoe_history', []).append({'timestamp': now_str, 'text': text})
        save_data(data)

        logger.warning(f"АДМИН {user_id} обновил важное: {text[:50]}...")

        bot.send_message(
            message.chat.id,
            f'🚨 **Важное объявление обновлено ({now_str}):**\n{text}',
            parse_mode='Markdown',
        )

    @staticmethod
    @log_command
    def show_important(message):
        data = load_data()
        history = data.get('vazhnoe_history', [])
        if not history:
            bot.send_message(message.chat.id, '🔔 Важных объявлений пока нет.')
            return
        last_entry = history[-1]
        text = f"🚨 **Важное объявление** (от {last_entry['timestamp']}):\n\n{last_entry['text']}"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @staticmethod
    @log_command
    def add_event(message):
        user_id = message.from_user.id
        if user_id not in id_admins_list:
            bot.send_message(message.chat.id, 'Ты не состоишь в списке администраторов!', parse_mode='Markdown')
            return

        text = message.text[12:].strip()
        if not text:
            bot.send_message(
                message.chat.id,
                'Напиши текст после команды. Пример: `!мероприятие В пятницу поход в музей`',
                parse_mode='Markdown',
            )
            return

        data = load_data()
        now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
        data.setdefault('meropriyatiya_history', []).append({'timestamp': now_str, 'text': text})
        save_data(data)

        logger.warning(f"АДМИН {user_id} добавил мероприятие: {text[:50]}...")

        bot.send_message(
            message.chat.id,
            f'🎉 **Мероприятие добавлено ({now_str}):**\n{text}',
            parse_mode='Markdown',
        )

    @staticmethod
    @log_command
    def show_event(message):
        data = load_data()
        history = data.get('meropriyatiya_history', [])
        if not history:
            bot.send_message(message.chat.id, '🎉 Ближайших мероприятий не запланировано.')
            return
        last_entry = history[-1]
        text = f"🎉 **Ближайшее мероприятие** (от {last_entry['timestamp']}):\n\n{last_entry['text']}"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @staticmethod
    @log_command
    def add_raspisanie(message):
        user_id = message.from_user.id
        if user_id not in id_admins_list:
            bot.send_message(message.chat.id, 'Ты не админ!')
            return

        raw_text = message.text or ''
        if len(raw_text) <= 11:
            bot.send_message(message.chat.id, 'Пусто! Напиши расписание после команды.')
            return

        schedule_body = raw_text[11:].strip()
        data = load_data()
        data['raspisanie'] = schedule_body
        save_data(data)

        logger.warning(f"АДМИН {user_id} обновил расписание: {schedule_body[:50]}...")

        bot.send_message(
            message.chat.id,
            f'📅 **Расписание записано:**\n\n{schedule_body}',
            parse_mode='Markdown',
        )

    @staticmethod
    @log_command
    def show_raspisanie(message):
        data = load_data()
        schedule_text = data.get('raspisanie', '')
        if not schedule_text:
            bot.send_message(message.chat.id, '📅 Расписание пока не заполнено.')
            return
        text = f'📅 **Школьное расписание:**\n\n{schedule_text}'
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

def init():
    bot.register_message_handler(my_bot.start, commands=['start'])
    bot.register_message_handler(my_bot.show_menu, commands=['menu'])
    bot.register_message_handler(my_bot.add_dz, func=lambda m: m.text is not None and m.text.startswith('!дз'))
    bot.register_message_handler(my_bot.show_dz, func=lambda m: m.text is not None and m.text.startswith('ДЗ'))
    bot.register_message_handler(my_bot.show_dz_history, func=lambda m: m.text is not None and m.text.startswith('История ДЗ'))
    bot.register_message_handler(my_bot.help, func=lambda m: m.text is not None and m.text.startswith('ПОМОЩЬ!!'))
    bot.register_message_handler(my_bot.add_important, func=lambda m: m.text is not None and m.text.startswith('!важно'))
    bot.register_message_handler(my_bot.show_important, func=lambda m: m.text is not None and m.text == 'Важное')
    bot.register_message_handler(my_bot.add_event, func=lambda m: m.text is not None and m.text.startswith('!мероприятие'))
    bot.register_message_handler(my_bot.show_event, func=lambda m: m.text is not None and m.text == 'Мероприятия')
    bot.register_message_handler(my_bot.add_raspisanie, func=lambda m: m.text and m.text.lower().strip().startswith('!расписание'))
    bot.register_message_handler(my_bot.show_raspisanie, func=lambda m: m.text and m.text.strip() == 'Расписание')

  #  @bot.message_handler(func=lambda message: True)
  #  @log_command
  #  def echo_all(message):
  #      try:
  #          bot.send_message(message.chat.id, "Я не понимаю эту команду. Используйте /menu")
  #      except Exception as e:
  #          logger.error(f"Ошибка в echo_all: {e}", exc_info=True)
  #          bot.send_message(message.chat.id, "Произошла ошибка. Администратор уже уведомлён.")

    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)

#if __name__ == '__main__':
#   init()
