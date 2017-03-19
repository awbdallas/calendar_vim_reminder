#!/usr/bin/env python3

import lib.calendarvim as calendarvim
import os
import sys
import smtplib
import configparser
import datetime


def main():
    config_options = get_config_options()
    calendar = calendarvim.CalendarVim(
        config_options['Main']['calendar_folder']
    )
    send_reminder_email(calendar, config_options)


def send_reminder_email(calendar, config_options):
    today = datetime.date.today()
    calendar_events = calendar.get_events_for_day(today)
    msg = email_from_events(calendar_events)
    send_email(config_options, msg)


def email_from_events(calendar_events):
    msg = """\
Hello,

Here are a list of your calendars and events scheduled for today.\n\n
"""
    
    for calendar in calendar_events:
        if len(calendar_events[calendar]) == 0:
            continue
        msg += '{}:\n'.format(calendar.summary)

        for event in calendar_events[calendar]:
            msg += event.summary + '\n'
        msg += '\n'

    return msg


def get_config_options():
    config_file = os.getcwd() + '/config_file.config'

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

    message = 'From: {}\r\nSubject: {}\r\nTo: {}\r\n\r\n{}'.format(
            config.get('Main', 'fromaddr'),
            "Calendar Reminder for {}".format(datetime.date.today()),
            config.get('Main', 'toaddr'),
            message)

    smtp_server.sendmail(config.get('Main', 'fromaddr'),
                         config.get('Main', 'toaddr'),
                         message)
    smtp_server.quit()

if __name__ == '__main__':
    main()
