# coding: utf-8
import datetime

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "tivagas".upper()
root_link = "http://www.tivagas.com.br/page/%s"
NUMBER_OF_PAGES = 50
ALERT = False

if __name__ == '__main__':
    # : timestamp for data ----- #
    date = datetime.datetime.now()

    # : FILE NAME ---------------------------------------------------- #
    name_file = COMPANY + "_" + str(date.strftime('%Y-%m-%d_%Hh%Mm%Ss'))

    for i in range(1, NUMBER_OF_PAGES):
        if ALERT:
            break
        try:
            soup = get_soup(root_link % i)
            for job in soup.find('div', {'class': 'whiteboard'}).find_all('li', {'class': 'filter_1'}):
                # TITLE --------
                job_block = job.find('h3')
                job_title = job_block.text

                # LINK ---------
                job_link = job_block.find('a')['href']

                # Get values from each page --
                single_job = get_soup(job_link)
                [el.extract() for el in single_job.find_all('div', {'class', 'apply'})]

                # SALARY -------
                job_salary = single_job.find('div', {'class': 'package'})
                if job_salary is not None:
                    job_salary = job_salary.text
                else:
                    job_salary = u"À combinar"

                # DESCRIPTION---
                job_desc = single_job.find('div', {'class': 'whiteboard'}).text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
