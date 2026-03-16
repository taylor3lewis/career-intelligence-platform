# coding: utf-8
import datetime

import requests
from bs4 import BeautifulSoup

from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "apinfo".upper()
root_link = "http://www.apinfo.com/apinfo/inc/list4.cfm"
PAGE_NUMBER = 500
ALERT = False

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7,it;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "www.apinfo.com",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/68.0.3440.106 Safari/537.36"
}


def dig_jobs(name_file_, soup_):
    count = 0
    for job in soup_.find_all('div', {'class': 'box-vagas'}):
        count += 1
        try:
            # TITLE --------
            job_title = job.find('div', {'class': 'cargo'}).text

            # LINK ---------
            job_link = job.find('a', {'class': 'btn3'})['href']

            # SALARY -------
            job_salary = u'À combinar'

            # DESCRIPTION---
            job_desc = job.find('div', {'class': 'texto'})
            [a.extract() for a in job_desc.find_all('a')]
            job_desc = job_desc.text

            save_data(name_file_, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            return False
    return True


def get_next_page(soup_, session_, headers, cookies, cookies_plain):
    form = dict()
    for i in soup_.find_all('input'):
        if i.has_attr('name'):
            if i['name'] in ['pkey', 'tcv', 'ddmmaa1', 'ddmmaa2', 'onde', 'andor', 'keyw', 'pag']:
                form[i['name']] = i['value']
    form_string = "&".join([k + '=' + form[k] for k in form])
    _headers = headers
    _headers["Content-Length"] = "82"
    _headers["Content-Type"] = "application/x-www-form-urlencoded"
    _headers["Cookie"] = "; ".join([k + '=' + cookies_plain[k] for k in cookies_plain])
    _headers["Referer"] = "http://www.apinfo.com/apinfo/inc/list4.cfm"
    resp = session_.post(root_link, headers=headers, data=form_string, cookies=cookies, verify=True)
    return BeautifulSoup(resp.text, 'lxml')


if __name__ == '__main__':
    # timestamp for data --------
    date = datetime.datetime.now()
    name_file = COMPANY + "_" + str(date.strftime('%Y-%m-%d_%Hh%Mm%Ss'))

    # PAGE ONE ..............
    print('page', 1)
    session = requests.Session()
    response = session.get(root_link, headers=headers)
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
    cookies_plain = response.cookies.get_dict()

    soup = BeautifulSoup(response.text, 'lxml')
    dig_jobs(name_file, soup)

    for i in range(PAGE_NUMBER):
        print('page', i + 2)
        soup = get_next_page(soup, session, headers, cookies, cookies_plain)
        if not dig_jobs(name_file, soup):
            break

    send_slack(COMPANY + " SCRAPY | Status OK")
