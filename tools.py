# /bin/bash
import os
import re
import logging

import paramiko
from dotenv import load_dotenv

import psycopg2
from psycopg2 import Error


logging.basicConfig(
        filename='logfile.txt',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


def findPhoneNumbers(text: str):
    """ Осуществляет поиск в тексте телефонных номеров

        Начинается с 8 или +7.
        Подходят следующие шаблоны и некоторые из их комбинаций:
        8XXXXXXXXXX, 8(XXX)XXXXXXX, 8 XXX XXX XX XX,
        8 (XXX) XXX XX XX, 8-XXX-XXX-XX-XX.

        Args:
            text: исходный текст для поиска номеров телефонов.

        Returns:
            Возвращает строку, содержащую список найденных
            телефонных номеров или уведомление об их отсутствии.
            Пример:

            1. +7 090-034-51-21
            2. +7 123-456-78-90
            3. +7 123-456-78-90
    """

    phoneNumRegex = re.compile(r"(8|\+7)[ -]?\(?(\d{3})\)?[ -]?(\d{3})[ -]?(\d{2})[ -]?(\d{2})")
    phoneNumberList = phoneNumRegex.findall(text)

    if phoneNumberList:
        numbersList = []
        for i in range(len(phoneNumberList)):
            numbersList.append((i + 1, "+7 " + '-'.join(phoneNumberList[i][1:])))

        return numbersList
    else:
        return None


def findEmails(text: str):
    """ Осуществляет поиск в тексте email-ов

        Подходят следующие шаблоны:
        mail@mail.com, mail.mail@mail.com, mail.mail.mail@mail.com,
        mail123_mail123@mail.com, ... ,
        mail456-mail789@mail.com, ... .

        Args:
            text: исходный текст для поиска email-ов.

        Returns:
            Возвращает строку, содержащую список найденных
            email-ов или уведомление об их отсутствии.
            Пример:

            1. mn.commbiuib@mn.com
            2. mn.commbiuib@mn.com
            3. mn.comm876biuib@mn.com
    """

    emailRegex = re.compile(r"\w+[-.\w]*@[-.\w]+\.[a-zA-Z]{2,}")
    emailsList = emailRegex.findall(text)

    if emailsList:
        emails = []
        for i in range(len(emailsList)):
            emails.append((i + 1, emailsList[i].strip()))

        return emails
    else:
        return None


def verifyPassword(password: str):
    """ Осуществляет проверку сложности пароля

        Требование к сложному паролю:
        - не менее восьми символов.
        - должен включать как минимум одну заглавную букву (A–Z).
        - должен включать хотя бы одну строчную букву (a–z).
        - должен включать хотя бы одну цифру (0–9).
        - должен включать хотя бы один специальный символ, такой как !@#$%^&*().

        Args:
            password: исходный пароль.

        Returns:
            Возвращает строку, содержащую информацию о надежности пароля.
    """

    if re.match(r'(?=.{8,})(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()])', password):
        return "Пароль сложный!"
    else:
        return "Пароль простой!"


def remoteCmdExecutionBySSH(command: str):
    """ Осуществляет удаленное выполнение команды

        Подключается к серверу по SSH, выполняет заданную команду
        и возврщает ее вывод.

        Args:
            command: команда для удаленного выполнения на сервере.

        Returns:
            Возвращает строку, содержащую вывод команды 'stdout+stderr'
    """

    load_dotenv()
    host = os.getenv("RM_HOST")
    port = int(os.getenv("RM_PORT"))
    username = os.getenv("RM_USER")
    password = os.getenv("RM_PASSWORD")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    return data


def getAllRowFromDBTable(table: str):
    message = ""
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        data = cursor.fetchall()
        for row in data:
            message += f"{row[0]}: {row[1]}\n"
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        message = "Ошибка при работе с PostgreSQL"
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

        return message


def insertInBDTable(table: str, column: str, data: str):
    state = False
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES ('{data}');")
        connection.commit()
        state = True
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

        return state


def rowExistsInBDTable(table: str, column: str, string: str):
    exists = False
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        cursor.execute(f"SELECT exists (SELECT 1 FROM {table} WHERE {column} = '{string}' LIMIT 1);")
        data = cursor.fetchall()
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

        return data[0][0]
