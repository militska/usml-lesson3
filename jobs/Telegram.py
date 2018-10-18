import telegram
import json


class Telegram:

    def execute(body):
        try:
            # Telegram Bot
            pp = telegram.utils.request.Request(proxy_url='socks5://0.0.0.0:9999', urllib3_proxy_kwargs={
                'username': 'some_username', 'password': 'some_password'})
            bot = telegram.Bot(
                token='id:token', request=pp)

            telegramData = json.loads(body)
            bot.sendMessage(telegramData['channel'], telegramData['message'])
        except Exception as exc:
            syslog.syslog("Error while sending telegram: %s" % (exc))
