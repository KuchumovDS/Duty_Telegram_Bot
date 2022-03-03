import telebot
import time
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Token, duty_message, unix_escalation, to_email, from_email, email_password, win_escalation, srk_escalation, shd_escalation, tele2_number, tele2_password, Phones
from array import *
from telebot import types
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
import os
from selenium.webdriver.common.by import By
import pickle
from selenium.webdriver.common.keys import Keys

task = []
email_check = 0
bot = telebot.TeleBot(Token)

upd = bot.get_updates()
#print(upd)
#last_upd = upd[-1]
#message_from_user = last_upd.message

@bot.message_handler(commands=['start'])
def handle_text(message):
    bot.send_message(message.from_user.id, 'Здравствуйте! Вас приветствует taskbot. \nЗапись нововой задачи /newtask [Задача] \nПросмотр активных задач /mytasks \nУдаление задачи /deletetask [Номер задачи]')


@bot.message_handler(commands=['time'])
def handle_start_command(message):
    global task
    local_time = time.localtime().tm_wday
    bot.send_message(message.from_user.id, f'{local_time}')
    #print(local_time)

@bot.message_handler(commands=['phone'])
def handle_start_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('Лариса', callback_data=Phones[0])
    item2 = types.InlineKeyboardButton('Руслан', callback_data=Phones[1])
    item3 = types.InlineKeyboardButton('Глеб', callback_data=Phones[2])
    item4 = types.InlineKeyboardButton('Саша', callback_data=Phones[3])
    markup.add(item, item2, item3, item4)
    bot.send_message(message.chat.id, 'Выберите на кого настроить переадресацию', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == 'phone')
def phone_handler(call):
    phone_number = call.data.split(':')[1]
    os.environ['WDM_LOG_LEVEL'] = '0'
    url = "https://msk.tele2.ru/"
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
    try:
        driver.get(url=url)
        time.sleep(1)
        driver.delete_all_cookies()
        for cookie in pickle.load(open(f"cookies_tele2", "rb")):
            driver.add_cookie(cookie)
        driver.get("https://msk.tele2.ru/lk/settings/callforwarding-managment")
        cookie_check = driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/div/div/div/div/div[1]/div/div/div/div/section/header/section[1]/div[3]/div/div/a/span')
        if cookie_check.text == 'Войти':
            #loginbutton = driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/div/div/div/div/div[1]/div/div/div/div/section/header/section[1]/div[3]/div/div/a/span')
            #loginbutton.click()
            #time.sleep(2)
            loginbox = driver.find_element_by_xpath('//*[@id="keycloakAuth.phone"]')
            loginbox.send_keys(tele2_number)
            time.sleep(1)
            loginbutton = driver.find_element_by_xpath('//*[@id="keycloakLoginModal"]/div/div/div/div/div[2]/div/form/div[2]/button')
            loginbutton.click()
            time.sleep(1)
            loginbutton = driver.find_element_by_xpath('//*[@id="keycloakLoginModal"]/div/div/div/div/div[2]/div/div/div[2]/button')
            loginbutton.click()
            time.sleep(1)
            loginbox = driver.find_element_by_xpath('//*[@id="keycloakAuth.password"]')
            loginbox.send_keys(tele2_password)
            time.sleep(1)
            loginbutton = driver.find_element_by_xpath('//*[@id="keycloakLoginModal"]/div/div/div/div/div[2]/div/form/div[2]/button[1]')
            loginbutton.click()
            time.sleep(2)
            pickle.dump(driver.get_cookies(), open(f"cookies_tele2", "wb"))

        driver.get("https://msk.tele2.ru/lk/settings/callforwarding-managment")
        time.sleep(1)
        phonebox = driver.find_element(By.XPATH, '//*[@id="042c52bb8ed236b5eb5b22ecea0e4753"]')
        phonebox.clear()
        time.sleep(1)
        phonebox.send_keys(phone_number)
        time.sleep(1)
        acceptbutton = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div/div/div[2]/div/div/div[2]/section/div/div[7]/button[1]')
        acceptbutton.click()
        time.sleep(2)

        xpath_try1 = driver.find_elements(By.XPATH, "//*[text()='Настройки сохранены.']")
        if not xpath_try1:
            print("null")
            errorbox = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div/div/div[2]/div/div/div[2]/section/p[2]')
            errorbox = errorbox.text
            bot.send_message(call.from_user.id, f'{errorbox}')
        else:
            print("nonull")
            bot.send_message(call.from_user.id, f'Переадресация выполнена\nПросьба проверить +7{tele2_number}')
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()




