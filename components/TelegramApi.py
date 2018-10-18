class telegram_api:
    def __init__(self, token, proxy={}):
        self.BOT_TOKEN = token
        self.cmd = {"stat": "getMe", "send": "sendMessage"}
        if proxy:
            ip = proxy['ip']
            port = proxy['port']
            user = proxy['user']
            passwd = proxy['password']
            pp = telegram.utils.request.Request(proxy_url='socks5://%s:%s' % (
                ip, port), urllib3_proxy_kwargs={'username': user, 'password': passwd})
        else:
            pp = telegram.utils.request.Request()
        self.bot = telegram.Bot(token=self.BOT_TOKEN, request=pp)

    def stat(self):
        # cmd=self.cmd["stat"]
        try:
            pass
        except Exception as err:
            messToSyslog = "Fail to read telegram_bot status: %s" % (err)
            syslog.syslog('-----------------------------------------')
            syslog.syslog(" %s" % messToSyslog)

    def send(self, chat, mess):
        # cmd = self.cmd["send"]
        mess = mess.encode('utf-8')
        try:
            self.bot.sendMessage(chat, mess)
            return True
        except Exception as err:
            messToSyslog = "Fail to sendmessage via telegram_bot: %s" % (err)
            syslog.syslog('-----------------------------------------')
            syslog.syslog(" %s" % messToSyslog)