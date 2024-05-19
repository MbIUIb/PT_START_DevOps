# /bin/bash
import logging
from uuid import uuid4

from telegram import Update
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext

from tools import *


def startCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю приветственное сообщение

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю список доступных команд

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    update.message.reply_text(text="<b>Общее</b>\n"
                                   "/start - начало работы с ботом\n"
                                   "/help - вывод списка команд\n"
                                   "\n<b>Поиск по тексту</b>\n"
                                   "/find_email - поиск всевозможных email в вашем сообщении\n"
                                   "/find_phone_number - поиск всех номеров в вашем сообщении\n"
                                   "/verify_password - анализ сложности вашего пароля\n"
                                   "\n<b>Информация о сервере</b>\n"
                                   "/get_release - информация о релизе\n"
                                   "/get_uname - сведения о системе\n"
                                   "/get_uptime - время работы\n"
                                   "/get_df - сведения о файловой системе\n"
                                   "/get_free - состояние RAM\n"
                                   "/get_mpstat - информация о производительности системы\n"
                                   "/get_w - Информация о работающих пользователях\n"
                                   "/get_auths - 10 последних авторизаций в системе\n"
                                   "/get_critical - 5 последних критических событий\n"
                                   "/get_ps - запущенные процессы\n"
                                   "/get_ss - используемые порты\n"
                                   "/get_apt_list *args - информация об установленных пакетах\n"
                                   "/get_services - некоторые запущенные сервисы\n"
                                   "\n<b>База данных</b>\n"
                                   "/get_repl_logs - логи о репликации БД\n"
                                   "/get_emails - вывод email-ов из БД\n"
                                   "/get_phone_numbers - вывод телефонных номеров\n",
                              parse_mode="HTML")


def echo(update: Update, context: CallbackContext):
    """Отправляет эхо-ответы на сообщения не являющиеся командами"""

    update.message.reply_text(update.message.text)


def findEmailsCommand(update: Update, context: CallbackContext):
    """ Запрашивает текст для поиска в ответ на команду '/find_email'.

        Является первым этапом диалога в процессе которого пользователю
        отправляется сообщение со списком всех найденных email-ов
        или сообщение об их отсутствии.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возврщает обработчику строку-состояние 'findEmailsAnswer'
    """

    update.message.reply_text(text="Введите текст для поиска email-ов")
    return "findEmailsAnswer"


def findEmailsAnswer(update: Update, context: CallbackContext):
    """ Отправляет пользователю список найденных email-ов.

        Является вторым этапом диалога в процессе которого пользователю
        отправляется сообщение со списком всех найденных email-ов
        или сообщение об их отсутствии.
        Проверяет найденные email на предмет их наличия в БД и
        предлагает записать отсутствующие в записях.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возврщает обработчику строку-состояние 'findEmailsBDAnswer'
    """

    message = ""
    emails = findEmails(update.message.text)
    context.user_data['emails'] = emails
    notInBD = False

    if emails:

        for emailNumber, email in emails:
            if rowExistsInBDTable("emails", "email", email):
                message += f"✓ {emailNumber}: {email}\n"
            else:
                message += f"✕ {emailNumber}: {email}\n"
                notInBD = True

    else:
        message = "Email-ы не найдены!"

    if notInBD:
        message += "\nДобавить новые email-ы в БД?\n[Да/Нет]"
        update.message.reply_text(text=message)
        return "findEmailsBDAnswer"
    else:
        message += "\nВсе Email-ы есть в БД"
        update.message.reply_text(text=message)
        return ConversationHandler.END


def findEmailsBDAnswer(update: Update, context: CallbackContext):
    """ Производит запись email-ов в БД в случае согласия и уведомляет пользователя

        Является третьим этапом диалога в процессе которого пользователю
        отправляется сообщение со списком всех найденных email-ов
        или сообщение об их отсутствии.
        Записывает отсутствующие в БД email-ы при согласии пользователя.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возвращает обработчику константу 'ConversationHandler.END',
            сообщающую об окончании диалога
    """

    message = "Произошла ошибка!"
    if update.message.text == "Да":
        emails = context.user_data['emails']

        if emails:
            for emailNumber, email in emails:
                if not rowExistsInBDTable("emails", "email", email):
                    if insertInBDTable('emails', 'email', email):
                        message = "Email-ы успешно добавлены"
                    else:
                        message = "Произошла ошибка при работе с PostgreSQL"
    else:
        message = "Спасибо, что пользуетесь нашим сервисом!"

    update.message.reply_text(text=message)
    return ConversationHandler.END


