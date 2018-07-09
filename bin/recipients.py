#!/usr/bin/python

import json
import subprocess
from datetime import date, datetime

import mysql.connector


with open('/home/libor_rate/bin/mysql_config.json', 'r') as f:
    config = json.load(f)
cnx = mysql.connector.connect(user=config['mysql']['user'],
                              password=config['mysql']['password'],
                              host=config['mysql']['host'],
                              database=config['mysql']['database'])
cursor = cnx.cursor(dictionary=True)


class Mail(object):
    '''
    Object reads recipients from recipients table and combines the email
    addresses into a comma-seperated string.
    '''
    def __init__(self):
        self.recipients = self.addresses()
        self.subject = 'LIBOR Rate %s' % str(date.today())

    def draft(self):

        # Draft the email
        cmd = '''
                SELECT rate1month, effective, updated_at
                FROM rates
                WHERE provider_id = 1
                ORDER BY updated_at DESC
                LIMIT 1;
                '''
        cursor.execute(cmd)
        x = cursor.fetchall()
        if x:
            rate = x[0]['rate1month']
            effective_date = x[0]['effective']
            updated_at = x[0]['updated_at']
        else:
            raise Exception('Problem reading data')
        email_body = ("\n\n\n\nHello,\n\n"
                      "The most recently published 1-month LIBOR rate is:\n\n"
                       "LIBOR Rate: $%s\n"
                       "%s*\n\n"
                       "The source for this information is %s and was obtained "
                       "on %s.\n\n"
                       "* Obtained directly from source website.\n\n\n\n"
                       "Best,\nLibor Rate Bot\n\n\n\n" % (
                                  rate,
                                   effective_date,
                                   'http://www.wsj.com/mdc/public/page/2_3020-libor.html',
                                   updated_at))

        with open('/home/libor_rate/bin/email.txt', 'w') as f:
            f.write(email_body)
        print '%s Email drafted successfully' % str(datetime.now())

    def addresses(self):
        '''
        Query the active email addresses from the recipients table.
        '''
        cmd = '''
                SELECT email
                FROM recipients
                WHERE enabled = 1;
                '''
        cursor.execute(cmd)
        x = cursor.fetchall()
        if x:
            recipients = ','.join([e['email'] for e in x])
        else:
            recipients = ''
        return recipients

    def send(self):
        '''
        Command to send email.
        '''
        subprocess.call(['bash', '/home/libor_rate/bin/mail.sh', self.subject, self.recipients])
        print '%s Email successfully sent' % datetime.now()
