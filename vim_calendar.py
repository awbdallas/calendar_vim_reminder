#!/usr/bin/env python3

import configparser
import datetime
import os
import smtplib
import sys
import lib.calendarvim as calendarvim

from argparse import ArgumentParser
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def main():
    parser = ArgumentParser()
    parser.add_argument('--reminder_email', help='Send Reminder Email', 
            action='store_true', default=False)
    args = parser.parse_args()
    config_options = get_config_options()
    calendar = calendarvim.CalendarVim(
        config_options['Main']['calendar_folder']
    )

    if args.reminder_email:
        send_reminder_email(calendar, config_options)
    else:
        print("No options were added")


def send_reminder_email(calendar, config_options):
    today = datetime.date.today()
    calendar_events = calendar.get_events_for_day(today)
    msg = email_from_events(calendar_events)
    send_email(config_options, msg)


def email_from_events(calendar_events):
    table_headers = ['Calendar', 'Event', 'Time Start', 'Time End']
    table_data = []
    
    for calendar in calendar_events:
        if len(calendar_events[calendar]) == 0:
            continue
        for event in calendar_events[calendar]:
            start_time = "{:02d}:{:02d}".format(event.start.hour, event.start.second)
            end_time = "{:02d}:{:02d}".format(event.end.hour, event.end.second)
            table_data.append([
                calendar.summary,
                event.summary,
                start_time,
                end_time
           ])

    msg = """\
<html>
    <head></heady>
    <body>
Hello,

Here are a list of your calendars and events scheduled for today.
<br />
<br />


{}
    </body>
</html>
""".format(tabulate(table_data, table_headers, tablefmt="html"))
    return msg


def get_config_options():
    file_dir, _ = os.path.split(os.path.abspath(__file__))
    config_file = file_dir + '/config_file.config'

    if not os.path.isfile(config_file):
        print('No config file set in cwd')
        sys.exit(0)

    config = configparser.ConfigParser()
    config.read(config_file)

    return config


# I used ses(aws). grabbed the guiddeee from here.
# http://blog.noenieto.com/2012/06/19/using_amazon_ses_with_your_python_applications.html
def send_email(config, message):
    needed_keys = ['smtp_server', 'smtp_username', 'smtp_password',
                   'smtp_port', 'smtp_tls', 'toaddr', 'fromaddr']
    # I, uh, kinda need these
    for key in needed_keys:
        try:
            config.get('Main', key)
        except configparser.NoOptionError:
            print('Config options for email not set: {}'.format(key))
            sys.exit(0)

    smtp_server = smtplib.SMTP(
        host=config.get('Main', 'smtp_server'),
        port=config.get('Main', 'smtp_port'),
        timeout=10
    )

    # TODO: take off when done with testing
    # smtp_server.set_debuglevel(10)
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(config.get('Main', 'smtp_username'),
                      config.get('Main', 'smtp_password'))
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Calendar Reminder for {}".format(datetime.date.today())
    msg['From'] = config.get('Main', 'fromaddr')
    msg['To'] = config.get('Main', 'toaddr')
    msg.attach(MIMEText(message, 'html'))

    smtp_server.sendmail(config.get('Main', 'fromaddr'),
                         config.get('Main', 'toaddr'),
                         msg.as_string())
    smtp_server.quit()

if __name__ == '__main__':
    main()
