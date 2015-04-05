import email
import smtplib
import click
from mailbox import mbox
# copy-pasta'd, no need for OCD
from email.Message import Message 
from email.MIMEBase import MIMEBase 
from email.MIMEText import MIMEText 
from email.MIMEMessage import MIMEMessage 

@click.command()
@click.option('--filename', required=True, help='filename of mbox file')
@click.option('--exclude', '-x', multiple=True, default=[])
@click.option('--send', default=False, help='do not actually send to email')
@click.option('--send-from')
@click.option('--send-to')
@click.option('--smtp-host')
@click.option('--smtp-port')
@click.option('--smtp-username')
@click.password_option('--smtp-password', confirmation_prompt=False)
def send_to_capsule(filename, exclude, send, send_from, send_to, smtp_host, smtp_port, smtp_username, smtp_password):
    archive = mbox(filename)
    messages = []
    for message in archive:
        should_exclude = False
        for excluded_to in exclude:
            if excluded_to in message['to']:
                should_exclude = True
                print 'excluding message to {0}'.format(message['to'])
                break
        if should_exclude:
            continue

        messages.append(message)

    if len(messages) > 0 and send and send_to:
        smtp = smtplib.SMTP(smtp_host, int(smtp_port))
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(smtp_username, smtp_password)

        for message in reversed(messages):
            forward = MIMEBase("multipart", "mixed") 
            forward["Subject"] = "FW: %s" % message['subject']
            forward["From"] = send_from
            forward["To"] = send_to
            forward['bcc'] = None

            rfcmessage = MIMEBase("message", "rfc822") 
            rfcmessage.attach(message) 
            forward.attach(rfcmessage) 

            smtp.sendmail(message['from'], message['to'], forward.as_string(unixfrom=0))


if __name__ == '__main__':
    send_to_capsule()