def findPhoneNumbersCommand(update: Update, context: CallbackContext):
    """ Запрашивает текст для поиска в ответ на команду '/find_phone_number'.

        Является первым этапом диалога в процессе которого пользователю
        отправляется сообщение со списком всех найденных телефонных
        номеров или сообщение об их отсутствии.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возврщает обработчику строку-состояние 'findPhoneNumbersAnswer'
    """

    update.message.reply_text(text="Введите текст для поиска номеров телефонов")
    return "findPhoneNumbersAnswer"


def findPhoneNumbersAnswer(update: Update, context: CallbackContext):
    """ Отправляет список найденных телефонных номеров.

        Является вторым этапом диалога в процессе которого пользователю
        отправляется сообщение со списком всех найденных телефонных
        номеров или сообщение об их отсутствии.
        Проверяет найденные телефонные номера на предмет их наличия в
        БД и предлагает записать отсутствующие в записях.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возвращает обработчику константу 'ConversationHandler.END',
            сообщающую об окончании диалога
    """

    message = ""
    phoneNumbers = findPhoneNumbers(update.message.text)
    context.user_data['phoneNumbers'] = phoneNumbers
    notInBD = False

    if phoneNumbers:
        for phoneNumberNumber, phoneNumber in phoneNumbers:
            if rowExistsInBDTable("numbers", "number", phoneNumber):
                message += f"✓ {phoneNumberNumber}: {phoneNumber}\n"
            else:
                message += f"✕ {phoneNumberNumber}: {phoneNumber}\n"
                notInBD = True

    else:
        message = "Телефонные номера не найдены!"

    if notInBD:
        message += "\nДобавить новые телефонные номера в БД?\n[Да/Нет]"
        update.message.reply_text(text=message)
        return "findPhoneNumbersBDAnswer"
    else:
        message += "\nВсе телефонные номера есть в БД"
        update.message.reply_text(text=message)
        return ConversationHandler.END


def findPhoneNumbersBDAnswer(update: Update, context: CallbackContext):
    """ Производит запись телефонных номеров в БД в случае согласия и уведомляет пользователя

        Является третьим этапом диалога в процессе которого пользователю
        отправляется сообщение со списком всех найденных телефонных номеров
        или сообщение об их отсутствии.
        Записывает отсутствующие в БД телефонные номера при согласии
        пользователя.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возвращает обработчику константу 'ConversationHandler.END',
            сообщающую об окончании диалога
    """

    message = "Произошла ошибка!"
    if update.message.text == "Да":
        phoneNumbers = context.user_data['phoneNumbers']

        if phoneNumbers:
            for phoneNumberNumber, phoneNumber in phoneNumbers:
                if not rowExistsInBDTable("numbers", "number", phoneNumber):
                    if insertInBDTable("numbers", "number", phoneNumber):
                        message = "Телефонные номера успешно добавлены"
                    else:
                        message = "Произошла ошибка при работе с PostgreSQL"
    else:
        message = "Спасибо, что пользуетесь нашим сервисом!"

    update.message.reply_text(text=message)
    return ConversationHandler.END


def verifyPasswordCommand(update: Update, context: CallbackContext):
    """ Запрашивает пароль для проверки в ответ на команду '/verify_password'.

        Является первым этапом диалога в процессе которого пользователю
        отправляется уведомление о надежности пароля.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возврщает обработчику строку-состояние 'verifyPasswordAnswer'
    """

    update.message.reply_text(text="Введите пароль")
    return "verifyPasswordAnswer"


def verifyPasswordAnswer(update: Update, context: CallbackContext):
    """ Отправляет пользователю сообщение о надежности пароля.

        Является вторым этапом диалога в процессе которого пользователю
        отправляется уведомление о надежности пароля.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возвращает обработчику константу 'ConversationHandler.END',
            сообщающую об окончании диалога
    """

    update.message.reply_text(text=verifyPassword(update.message.text))
    return ConversationHandler.END


def getReleaseCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о релизе

        Отправляет сообщение, содержащее вывод команды 'uname -r'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "uname -r"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getUnameCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о системе

        Отправляет сообщение, содержащее вывод команды 'uname -pnv'
        удаленного сервера в удобном формате.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    processorVersion = str(remoteCmdExecutionBySSH("uname -p")).replace('\\n', '\n')[2:-1]
    hostname = str(remoteCmdExecutionBySSH("uname -n")).replace('\\n', '\n')[2:-1]
    kernelVersion = str(remoteCmdExecutionBySSH("uname -v")).replace('\\n', '\n')[2:-1]

    data = (f"Версия роцессора: {processorVersion}"
            f"Имя хоста: {hostname}"
            f"Версия ядра: {kernelVersion}")
    update.message.reply_text(data)


def getUptimeCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о времени работы системы

        Отправляет сообщение, содержащее вывод команды 'uptime -p'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "uptime -p"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getDfCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о состоянии файловой системы

        Отправляет сообщение, содержащее вывод команды 'df'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "df"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)


def getFreeCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о состоянии ОЗУ

        Отправляет сообщение, содержащее вывод команды 'free -h'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "free -h"
    data = remoteCmdExecutionBySSH(command)
    data = 'ram' + str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getMpstatCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о производительности системы

        Отправляет сообщение, содержащее вывод команды 'mpstat'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "mpstat"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getWCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о работающих в системе пользователях

        Отправляет сообщение, содержащее вывод команды 'w'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "w"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getAuthsCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о 10 последних входах в систему

        Отправляет сообщение, содержащее вывод команды 'last -n 10'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "last -n 10"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getCriticalCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о 5 последних критических событиях

        Отправляет сообщение, содержащее вывод команды 'journalctl -p crit -n 5'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "journalctl -p crit -n 5"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getPsCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о некоторых запущенных процессах

        Отправляет сообщение, содержащее вывод команды 'ps | head'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "ps | head"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getSsCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о некоторых используемых портах

        Отправляет сообщение, содержащее вывод команды 'ss | head'
        удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "ss | head"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getAptListCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию об установленных пакетах

        В случае команды /get_apt_list без аргументов отправляет
        сообщение, содержащее вывод команды 'apt list | head'
        удаленного сервера. При наличии аргуметов, содержащих
        газвания пакетов отправляет информацию о них из команды
        'apt show packetName'.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    data = ""
    if context.args:
        injectionSymbols = ['|', '&']
        for packet in context.args:
            if any(injectionSymbol in packet for injectionSymbol in injectionSymbols):
                data += f"INCORRECT PACKAGE NAME: {packet}\n"
            else:
                command = f"apt show {packet}"
                tmpData = remoteCmdExecutionBySSH(command)
                tmpData = str(tmpData).replace('\\n', '\n')[2:-1]

                data += tmpData

        update.message.reply_text(data)
    else:
        command = "apt list | head"
        data = remoteCmdExecutionBySSH(command)
        data = str(data).replace('\\n', '\n')[2:-1]
        update.message.reply_text(data)


def getServicesCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю информацию о некоторых запущенных сервисах

        Отправляет сообщение, содержащее вывод команды
        'service --status-all | grep + | head' удаленного сервера.

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "systemctl list-units --type service --state running | head"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getReplLogCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю логи о репликации БД

        Отправляет сообщение, содержащее вывод команды
        'cat /var/log/postgresql/*.log | grep repl_user | hea'
        удаленного сервера. Нужны права на чтение для ssh пользователя:
        'sudo chmod o+r /var/log/postgresql/postgresql-15-main.log'

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.
    """

    command = "cat /var/log/postgresql/*.log | grep -i repl | tail -n 20"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


def getEmailsCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю список email-ов из базы данных

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возврщает обработчику строку-состояние 'findEmailsAnswer'
    """

    update.message.reply_text(text=getAllRowFromDBTable("emails"))


def getPhoneNumbersCommand(update: Update, context: CallbackContext):
    """ Отправляет пользователю список телефонных номеров из базы данных

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возврщает обработчику строку-состояние 'findPhoneNumbersAnswer'
    """

    update.message.reply_text(text=getAllRowFromDBTable("numbers"))


def main():
    # включаем логирование
    logging.basicConfig(
        filename='logfile.txt',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    # подключаем переменные окружения
    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики диалогов
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbersAnswer': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbersAnswer)],
            'findPhoneNumbersBDAnswer': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbersBDAnswer)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmailsAnswer': [MessageHandler(Filters.text & ~Filters.command, findEmailsAnswer)],
            'findEmailsBDAnswer': [MessageHandler(Filters.text & ~Filters.command, findEmailsBDAnswer)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPasswordAnswer': [MessageHandler(Filters.text & ~Filters.command, verifyPasswordAnswer)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", startCommand))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", getReleaseCommand))
    dp.add_handler(CommandHandler("get_uname", getUnameCommand))
    dp.add_handler(CommandHandler("get_uptime", getUptimeCommand))
    dp.add_handler(CommandHandler("get_df", getDfCommand))
    dp.add_handler(CommandHandler("get_free", getFreeCommand))
    dp.add_handler(CommandHandler("get_mpstat", getMpstatCommand))
    dp.add_handler(CommandHandler("get_w", getWCommand))
    dp.add_handler(CommandHandler("get_auths", getAuthsCommand))
    dp.add_handler(CommandHandler("get_critical", getCriticalCommand))
    dp.add_handler(CommandHandler("get_ps", getPsCommand))
    dp.add_handler(CommandHandler("get_ss", getSsCommand))
    dp.add_handler(CommandHandler("get_apt_list", getAptListCommand))
    dp.add_handler(CommandHandler("get_services", getServicesCommand))
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogCommand))
    dp.add_handler(CommandHandler("get_emails", getEmailsCommand))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbersCommand))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
