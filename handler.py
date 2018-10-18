
class handler:
    def __init__(self, queue):
        self.queue = queue

        if queue == "queue_Tgm_1":
            self.notify = self.telegram
        elif queue == "queue_tlgrm":
            self.notify = self.psevdo_telegram
        else:
            self.notify = self.default

        self.params = {"telegram": {"token": "id:token",
                                    "base_url": "https://api.telegram.org/bot",
                                    'proxy': {
                                        'ip': '0.0.0.0',
                                        'port': 9999, 'user': 'some_user', 'password': 'some_password'}},
                       "to_db": {'url_in': 'some url in'}}

    def start_consume(self):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
            channel = connection.channel()

            channel.queue_declare(queue=self.queue, durable=True)
            channel.basic_consume(self.callback,
                                  queue=self.queue,
                                  no_ack=False, exclusive=False)
            channel.basic_qos(prefetch_count=1)
            channel.start_consuming()
        except Exception as exc:
            # channel.stop_consuming()
            syslog.syslog("Error while consuming %s queue: %s" %
                          (self.queue, str(exc)))
        connection.close()
        sys.exit(1)

        connection.close()

    def callback(self, ch, method, properties, body):
        if self.notify(body):
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def default(self, body):
        messToSyslog = "got " + body + " but not set notifyer"
        syslog.syslog("%s: %s" % (self.queue, messToSyslog))
        return True

    def telegram(self, body):
        syslog.syslog("%s: send data to telegramm %s" % (self.queue, body))
        params = self.params["telegram"]
        t = telegram_api(params["token"], proxy=params.get('proxy'))
        data = json.loads(body)
        chat_id = data["chat_id"]
        mess = data["message"]
        return t.send(chat_id, mess) or True

    def psevdo_telegram(self, body):
        params = self.params["to_db"]
        db = corporateDB(params['url_in'])
        data = json.loads(body)
        res, mess = db.telegram_procedure_exec(
            data['group'], data['message'])
        syslog.syslog("%s: send data for telegramm notification %s with status %s" % (
            self.queue, body, res))
        return True
