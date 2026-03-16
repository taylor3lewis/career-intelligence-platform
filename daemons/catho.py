# coding: utf-8

import datetime

from custom_libs.job_scraper import get_soup
from custom_libs.job_scraper import save_data
from custom_libs.slack_integration import send_slack

COMPANY = "CATHO".upper()
root_link = "https://www.catho.com.br/vagas/?q=desenvolvedor&pais_id=31&faixa_sal_id_combinar=1&perfil_id=1&order=score&where_search=1&how_search=2&page=%s"
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
            for job in soup.find_all('li', {'class': 'boxVaga'}):
                # TITLE --------
                job_title = job.find('a', {'class': 'viewVagaAction'}).text

                # LINK ---------
                job_link = job.find('a', {'class': 'viewVagaAction'})['href']

                # Get values from each page --
                single_job = get_soup(job_link)

                # SALARY -------
                job_salary = single_job.find(
                    'header', {'class': 'headerVaga'}
                ).find(
                    'em', {'class', 'cidades'}
                ).find_all('span')[0].text

                # DESCRIPTION---
                job_desc_html = single_job.find('article', {'class': 'infosVaga'})
                # Remove share icons
                if job_desc_html.find('section', {'id': 'compartilhe-esta-vaga'}) is not None:
                    job_desc_html.find('section', {'id': 'compartilhe-esta-vaga'}).extract()
                # get text with share icons
                job_desc = job_desc_html.text

                save_data(name_file, job_title, job_link, job_salary, job_desc)
        except Exception as err:
            send_slack("ERROR IN: " + COMPANY + " " + str(err))
            print(err)
            ALERT = True
            break
    send_slack(COMPANY + " SCRAPY | Status OK")
