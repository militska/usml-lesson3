import json

class Sms:
    def execute(body):
        smsDict = json.loads(body)

        number = smsDict['number']
        subject = smsDict['subject']
        message = smsDict['message']

        message = subject + " " + message
        message = message.replace('\n', '')
        message = message[:70].encode('utf-8')

        try:
            connection = dbModule.Connection("db_login/db_pass")
            cursor = connection.cursor()

            sql = "DECLARE res_v VARCHAR (100); \
            BEGIN send_procedure(%s, %s); COMMIT; END;" \
                  % (number.encode('utf-8'), message)

            cursor.execute(sql)

            syslog.syslog("Sending SMS message to: %s" % (smsDict['number']))
        except Exception as exc:
            syslog.syslog("Error while sending SMS notification: %s" % (exc))

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
