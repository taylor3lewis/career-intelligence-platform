# coding: utf-8

import datetime
import re

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "VAGAS-COM-BR".upper()
root_link = "https://www.vagas.com.br"
root_link_1 = "https://www.vagas.com.br/vagas-de-tecnologia?a%5B%5D=24&q=tecnologia&pagina="
root_link_2 = "&_=1534113648244"
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
            soup = get_soup(root_link_1 + str(i) + root_link_2)
            for job in soup.find_all('li', {'class': 'vaga'}):
                # TITLE --------
                job_title = job.find('h2').text

                # LINK ---------
                job_link = root_link + job.find('a', {'class': 'link-detalhes-vaga'})['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # SALARY -------
                job_salary = single_job.find('div', {'class': 'infoVaga'})
                if job_salary is not None:
                    job_salary = job_salary.find_all('li')[0].find('span').text
                    job_salary = re.sub(r"[^0-9R$.a-zA-ZãÃÁàá\s]", "", job_salary).replace('\n', '').replace('\r', '')
                else:
                    job_salary = 'Não informado'

                # DESCRIPTION---
                job_desc = single_job.find('div', {'class': 'texto'}).text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
    send_slack(COMPANY + " SCRAPY | Status OK")
