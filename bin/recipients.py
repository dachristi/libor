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
    Object reads recipients from `recipients` table and combines the email
    addresses into a comma-seperated string.
    '''
    def __init__(self):
        self.recipients = self.addresses()
        self.subject = 'LIBOR Rate %s' % str(date.today())

    def draft(self):
        '''
        Creates an HTML file containing the body of the email to be sent.
        '''

        cmd = '''
                SELECT rate1month, effective, updated_at
                FROM rates
                WHERE provider_id = 3
                ORDER BY updated_at DESC
                LIMIT 1;
                '''
        cmd1 = '''
                SELECT url
                FROM providers
                WHERE id = 3;
                '''
        # url
        cursor.execute(cmd1)
        x = cursor.fetchall()
        if x:
            url = x[0]['url']
        else:
            raise exception('Cannot find the url for provider')
        # rate
        cursor.execute(cmd)
        x = cursor.fetchall()
        if x:
            rate = x[0]['rate1month']

            # Format mysql date into python datetime object
            effective_date = x[0]['effective']
            #e_year, e_month, e_day = map(int, effective_date.split('-'))
            #effective_date = datetime(e_year, e_month, e_day).strftime('%d/%m/%Y')
            #e_year, e_month, e_day = map(int, effective_date.split('-'))
            #updated_at = datetime(*map(int, x[0]['updated_at'].split('-'))).strftime('%d/%m/%Y')

            updated_at = x[0]['updated_at'].strftime('%-m/%-d/%Y')
        else:
            raise Exception('Problem reading data')
        email_body = '<html>\n'
        email_body += '<body>\n'
        email_body += '<p>'
        #               "LIBOR Rate: %s%%\n"
        email_body += ("<br>\n<br>\n"
                       "Hello,"
                       "<br>\n<br>\n"
                       "The most recently published 1-month LIBOR rate is: "

                       "<b>%s%%</b>.\n<br>\n<br>\n"

                       "%s.\n<br>\n<br>\n"
                       "The source for this information is %s and was obtained "
                       "on %s.\n<br>\n<br>\n<br>\n<br>\n"
                       "Cheers,\n<br>\n"
                       "Libor Rate Bot\n<br>\n<br>\n<br>\n<br>\n"

                       "</p>\n"
                       "</body>\n"
                       "</html>\n"
                       % (
                       rate,
                       effective_date,
                       url,
                       updated_at))

        with open('/home/libor_rate/bin/email.html', 'w') as f:
            f.write(email_body)
        print '%s Email drafted successfully' % str(datetime.now())

    def addresses(self):
        '''
        Query the active email addresses from the `recipients` table.
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
