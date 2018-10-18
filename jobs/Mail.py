import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from validate_email import validate_email


class Mail:
    def execute(self, body):


        try:
            my_mail = 'mail@mail.server'
            mailDict = json.loads(body)
            mail_is_valid = validate_email(mailDict['mail'])

            if mail_is_valid is not True:
                raise Exception("invalid e-mail: " + mailDict['mail'])

            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(mailDict['subject'], 'utf-8')
            msg['From'] = my_mail
            msg['To'] = mailDict['mail']

            msgText = MIMEText(mailDict['message'].encode(
                'utf-8'), 'plain', 'utf-8')
            msg.attach(msgText)

            s = smtplib.SMTP('mail.server')
            s.sendmail(my_mail, mailDict['mail'], msg.as_string())

            syslog.syslog("Sending email-massage to: %s" % (mailDict['mail']))
        except Exception as exc:
            syslog.syslog("Error while sending e-mail: %s" % (exc))

        finally:
            if s:
                s.quit()