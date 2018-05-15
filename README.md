# auto-auto reply
Auto-auto reply is an email utility that automatically sends an out-of-office message when you have too much unread mail, defined by a tolerance level. In other words, it is a dynamic out-of-office message that responds to your current email load, without you needing to explicitly turn it on and off. It also encourages brevity and channel switching by permitting people to send short email replies (< 140 characters), and have them delivered via text to your phone.

## Getting Started

Auto-auto reply accesses a mail server using IMAP. It has been tested against 
Gmail's IMAP, but to enable the bot to work on Gmail, you will have to enable
the "Allow less secure apps" option. Other IMAP servers may work as
well, but they have not at this time been tested.

Also establish a [Twilio](https://twilio.com) account, from which you will extract its [API access keys](https://www.twilio.com/console).

### Prerequisites

Auto-auto reply requires IMAPClient and the Twilio API (to relay text
responses to your phone after someone responds to your auto-reply). 

``pip install imapclient
pip install twilio``

### Installing

``git clone https://github.com/ee-gilbert/autoautoreply.git``

Change lines 12-24 to reflect your servers, tokens, accounts, etc.
Update the actual message as well. :-)

Auto-auto reply runs as a cron job, which you can run at any frequency,
but every 10 minutes is a reasonable default. To run it every 10
minutes, enter the following line into your crontab on a workstation that can
access your mailserver:

``*/10 * * * * python autoautoreply.py > auto-auto.log``

## Contributing

Contributions welcome. :-)

## Authors

* **Eric Gilbert** - [School of Information, University of Michigan](http://eegilbert.org)

## License

This project is licensed under the GPL v3.0 - see [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

Thanks for all the email, without which this project may never have been
born.
