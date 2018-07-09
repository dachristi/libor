#!/usr/bin/python

import re
import sys
import requests
import json
from os import listdir
from datetime import datetime

from recipients import Mail

import mysql.connector
from bs4 import BeautifulSoup


with open('/home/libor_rate/bin/mysql_config.json', 'r') as f:
    config = json.load(f)
cnx = mysql.connector.connect(user=config['mysql']['user'],
                              password=config['mysql']['password'],
                              host=config['mysql']['host'],
                              database=config['mysql']['database'])
cursor = cnx.cursor(dictionary=True)


class Libor(object):
    def __init__(self, provider_tag, provider_id, filepath):
        self.provider = provider_tag
        self.provider_id = provider_id
        self.filepath = filepath

        # See `providers` table in database for tag definitions
        if self.provider == 'wsj':
            self.label, self.rate, self.effective_date = self.parse_wsj()
        elif self.provider == 'hf':
            self.rate = self.parse_hf(self)
        elif self.provider == 'gr':
            self.rate = self.parse_gr(self)
        else:
            raise Exception('Invalid provider given as arguement.')

    def parse_wsj(self):
        with open(self.filepath, 'r') as f:
            text = f.read()
        soup = BeautifulSoup(text, "lxml")

        # Effective Date
        table_desc = soup.findAll('div', {'class': 'tableDesc'})
        if table_desc:
            effective_date = table_desc[0].text
        else:
            raise Exception('Cannot find the effective date in page')
            #return (0, 'Cannot find the effective date in page')
        if 'Rates shown are effective' not in effective_date:
            raise Exception('Cannot find the effecive date in parsed object')
            #return (0, 'Cannot find the effecive date in parsed object')

        # Libor Rate
        tables = soup.findAll('table')
        for table in tables:
            if 'Libor Rates (USD)' in table.text:
                break
        # Insert check to ensure Libor Rates (USD) is within table
        if 'Libor Rates (USD)' in table.text:
            pass
        else:
            #std.err('Cannot find rate in table')
            raise Exception('Cannot find rate in table')
            #return (0, 'Cannot find rate in table')

        if 'Libor Rates (USD)' in tables[2].findAll('tr')[3].text:
            pass
        else:
            raise Exception('Cannot find rate in rows')
            #return (0, 'Cannot find rate in rows')

        assert('Libor Rates (USD)' in tables[2].findAll('tr')[3].text)

        label = tables[2].findAll('tr')[6].findAll('td')[0].text
        rate = tables[2].findAll('tr')[6].findAll('td')[1].text

        return (label, rate, effective_date)


class Provider(object):

    #root_dir = '/Users/dc/Documents/projects/libor_project/libor/html_files/'
    root_dir = '/home/libor_rate/html_files/'

    def __init__(self, id, provider, tag, url):
        self.id = id
        self.provider = provider
        self.tag = tag
        self.url = url
        self.file_dir = self.root_dir + self.tag + '/'

    def scrape(self):
        '''
        Simple function to scrape a webpage and store the data as a file.
        The provider arguement is in object with tag and url attributes expected.
        '''
        r = requests.get(self.url)
        date = datetime.now().strftime("%Y%m%d")  # yields YYYYMMDD date format
        filepath = '%s%s.html' % (self.file_dir, date)
        with open(filepath, 'w') as f:
            f.write(r.content)


def main():
    providers = data_providers()  # Returns a list of Provider objects
    for provider in providers:
        print datetime.now(), 'Scraping data for %s' % provider.provider
        provider.scrape()
    for provider in providers:
        files = listdir(provider.file_dir)
        for f in files:
            if processed_files(provider.file_dir + f):
                continue
            # Parse the data from stored html file
            libor = Libor(provider.tag, provider.id, provider.file_dir + f)
            # Store the parsed data
            store(libor)
    mail = Mail()
    mail.draft()
    mail.send()
    return 0


def data_providers():
    '''
    Read the `providers` table to obtain eah provider and corresponding url.
    '''
    cmd = '''
            SELECT id, provider, tag, url
            FROM providers
            WHERE enabled = 1;
            '''
    providers = []
    cursor.execute(cmd)
    x = cursor.fetchall()
    for item in x:
        provider = Provider(item['id'], item['provider'], item['tag'], item['url'])
        providers.append(provider)
    return providers


def store(data):
    '''
    data is an object that is expected to contain provider, rate, label,
    and effective_date attributes.
    '''
    cmd1 = '''
            INSERT INTO files
            (filepath)
            VALUES (%s);
            '''
    cmd2 = '''
            SELECT id
            FROM files
            WHERE filepath = %s;
            '''
    cmd3 = '''
            INSERT INTO rates
            (provider_id, rate1month, effective, updated_at, files_id)
            VALUES (%s,%s,%s,%s,%s);
            '''
    cursor.execute(cmd1, (data.filepath,))
    cursor.execute(cmd2, (data.filepath,))
    x = cursor.fetchall()
    if x:
        files_id = x[0]['id']
    else:
        raise Exception('Problem storing filename & retrieving corresponding id')
        return 1

    cursor.execute(cmd3, (data.provider_id,
                          data.rate,
                          data.effective_date,
                          datetime.now().date(),
                          files_id))
    cnx.commit()
    return 0


def processed_files(f):
    '''
    Check if file has already been processed.
    '''
    cmd = '''
            SELECT id
            FROM files
            WHERE filepath = %s;
            '''
    cursor.execute(cmd, (f,))
    x = cursor.fetchall()
    if x:
        return 1  # file has already been processed
    else:
        return None  # file has not been processed; ok to process it & store data


if __name__ == '__main__':
    sys.exit(main())




'''


1. check for files that have not been processed
2. process each file





'''