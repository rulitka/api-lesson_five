from __future__ import print_function
from terminaltables import SingleTable
import requests
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY_SJ = os.getenv('SECRET_KEY')


def predict_salary(min_salary, max_salary):
    average_salary = 0
    if min_salary and max_salary is not None or 0:
        average_salary = ((max_salary+min_salary)/2)
    if min_salary is None or 0:
        average_salary = max_salary*0.8
    if max_salary is None or 0:
        average_salary = min_salary*1.2
    return average_salary


def predict_rub_salary_hh(profesion):
    vacancies = []
    all_zp = 0
    all_n = 0
    page = 0
    pages = 1
    while page < pages:
        url = 'https://api.hh.ru/vacancies'
        par = {'text': profesion, 'area': '4', 'period': '5',
               'per_page': '10', 'page': page}
        page_response = requests.get(url, params=par)
        pages = page_response.json()['pages']
        page += 1
        page_data = page_response.json()
        vacancies.append(page_data)
        found_vac = vacancies[0]['found']
    for vacancy in vacancies:
        prep_list_of_vac = vacancy['items']
        number_vac_with_sal = 0
        sum_zp = 0
        av_zp = 0
        for prep_one_of_vac in prep_list_of_vac:
            if prep_one_of_vac['salary'] is not None:
                sal = prep_one_of_vac['salary']
                if sal['currency'] == 'RUR':
                    number_vac_with_sal += 1
                    min_salary = sal['from']
                    max_salary = sal['to']
                    average_salary_hh = predict_salary(min_salary, max_salary)
                    sum_zp += average_salary_hh
                if sal['currency'] != 'RUR':
                    pass
        all_zp += sum_zp
        all_n += number_vac_with_sal
    try:
        av_zp = int(all_zp/all_n)
    except ZeroDivisionError:
        pass
    list_vac = [profesion, found_vac, all_n,  av_zp]
    return list_vac


def predict_rub_salary_sj(profesion):
    vacancies = []
    all_zp = 0
    all_n = 0
    page = 0
    pages = 1
    found_vac = 0
    sum_zp = 0
    av_zp = 0
    while page < pages:
        url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {'X-Api-App-Id': SECRET_KEY_SJ}
        param = {'keyword': profesion,
                 'town': 4,
                 'period': 5,
                 'count': 10,
                 'page': page}
        page_response = requests.get(url, headers=headers, params=param)
        page_response.raise_for_status()
        pages_zoom = page_response.json()['more']
        if pages_zoom is True:
            page += 1
            pages += 1
        if pages_zoom is False:
            break
        page_data = page_response.json()
        vacancies.append(page_data)
        found_vac = vacancies[0]['total']
    for vacancy in vacancies:
        prep_list_of_vac = vacancy['objects']
        number_vac_with_sal = 0
        for prep_one_of_vac in prep_list_of_vac:
            if prep_one_of_vac['currency'] == 'rub':
                min_salary = prep_one_of_vac['payment_from']
                max_salary = prep_one_of_vac['payment_to']
                if min_salary or max_salary != 0:
                    number_vac_with_sal += 1
                average_salary_sj = predict_salary(min_salary, max_salary)
                sum_zp += average_salary_sj
            if prep_one_of_vac['currency'] != 'rub':
                pass
        all_zp += sum_zp
        all_n += number_vac_with_sal
    try:
        av_zp = int(all_zp/all_n)
    except ZeroDivisionError:
        pass
    list_vac = [profesion, found_vac, all_n,  av_zp]
    return list_vac


def get_table(table, title):
    TABLE_DATA = [['Язык программирования', 'Вакансий найдено',
                   'Вакансий обработано', 'Средняя зарплата'], ]
    for line in table:
        TABLE_DATA.append(line)
        table_instance = SingleTable(TABLE_DATA, title)
        table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    print()


def main():
    table_hh = []
    table_sj = []
    profesions = ("Java", "JavaScript",
                  "1С", "Python",
                  "C", "C++",
                  "C#", "Objective-C",
                  "Perl", "Ruby",
                  "PHP")
    for profesion in profesions:
        hh_response = predict_rub_salary_hh(profesion)
        table_hh.append(hh_response)
        title_hh = 'HEADHUNTER_MOSCOW'
        sj_response = predict_rub_salary_sj(profesion)
        table_sj.append(sj_response)
        title_sj = 'SUPERJOB_MOSCOW'
        get_table(table_hh, title_hh)
        get_table(table_sj, title_sj)


if __name__ == '__main__':
    main()