@bot.message_handler(commands=['aix'])
def handle_start_command(message):
    global task
    aix_csv= pd.read_csv("aix.csv")
    #print(aix_csv.loc[[1]])
    work_time = time.localtime().tm_hour
    work_day = time.localtime().tm_wday
    #Так как дежурства с 9 до 9 утра, значит нам надо менять дату дежурств на один день назад, елси время до 9 утра
    if work_day == 0 and work_time<9:
        work_day = 6
    if work_day<5 and work_time<9:
        work_day = work_day-1
    if work_day<4 and (work_time<9 or work_time>17):
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
    unix_csv = pd.read_csv("unix.csv")
    work_time = time.localtime().tm_hour
    #work_time = 9
    work_day = time.localtime().tm_wday
    month_day = time.localtime().tm_mday
    #duty_check = unix_schedule.isin({'{month_day}': ['X']})

    if work_day<5 and work_time>4 and work_time<9:
        if (work_day % 2) == 0:
            #duty_unix=unix_schedule.loc[unix_schedule[f'Name']=='Холстинин Вячеслав Владимирович',['ФИО']].to_string(index = False, header = False)
            duty_unix = 'Холстинин Вячеслав Владимирович'
            unix_phone = unix_csv.loc[unix_csv['Name']==duty_unix, ['Phone']].to_string(index = False, header = False)
            bot.send_message(message.from_user.id, f'{duty_unix} \n+{unix_phone} \nЭскалация Unix: /unix_escalation')
        else:
            #duty_unix=unix_schedule.loc[unix_schedule[f'Name']=='Челмаев-Суриков Арсений Валерьевич',['ФИО']].to_string(index = False, header = False)
            duty_unix = 'Челмаев-Суриков Арсений Валерьевич'
            unix_phone = unix_csv.loc[unix_csv['Name']==duty_unix, ['Phone']].to_string(index = False, header = False)
            bot.send_message(message.from_user.id, f'{duty_unix} \n+{unix_phone} \nЭскалация Unix :/unix_escalation')
    else:
        if work_time < 5:
            work_day = work_day -1

        duty_unix=unix_schedule.loc[unix_schedule[f'{month_day}']=='X',['ФИО']].to_string(index = False, header = False)
        unix_phone = unix_csv.loc[unix_csv['Name']==duty_unix, ['Phone']].to_string(index = False, header = False)
        bot.send_message(message.from_user.id, f'{duty_unix} \n+{unix_phone} \nЭскалация Unix: /unix_escalation')

@bot.message_handler(commands=['unix_escalation'])
def handle_start_command(message):
    global task
    #unix_csv = pd.read_csv("unix.csv")
    #unix_escalation = unix_csv.to_string(index = False, header = False)
    bot.send_message(message.from_user.id, f'{unix_escalation}')

@bot.message_handler(commands=['duty'])
def handle_start_command(message):
    global task
    bot.send_message(message.from_user.id, f'{duty_message}')

#@bot.message_handler(commands=['email'])
#def handle_start_command(message):
#    global email_check
#    bot.send_message(message.from_user.id, 'Введите текст для отправки по почте')
#    email_check = 1

@bot.message_handler(commands=['win_escalation'])
def handle_start_command(message):
        bot.send_message(message.from_user.id, f'{win_escalation}')

@bot.message_handler(commands=['srk_escalation'])
def handle_start_command(message):
        bot.send_message(message.from_user.id, f'{srk_escalation}')

@bot.message_handler(commands=['shd_escalation'])
def handle_start_command(message):
        bot.send_message(message.from_user.id, f'{shd_escalation}')






@bot.message_handler(content_types=['text'])
def email_send(email_message):
    message = email_message.text
    msg = MIMEMultipart()
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(from_email, email_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    bot.send_message(email_message.from_user.id, 'Отправлено на почту дежурных')





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
        bot.send_message(message.from_user.id, f'Задач нет. Для ввода новой задачи используйте ///newtask')
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