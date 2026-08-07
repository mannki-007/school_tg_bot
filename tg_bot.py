from json_storage import *
import telebot
from telebot import types
import os
from datetime import datetime
import re

TOKEN = 'СЮДА_ТВОЙ_ТОКЕН'



bot = telebot.TeleBot(TOKEN)

#ID Одноклассников,но будь внимательней,это не Username который начинается на @,узнать его можно в спец боте
id_admins_list = [

]


school_class_letter = "9A"



"""                                                                  \n - перенос на новую строку
                                                                                `` - косой щрифт
                                                                                **** - жирный шрифт
                                                                            
"""

class my_bot:
    @staticmethod # staticmethod для того чтобы не писать селф каждый раз
    def show_menu(message):
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      btn1 = types.KeyboardButton('Расписание')   #  набор кнопок
      btn2 = types.KeyboardButton('ДЗ')
      btn3 = types.KeyboardButton('Важное')
      btn4 = types.KeyboardButton('Мероприятия')
      btn5 = types.KeyboardButton('История ДЗ')
      btn6 = types.KeyboardButton('ПОМОЩЬ!!')

      markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
      bot.send_message(
          message.chat.id, 'Выберите действие:', reply_markup=markup
      )
    @staticmethod
    def start(message):
        #print(f'Я бот для группы твоего класса', school_class, school_class_letter)
        text = f'Привет,я бот 🤖 для группы {school_class_letter} класса'
        bot.reply_to(message, text)

    @staticmethod
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


        ' **Админам:**\n'
        '`!дз <текст>` — обновить ДЗ\n'
        '`!важно <текст>` — обновить объявление\n'
        '**АДМИНЫ** \n'
        f' {admins_text} '
            )
        bot.reply_to(message, text, parse_mode='Markdown')

    @staticmethod
    def add_dz(message):
        user_id = message.from_user.id
        if user_id not in id_admins_list:
            bot.reply_to(message, "Ты не состоишь в списке администраторов,ты не можешь редактировать Д/З", parse_mode='Markdown')
            return
        
        new_dz = message.text[4:].strip()

        if not new_dz:
            bot.reply_to(message, "Напиши текст Д/З после команды. Пример: `!дз математика стр 5`", parse_mode='Markdown')
            return
        data = load_data()
        now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
        data['dz_history'].append({'timestamp': now_str, 'text': new_dz})
        save_data(data)
        bot.reply_to(
            message,
            f'✅ **Д/З обновлено ({now_str}):**\n{new_dz}',
            parse_mode='Markdown',
        )

    @staticmethod
    def show_dz(message):
        data = load_data()
        history = data.get('dz_history', [])

        if not history:
            bot.reply_to(message, 'Д/З пока не задано.')
            return

        last_entry = history[-1]
        text = f"**🕐 Актуальное Д/З** (от {last_entry['timestamp']}):\n\n{last_entry['text']}"

        bot.reply_to(message, text, parse_mode='Markdown')


    @staticmethod
    def show_dz_history(message):
        data = load_data()
        history = data.get('dz_history', [])

        if not history:
            bot.reply_to(message, '🌵 История Д/З пуста.')
            return

        recent = history[-5:][::-1]
        lines = []
        for item in recent:
            lines.append(f"📌 **{item['timestamp']}**\n{item['text']}\n")

        text = '📜 **История последних обновлений Д/З:**\n\n' + '\n'.join(lines)
        bot.reply_to(message, text, parse_mode='Markdown')



    @staticmethod
    def add_important(message):
      user_id = message.from_user.id
      if user_id not in id_admins_list:
        bot.reply_to(
            message,
            'Ты не состоишь в списке администраторов!',
            parse_mode='Markdown',
        )
        return

      text = message.text[7:].strip()  # Отрезаем '!важно '
      if not text:
        bot.reply_to(
            message,
            'Напиши текст после команды. Пример: `!важно Завтра сокращенный день`',
            parse_mode='Markdown',
        )
        return

      data = load_data()
      now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
      data.setdefault('vazhnoe_history', []).append(
          {'timestamp': now_str, 'text': text}
      )
      save_data(data)

      bot.reply_to(
          message,
          f'🚨 **Важное объявление обновлено ({now_str}):**\n{text}',
          parse_mode='Markdown',
      )

    @staticmethod
    def show_important(message):
      data = load_data()
      history = data.get('vazhnoe_history', [])

      if not history:
        bot.reply_to(message, '🔔 Важных объявлений пока нет.')
        return

      last_entry = history[-1]
      text = f"🚨 **Важное объявление** (от {last_entry['timestamp']}):\n\n{last_entry['text']}"
      bot.reply_to(message, text, parse_mode='Markdown')

    @staticmethod
    def add_event(message):
      user_id = message.from_user.id
      if user_id not in id_admins_list:
        bot.reply_to(
            message,
            'Ты не состоишь в списке администраторов!',
            parse_mode='Markdown',
        )
        return

      text = message.text[12:].strip()  
      if not text:
        bot.reply_to(
            message,
            'Напиши текст после команды. Пример: `!мероприятие В пятницу поход в музей`',
            parse_mode='Markdown',
        )
        return

      data = load_data()
      now_str = datetime.now().strftime('%d.%m.%Y %H:%M')
      data.setdefault('meropriyatiya_history', []).append(
          {'timestamp': now_str, 'text': text}
      )
      save_data(data)

      bot.reply_to(
          message,
          f'🎉 **Мероприятие добавлено ({now_str}):**\n{text}',
          parse_mode='Markdown',
      )



    """      'dz_history': [],
        'vazhnoe_history': [],
        'meropriyatiya_history': [],
        'raspisanie': {},
    """


    @staticmethod
    def show_event(message):
      data = load_data()
      history = data.get('meropriyatiya_history', [])

      if not history:
        bot.reply_to(message, '🎉 Ближайших мероприятий не запланировано.')
        return

      last_entry = history[-1]
      text = f"🎉 **Ближайшее мероприятие** (от {last_entry['timestamp']}):\n\n{last_entry['text']}"
      bot.reply_to(message, text, parse_mode='Markdown')


    @staticmethod
    def add_raspisanie(message):
      user_id = message.from_user.id
      if user_id not in id_admins_list:
        bot.reply_to(message, 'Ты не админ!')
        return

      raw_text = message.text or ''

      if len(raw_text) <= 11:
        bot.reply_to(message, 'Пусто! Напиши расписание после команды.')
        return

      schedule_body = raw_text[11:].strip()

      data = load_data()
      data['raspisanie'] = schedule_body
      save_data(data)

      bot.reply_to(
          message,
          f'📅 **Расписание записано:**\n\n{schedule_body}',
          parse_mode='Markdown',
      )

    @staticmethod
    def show_raspisanie(message):
      data = load_data()
      schedule_text = data.get('raspisanie', '')

      if not schedule_text:
        bot.reply_to(message, '📅 Расписание пока не заполнено.')
        return

      text = f'📅 **Школьное расписание:**\n\n{schedule_text}'
      bot.reply_to(message, text, parse_mode='Markdown')
                        
                    

            
            
    

