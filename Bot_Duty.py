import telebot
import time
import pandas as pd
from array import *

task = []
bot = telebot.TeleBot("508838080:AAGznXL_9EWMGJZroKC0Fg7Z2_4P87PhmTY")

upd = bot.get_updates()
#print(upd)
last_upd = upd[-1]
message_from_user = last_upd.message

@bot.message_handler(commands=['start'])
def handle_text(message):
    bot.send_message(message.from_user.id, 'Здравствуйте! Вас приветствует taskbot. \nЗапись нововой задачи /newtask [Задача] \nПросмотр активных задач /mytasks \nУдаление задачи /deletetask [Номер задачи]')


@bot.message_handler(commands=['time'])
def handle_start_command(message):
    global task
    local_time = time.localtime().tm_wday
    bot.send_message(message.from_user.id, f'{local_time}')
    #print(local_time)

@bot.message_handler(commands=['aix'])
def handle_start_command(message):
    global task
    aix_csv= pd.read_csv("aix.csv")
    #print(aix_csv.loc[[1]])
    work_time = time.localtime().tm_hour
    work_day = time.localtime().tm_wday
    #Так как дежурства с 9 до 9 утра, значит нам надо менять дату дежурств на один день назад, елси время до 9 утра
    if work_day == 0 and work_time<9:
        work_day == 6
    if work_day<5 and work_time<9:
        work_day = work_day-1
    if work_day<4 and work_time<9 or work_time>18:
        aix_duty_name = aix_csv[['Name']].loc[[work_day]]
        aix_duty_name = aix_duty_name.to_string(index = False, header = False)
        aix_duty_phone = aix_csv[['Phone']].loc[[work_day]]
        aix_duty_phone = aix_duty_phone.to_string(index = False, header = False)
        bot.send_message(message.from_user.id, f'{aix_duty_name} \n+{aix_duty_phone} \nЭскалация AIX:/aix_escalation')
    else:
        aix_duty_name = aix_csv[['Name']].loc[[4]]
        aix_duty_name = aix_duty_name.to_string(index = False, header = False)
        aix_duty_phone = aix_csv[['Phone']].loc[[4]]
        aix_duty_phone = aix_duty_phone.to_string(index = False, header = False)
        bot.send_message(message.from_user.id, f'{aix_duty_name} \n+{aix_duty_phone} \nЭскалация AIX:/aix_escalation')

@bot.message_handler(commands=['aix_escalation'])
def handle_start_command(message):
    global task
    aix_csv= pd.read_csv("aix_escalation.csv")
    aix_name = [0 for i in range(5)]
    aix_phone = [0 for i in range(5)]
    aix_text = ''
    for i in range(5):
        aix_duty_name = aix_csv[['Name']].loc[[i]]
        aix_name[i] = aix_duty_name.to_string(index = False, header = False)
        aix_duty_phone = aix_csv[['Phone']].loc[[i]]
        aix_phone[i] = aix_duty_phone.to_string(index = False, header = False)
        aix_phone[i] = ' +'+aix_phone[i]+' \n'
        aix_text = aix_text + aix_name[i] + aix_phone[i]
    bot.send_message(message.from_user.id, f'{aix_text}')


@bot.message_handler(commands=['unix'])
def handle_start_command(message):
    global task
    unix_schedule = pd.read_csv("unix_schedule.csv")


@bot.message_handler(commands=['newtask'])
def handle_start_command(message):
    global task
    if len(message.text) > 9:
        bot.send_message(message.from_user.id, f'Новая задача добавлена')
        task.append(message.text[9:len(message.text)+2])
    else:
        bot.send_message(message.from_user.id, f'Укажите какую задачу добавить в формате /newtask [Ваша задача]')


@bot.message_handler(commands=['mytasks'])
def handle_start_command(message):
    global task
    if len(task) == 0:
        bot.send_message(message.from_user.id, f'Задач нет. Для ввода новой задачи используйте /newtask')
        return

    bot.send_message(message.from_user.id, f'Задачи:')
    for number in range(len(task)):
        bot.send_message(message.from_user.id, f'{number+1}. {task[number]}')

@bot.message_handler(commands=['deletetask'], content_types=['text'])
def handle_start_command(message):
    global task
    bot.send_message(message.from_user.id, f'Задача {message.text[11:len(message.text)+2]} завершена')
    del task[int(message.text[11:len(message.text)+2])-1]


bot.polling(none_stop=True, interval=0)