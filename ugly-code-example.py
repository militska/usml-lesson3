#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika
import os
import sys
import json
import syslog
import time
import re
import requests
from threading import Thread
from Mail import Mail
from Telegram import Telegram
from TelegramApi import telegram_api
from corporateDB import corporateDB
from handler import handler
from Sms import Sms


def Supervisor(thr_list):
    thr = []

    while True:
        i = 0
        for thread_name in thr_list:
            if not thr[i] or not thr[i].is_alive():
                thr[i] = Thread(target=thread_name)
                thr[i].daemon = True
                thr[i].start()
                syslog.syslog("Starting thread for: %s" % str(thread_name))
            thr[i].join(1)
            i = i + 1

        time.sleep(10)


def db_process_one(row):
    if not row:
        return False
    zhost = row[7]

    try:
        connection = dbModule.Connection("db_login/db_pass")
    except dbModule.DatabaseError as exc:
        syslog.syslog("DB connection error: %s" % exc)
        return False

    try:
        cursor = connection.cursor()
        statTT = cursor.var(dbModule.STRING, 255)
        result = cursor.var(dbModule.NUMBER, 255)
        numTT = cursor.var(dbModule.NUMBER, 255)
        cursor.prepare("""BEGIN;
            procedure_one(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11);
        ); END;""")
        row.append(result)
        row.append(numTT)
        row.append(statTT)
        cursor.execute(None, row)
        connection.commit()
        cursor.close()
        syslog.syslog("Insert data to db: %s" % row[0])
    except Exception as exc:
        syslog.syslog("Error while inserting to db: %s" % exc)
        return False

    event_num = re.search("\s*([0-9]+)", row[6]).group(1)
    resultTT = (int(row[-3].getvalue()),
                int(row[-2].getvalue()), str(row[-1].getvalue()))

    syslog.syslog("Prepare ack one: %s" % row)
    return (zhost, event_num, resultTT)


def db_process_two(row):
    if not row:
        return False
    zhost = row[7]
    try:
        connection = dbModule.Connection("db_login/db_pass")
    except dbModule.DatabaseError as exc:
        syslog.syslog("DB connection error: %s" % exc)
        return False

    try:
        cursor = connection.cursor()
        statTT = cursor.var(dbModule.STRING, 255)
        result = cursor.var(dbModule.NUMBER, 255)
        numTT = cursor.var(dbModule.NUMBER, 255)
        cursor.prepare("""BEGIN
        procedure_two(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11);
        END;""")
        row.append(result)
        row.append(numTT)
        row.append(statTT)
        cursor.execute(None, row)
        connection.commit()
        cursor.close()
        syslog.syslog("Insert data to db: %s" % row[0])
    except Exception as exc:
        syslog.syslog("Error while inserting to db: %s" % exc)
        return False

    syslog.syslog(str(row))
    event_num = re.search("\s*([0-9]+)", row[3]).group(1)
    event_reg_num = row[-2].getvalue()
    if event_reg_num == None:
        event_reg_num = 0
    event_reg_status = str(row[-1].getvalue())
    resultTT = (int(event_reg_num), event_reg_status)
    syslog.syslog("Prepare ack two: %s" % row)
    return (zhost, event_num, resultTT)


def db_process_three(row):
    if not row:
        return False
    try:
        connection = dbModule.Connection("db_login/db_pass")
    except dbModule.DatabaseError as exc:
        syslog.syslog("DB connection error: %s" % exc)
        return False

    try:
        cursor = connection.cursor()
        cursor.prepare("""BEGIN;
            procedure_three(:1, :2, :3);
            END;""")
        cursor.execute(None, row)
        connection.commit()
        syslog.syslog("Insert data to db: %s" % row[0])
    except Exception as exc:
        syslog.syslog("Error while inserting to db: %s" % exc)
        return False

    return True


def start_consume_one():
    start_consume('queue_one', callback_one, {"x-priority": 5})


def start_consume_two():
    start_consume('queue_two', callback_two)


def start_consume_three():
    start_consume('queue_three', callback_three)


# def start_consume(queue_params, consume_params):
def start_consume(queue_name, calllback, arguments=None):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )

        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_consume(calllback, queue=queue_name, no_ack=False,
                              arguments)  # вот тут может быть что то сильно не так

        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()
    except Exception as exc:
        channel.stop_consuming()
        syslog.syslog("Error while consuming queue three: %s" % str(exc))

    connection.close()
    sys.exit(1)


def start_consume_mail():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )

        channel = connection.channel()
        channel.queue_declare(queue='queue_mail', durable=True)
        channel.basic_consume(callback_mail,
                              queue='queue_mail',
                              no_ack=True)

        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()
    except Exception as exc:
        channel.stop_consuming()
        syslog.syslog("Error while consuming queue mail: %s" % str(exc))

    connection.close()
    sys.exit(1)


