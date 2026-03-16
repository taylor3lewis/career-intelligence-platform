# coding: utf-8

import datetime

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "empregos-com".upper()
root_link = "https://www.empregos.com.br/vagas/sp/informatica-ti-e-internet/p%s"
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
            for job in soup.find_all('div', {'class': 'descricao'}):

                job_1 = job.find('h3')
                [it.extract() for it in job_1.find_all('span')]

                # TITLE --------
                job_title = job_1.text

                # LINK ---------
                job_link = job_1.find('a')['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # SALARY -------
                job_salary = single_job.find('div', {'class': 'salario-vaga'})
                if job_salary is not None:
                    job_salary.find('p', {'class': 'valor'})
                    if job_salary is not None:
                        job_salary = job_salary.find('span').text

                if job_salary is None:
                    job_salary = 'À combinar'

                # DESCRIPTION---
                job_desc = single_job.find('div', {'class': 'conteudo-vaga'}).text
                job_desc += " " + single_job.find('div', {'class': 'salario-vaga'}).text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
    send_slack(COMPANY + " SCRAPY | Status OK")
