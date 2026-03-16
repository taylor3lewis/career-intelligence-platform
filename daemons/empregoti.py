# coding: utf-8

import datetime
import re

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "empregoti".upper()
root_link = "http://www.empregoti.com/jobs-in/estado-de-sao-paulo/?p=%s"
NUMBER_OF_PAGES = 50
ALERT = False

if __name__ == '__main__':
    # : timestamp for data ----- #
    date = datetime.datetime.now()

    # : FILE NAME ---------------------------------------------------- #
    name_file = COMPANY + "_" + str(date.strftime('%Y-%m-%d_%Hh%Mm%Ss'))

    for i in range(1, NUMBER_OF_PAGES):
        print(i)
        if ALERT:
            break
        try:
            soup = get_soup(root_link % i)

            for job in soup.find_all('div', {'class': 'job-opening'}):
                # TITLE --------
                job_title = job.find('a', {'class', 'job-title'}).text

                # LINK ---------
                job_link = job.find('a', {'class': 'job-title'})['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # DESCRIPTION---
                job_desc = single_job.find(
                    'div', {'id': 'content'}).text

                # SALARY -------
                job_salary = " - ".join(re.findall("([Rr]\$[\s0-9.,]+)", job_desc))

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
