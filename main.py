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
    total_salary = 0
    total_number = 0
    page = 0
    pages = 1
    while page < pages:
        url = 'https://api.hh.ru/vacancies'
        user_request = {'text': profesion, 'area': '4', 'period': '5',
               'per_page': '10', 'page': page}
        page_response = requests.get(url, params=user_request)
        pages = page_response.json()['pages']
        page += 1
        page_json = page_response.json()
        vacancies.append(page_json)
        total_vacancies = vacancies[0]['found']
    for vacancy in vacancies:
        prepare_vacancies = vacancy['items']
        number = 0
        sum_salary = 0
        average_salary = 0
        for prepare_vacancy in prepare_vacancies:
            if prepare_vacancy['salary'] is not None:
                salary = prepare_vacancy['salary']
                if salary['currency'] == 'RUR':
                    number += 1
                    min_salary = salary['from']
                    max_salary = salary['to']
                    average_salary = predict_salary(min_salary, max_salary)
                    sum_salary += average_salary
                else:
                    pass
        total_salary += sum_salary
        total_number += number
    try:
        total_average_salary = int(total_salary/total_number)
    except ZeroDivisionError:
        pass
    salary_response = [profesion, total_vacancies, total_number,  total_average_salary]
    return salary_response


def predict_rub_salary_sj(profesion):
    vacancies = []
    total_salary = 0
    total_number = 0
    page = 0
    pages = 1
    total_vacancies = 0
    sum_salary = 0
    total_average_salary = 0
    while page < pages:
        url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {'X-Api-App-Id': SECRET_KEY_SJ}
        user_request = {'keyword': profesion,
                 'town': 4,
                 'period': 5,
                 'count': 10,
                 'page': page}
        page_response = requests.get(url, headers=headers, params=user_request)
        page_response.raise_for_status()
        more_vacancies = page_response.json()['more']
        if more_vacancies is True:
            page += 1
            pages += 1
        if more_vacancies is False:
            break
        page_json = page_response.json()
        vacancies.append(page_json)
        total_vacancies = vacancies[0]['total']
    for vacancy in vacancies:
        prepare_vacancies = vacancy['objects']
        number = 0
        for prepare_vacancy in prepare_vacancies:
            if prepare_vacancy['currency'] == 'rub':
                min_salary = prepare_vacancy['payment_from']
                max_salary = prepare_vacancy['payment_to']
                if min_salary or max_salary != 0:
                    number += 1
                average_salary = predict_salary(min_salary, max_salary)
                sum_salary += average_salary
            else:
                pass
        total_salary += sum_salary
        total_number += number
    try:
        total_average_salary = int(total_salary/total_number)
    except ZeroDivisionError:
        pass
    salary_response = [profesion, total_vacancies, total_number,  total_average_salary]
    return salary_response


def get_table(table, title):
    table_template = [['Язык программирования', 'Вакансий найдено',
                   'Вакансий обработано', 'Средняя зарплата'], ]
    for line in table:
        table_template.append(line)
        table_instance = SingleTable(table_template, title)
        table_instance.justify_columns[2] = 'right'
        table_result = table_instance.table
    return table_result


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
    print (get_table(table_hh, title_hh))
    print()
    print (get_table(table_sj, title_sj))
    print()


if __name__ == '__main__':
    main()
