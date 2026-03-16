# coding: utf-8

import datetime

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "profissionaisti".upper()
root_link = "https://empregos.profissionaisti.com.br/?p=%s"
PAGE_NUMBER = 50
ALERT = False

if __name__ == '__main__':
    # timestamp for data -----
    date = datetime.datetime.now()
    name_file = COMPANY + "_" + str(date.strftime('%Y-%m-%d_%Hh%Mm%Ss'))

    for i in range(1, PAGE_NUMBER):
        if ALERT:
            break
        try:
            soup = get_soup(root_link % i)
            for job in soup.find_all('div', {'class': 'job-list-content'}):
                # TITLE --------
                job_title = job.find('h4').text

                # LINK ---------
                job_link = job.find('h4').find('a')['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # HTML
                html_content = single_job.find('div', {'id': 'content'})
                header = html_content.find('div', {'class': 'job-header'})
                content = html_content.find('div', {'class': 'job-content'})

                # SALARY -------
                job_salary = " ".join([p.text for p in content.find_all('p') if 'Salário:' in p.text])

                # DESCRIPTION---
                job_desc = content.text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
    send_slack(COMPANY + " SCRAPY | Status OK")
