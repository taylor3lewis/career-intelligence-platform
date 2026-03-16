# coding: utf-8

import datetime
import time
from random import randint

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "MANAGER".upper()
root_link = "https://www.manager.com.br/empregos-desenvolvedor-pagina-%s"
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
            for job in soup.find_all('article', {'class': 'vaga'}):
                # TITLE --------
                job_title = job.find('h2').text

                # LINK ---------
                job_link = job.find('a', {'class': 'permalink'})['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # HTML
                html_content = single_job.find('article', {'class': 'vaga'})
                if html_content is None:
                    continue

                # SALARY -------
                job_salary = " ".join(
                    [dl.text for dl in html_content.find_all('dl') if 'Salário:' in dl.text]
                )

                # DESCRIPTION---
                job_desc = html_content.text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
                time.sleep(randint(1, 11))
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
    send_slack(COMPANY + " SCRAPY | Status OK")
