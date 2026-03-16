# coding: utf-8

import datetime

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "NOME_DO_SITE".upper()
root_link = "https://URL_DO_SITE/LISTA_DE_EMPREGOS?PAGINA=%s"
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

            for job in soup.find_all('div', {'class': 'VAGA'}):
                # TITLE --------
                job_title = job.find('h2', {'class', 'TITULO_VAGA'}).text

                # LINK ---------
                job_link = job.find('a', {'class': 'LINK_VAGA'})['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # SALARY -------
                job_salary = single_job.find('p', {'class': 'SALARIO'}).text

                # DESCRIPTION---
                job_desc = single_job.find(
                    'div', {'class': 'TEXTO_DESCRITIVO'}).text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