def start_consume_sms():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )

        channel = connection.channel()
        channel.queue_declare(queue='queue_sms', durable=True)
        channel.basic_consume(callback_sms,
                              queue='queue_sms',
                              no_ack=True
                              )

        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()
    except Exception as exc:
        channel.stop_consuming()
        syslog.syslog("Error while consuming queue sms: %s" % str(exc))
    connection.close()
    sys.exit(1)


def start_consume_telegram():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )

        channel = connection.channel()
        channel.queue_declare(queue='queue_tlgrm', durable=True)
        channel.basic_consume(callback_telegram,
                              queue='queue_tlgrm',
                              no_ack=True
                              )

        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()
    except Exception as exc:
        channel.stop_consuming()
        syslog.syslog("Error while consuming queue tlgrm: %s" % str(exc))

    connection.close()
    sys.exit(1)







def create_one(body_msg):
    tt = json.loads(body_msg)

    try:
        row = [
            tt['hostname'].encode('utf-8'),
            tt['hostname'].encode('utf-8'),
            tt['state-trigger'].encode('utf-8'),
            "Автоматически создано \nevent: " +
            str(tt['event'].encode('utf-8')),
            tt['check-type'].encode('utf-8'),
            int(tt['trigger']),
            tt['message'].encode('utf-8'),
            tt.get('zhost', 'some.host').encode('utf-8')
        ]

        syslog.syslog('Message: {} {} {}'.format(tt['hostname'].encode(
            'utf-8'), tt['message'].encode('utf-8'), tt['state-trigger'].encode('utf-8')))
        return row
    except Exception as exc:
        syslog.syslog("Error while creating: %s" % exc)
        return False


def create_two(body_msg):
    tt = json.loads(body_msg)
    try:
        row = [
            tt['hostname'].encode('utf-8'),
            tt['ip-address'].encode('utf-8'),
            tt['state-trigger'].encode('utf-8'),
            tt['message'].encode('utf-8'),
            tt['comment'].encode('utf-8'),
            tt['trigger'].encode('utf-8'),
            "Автоматически создано " +
            tt['prefix'].encode('utf-8') + "\nevent: " +
            tt['event'].encode('utf-8'),
            tt.get('zhost', 'some.host').encode('utf-8')
        ]

        syslog.syslog('Message: {} {} {}'.format(tt['hostname'].encode(
            'utf-8'), tt['message'].encode('utf-8'), tt['state-trigger'].encode('utf-8')))
        return row
    except Exception as exc:
        syslog.syslog("Error while creating: %s" % exc)
        return False


def create_three(body_msg):
    tt = json.loads(body_msg)
    try:
        row = [tt['hostname'].encode(
            'utf-8'), tt['state-trigger'].encode('utf-8'), tt['trigger'].encode('utf-8')]

        syslog.syslog('Three message: {} {} {}'.format(tt['hostname'].encode(
            'utf-8'), tt['message'].encode('utf-8'), tt['state-trigger'].encode('utf-8')))
        return row
    except Exception as exc:
        syslog.syslog("Error while creating: %s" % (exc))
        return False


def event_update(data):
    if not data:
        return False
    zhost, evid, NumTT = data

    server = 'server'
    if zhost == 'server2':
        server = 'server2'

    login = 'event_login'
    password = 'event_password'

    s = requests.Session()
    s.auth = (login, password)

    return True




def callback_one(ch, method, properties, body):
    row = create_one(body)
    db_result = db_process_one(row)
    result = event_update(db_result)
    if result:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)


def callback_two(ch, method, properties, body):
    row = create_two(body)
    db_result = db_process_two(row)
    result = event_update(db_result)
    if result:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)


def callback_three(ch, method, properties, body):
    row = create_three(body)
    db_result = db_process_three(row)
    if db_result:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)


def callback_sms(ch, method, properties, body):
    Sms.send(body)


def callback_telegram(ch, method, properties, body):
    Telegram.send(body)


def callback_mail(ch, method, properties, body):
    Mail.send(body)



if __name__ == "__main__":
    syslog.openlog('some_tag', syslog.LOG_PID, syslog.LOG_NOTICE)

    try:
        thr_list = [
            start_consume_one,
            start_consume_two,
            start_consume_three,
            start_consume_mail,
            start_consume_sms,
            start_consume_telegram
        ]

        for n in ["queue_Tgm_1", "queue_tlgrm"]:
            t = handler(n)
            thr_list.append(t.start_consume)

        Supervisor(thr_list)

    except KeyboardInterrupt:
        print("EXIT")
        raise