def init():
    bot.register_message_handler(my_bot.start, commands=['start'])
    bot.register_message_handler(my_bot.show_menu, commands=['menu'])
    bot.register_message_handler(
      my_bot.add_dz,
      func=lambda m: m.text is not None and m.text.startswith('!дз'),
  )
    bot.register_message_handler(
      my_bot.show_dz,
      func=lambda m: m.text is not None and m.text.startswith('ДЗ'),
)
    bot.register_message_handler(
      my_bot.show_dz_history,
      func=lambda m: m.text is not None and m.text.startswith('История ДЗ'),
  )
    bot.register_message_handler(
      my_bot.help,
      func=lambda m: m.text is not None and m.text.startswith('ПОМОЩЬ!!'),
  )
    bot.register_message_handler(
      my_bot.add_important,
      func=lambda m: m.text is not None and m.text.startswith('!важно'),
        )
    bot.register_message_handler(
        my_bot.show_important,
        func=lambda m: m.text is not None and m.text == 'Важное',
)
    bot.register_message_handler(
        my_bot.add_event,
        func=lambda m: m.text is not None and m.text.startswith('!мероприятие'),
    )
    bot.register_message_handler(
        my_bot.show_event,
        func=lambda m: m.text is not None and m.text == 'Мероприятия',
    )

    bot.register_message_handler(
            my_bot.add_raspisanie,
            func=lambda m: m.text
            and m.text.lower().strip().startswith('!расписание'),
        )
    bot.register_message_handler(
            my_bot.show_raspisanie,
            func=lambda m: m.text and m.text.strip() == 'Расписание',
        )


    
    bot.infinity_polling(skip_pending=True)



    
