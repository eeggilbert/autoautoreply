from imapclient import IMAPClient
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from twilio.rest import Client
import smtplib
import email
import os

# server + api settings
imap_server = "YOUR IMAP SERVER"
smtp_server = "YOUR SMTP SERVER"
email_addr = "YOUR EMAIL ADDRESS"
email_pw = "YOUR EMAIL PASSWORD"
twilio_account_sid = "YOUR TWILIO SID"
twilio_auth_token = "YOUR TWILIO AUTH TOKEN"
twilio_cell = "A TWILIO NUMBER" 
my_cell = "YOUR ACTUAL NUMBER"

# names and pronouns
first_name = "YOUR FIRST NAME"
full_name = "YOUR FULL NAME"
pronoun1 = "her/his/their..."
pronoun2 = "she/he/they..."

# tolerance for unread mail; auto-replies are sent after unread count crosses this number
TOLERANCE = 40

auto_msg =  first_name + " is not actively reading " + pronoun1 + " email, as " + pronoun1
auto_msg += " unread message count has crossed a pre-set threshold. This could be "
auto_msg += "because " + pronoun2 + " traveling, or approaching a deadline. "
auto_msg += "This script turns on when that happens [1]."
auto_msg += "\n\n"
auto_msg += "If you need to get in touch, one of the following two options is best: "
auto_msg += "\n\n"
auto_msg += "1. Channel switch. If it's urgent and you can switch to text, Signal, Facebook messenger, Slack, or "
auto_msg += "some other channel, you are more likely to reach " + first_name + " quickly."
auto_msg += "\n\n"
auto_msg += "2. Compose a text in reply to this message. Alternatively, you can "
auto_msg += "reply to this message with fewer than 140 characters (above the quoted reply), "
auto_msg += "and I will send it via text to " + pronoun1 + " cell."
auto_msg += "\n\n"
auto_msg += "thanks,\nauto-auto reply bot"
auto_msg += "\n\n"
auto_msg += "[1] https://github.com/eeggilbert/autoautoreply"

def monitor_new_email():
    with IMAPClient(host=imap_server) as client:
        client.login(email_addr, email_pw)
        client.select_folder('INBOX')

        messages = client.search(['UNSEEN'])
        n_recent = len(messages)
        if n_recent > TOLERANCE:
            for msgid, data in client.fetch(messages, ['ENVELOPE', 'RFC822']).items():
                envelope = data[b'ENVELOPE']
                rfc822 = data[b'RFC822']
                sender = envelope.from_[0].mailbox + "@" + envelope.from_[0].host
                recipients = []
                if envelope.to:
                    recipients = [a.mailbox + "@" + a.host for a in envelope.to]
                if envelope.cc:
                    recipients += [a.mailbox + "@" + a.host for a in envelope.cc]
                flags = client.get_flags(msgid)

                # only auto-reply if on to or cc list and if not acted on before
                if email_addr in recipients and not 'AAREPLIED' in flags[msgid]:
                    # first check if this is a reply i should text
                    if "auto-auto reply bot" in rfc822 and not 'AATEXTED' in flags[msgid]:
                        body = email.message_from_string(rfc822).get_payload()
                        reply_split = body.split('>')
                        text_body = "from " + sender + ": "
                        if len(reply_split) > 0:
                            text_body += reply_split[0]
                        else:
                            text_body += body
                        if len(text_body) > 140:
                            text_body = text_body[:140]
                        t = Client(twilio_account_sid, twilio_auth_token)
                        text = t.messages.create(to=my_cell, from_=twilio_cell, body=text_body)
                        print "sent text with id " + text.sid
                        client.add_flags(msgid, ['AATEXTED'])
                    else:
                        mail(to=sender, subject="Re: "+subject, text=auto_msg, custom_headers={'In-Reply-To': envelope.message_id.decode()})
                        print('sent reply to msg id #%d: "%s" received %s' % (msgid, subject, envelope.date))
                        client.add_flags(msgid, ['AAREPLIED'])

def mail(to, subject, text, cc=None, bcc=None, reply_to=None, attach=None,
         html=None, pre=False, custom_headers=None):
    msg = MIMEMultipart()

    msg['From'] = full_name + " <" + email_addr + ">"
    msg['To'] = to
    msg['Subject'] = subject

    to = [to]

    if cc:
        # cc gets added to the text header as well as list of recipients
        if type(cc) in [str, unicode]:
            msg.add_header('Cc', cc)
            cc = [cc]
        else:
            cc = ', '.join(cc)
            msg.add_header('Cc', cc)
        to += cc

    if bcc:
        # bcc does not get added to the headers, but is a recipient
        if type(bcc) in [str, unicode]:
            bcc = [bcc]
        to += bcc

    if reply_to:
        msg.add_header('Reply-To', reply_to)

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to
    # display.

    if pre:
        html = "<pre>%s</pre>" % text
    if html:
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        msgText = MIMEText(text)
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it
        # below
        msgText = MIMEText(html, 'html')
        msgAlternative.attach(msgText)
    else:
        msg.attach(MIMEText(text))

    if attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)

    if custom_headers:
        for k, v in custom_headers.iteritems():
            msg.add_header(k, v)

    mailServer = smtplib.SMTP(smtp_server, 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(email_addr, email_pw)

    mailServer.sendmail(email_addr, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

def main():
    monitor_new_email()

if __name__ == "__main__":
    main()
