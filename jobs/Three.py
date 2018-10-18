import json
from components.DB import DB
import syslog


class Three:

    def execute(self, ch, method, properties, body):
        row = create_three(body)
        db_result = DB.db_process_three(row)
        if db_result:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def create_three(self, body_msg):
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