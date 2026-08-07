"""" БОТ Для классной группы для автоматизации учебного процесса
    Написан Минаевым Денисом
    Проект полностью открыт для всех "Ссылка на гитхаб проект" 
    
    Для тех кто захочет (может с других школ/классов) добавить себе в группу:
    
    id_admins_list = [   Сюда надо записать ID (не юз который на @) того кто сможет добавлять дз или делать что-важное
    ...
    ]

    TOKEN = ...            ЕГО НИКОМУ НЕ ДАВАТЬ И НЕ ПОКАЗЫВАТЬ!!! Сюда вставить токен с бота BotFather

    school_class_letter = ...            Сюда вставить номер и букву класса пример: "1Б"
    
    
    
    
    
"""

import os
import sys
import threading
from tg_bot import *

def console_listener():
  while True:
      terminal_command = input().strip().lower()
      if terminal_command in ['exit', 'q']:
        print('Stoping....')
        bot.stop_polling() 
        break


def main():
  print("Working... q or exit to stop")
  listener_thread = threading.Thread(target=console_listener, daemon=True)
  listener_thread.start()

  init()

if __name__ == '__main__':
  main()
