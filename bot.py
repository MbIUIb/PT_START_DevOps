# /bin/bash
import logging

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
                                   "/get_services - некоторые запущенные сервисы",
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

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возвращает обработчику константу 'ConversationHandler.END',
            сообщающую об окончании диалога
    """

    update.message.reply_text(text=findEmails(update.message.text))
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

        Args:
            update: объект telegram.update.Update.
            context: объект telegram.ext.CallbackContext.

        Returns:
            Возвращает обработчику константу 'ConversationHandler.END',
            сообщающую об окончании диалога
    """

    update.message.reply_text(text=findPhoneNumbers(update.message.text))
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

    command = "service --status-all | grep + | head"
    data = remoteCmdExecutionBySSH(command)
    data = str(data).replace('\\n', '\n')[2:-1]
    update.message.reply_text(data)


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
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmailsAnswer': [MessageHandler(Filters.text & ~Filters.command, findEmailsAnswer)],
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

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
