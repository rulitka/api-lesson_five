from terminaltables import SingleTable
import requests
import os
from dotenv import load_dotenv


def predict_salary(min_salary, max_salary):
    if min_salary == None or min_salary == 0:
        average_salary =  max_salary*0.8
    elif max_salary == None or max_salary == 0:
        average_salary =  min_salary*1.2
    else:  
        average_salary = ((max_salary+min_salary)/2)
    return average_salary  


def get_vacancies_hh(profession):
    hh_vacancies = []
    page = 0
    pages = 1
    while page < pages:
        url = 'https://api.hh.ru/vacancies'
        user_request = {'text': profession, 'area': '4', 'period': '30',
               'per_page': '10', 'page': page}
        page_response = requests.get(url, params=user_request)
        pages = page_response.json()['pages']
        page += 1
        page_answer_hh = page_response.json()
        hh_vacancies.append(page_answer_hh)
    return hh_vacancies

def predict_rub_salary_hh(hh_vacancies, profession):
    total_vacancies = hh_vacancies[0]['found']
    total_salary = 0
    total_number = 0
    for vacancy in hh_vacancies:
        prepare_vacancies = vacancy['items']
        number = 0
        sum_salary = 0
        total_average_salary = 0
        for prepare_vacancy in prepare_vacancies:
            if prepare_vacancy['salary'] is not None:
                salary = prepare_vacancy['salary']
                if salary['currency'] == 'RUR':
                    number += 1
                    min_salary = salary['from']
                    max_salary = salary['to']
                    average_salary = predict_salary(min_salary, max_salary)
                    sum_salary += average_salary
        total_salary += sum_salary
        total_number += number
    try:
        total_average_salary = int(total_salary/total_number)
    except ZeroDivisionError:
        pass
    hh_response = [profession, total_vacancies, total_number,  total_average_salary]
    return hh_response


def get_vacancies_sj(profession, secret_key_sj):
    sj_vacancies = []
    page = 0
    pages = 1
    while page < pages:
        url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {'X-Api-App-Id': secret_key_sj}
        user_request = {'keyword': profession,
                 'town': 4,
                 'period': 30,
                 'count': 10,
                 'page': page}
        page_response = requests.get(url, headers=headers, params=user_request)
        page_response.raise_for_status()
        more_vacancies = page_response.json()['more']
        if more_vacancies:
            page += 1
            pages += 1
        if not more_vacancies:
            break
        page_answer_sj = page_response.json()
        sj_vacancies.append(page_answer_sj)
    return sj_vacancies

def predict_rub_salary_sj(sj_vacancies, profession):
    total_vacancies = sj_vacancies[0]['total']
    total_salary = 0
    total_number = 0
    for vacancy in sj_vacancies:
        prepare_vacancies = vacancy['objects']
        number = 0
        sum_salary = 0
        total_average_salary = 0
        for prepare_vacancy in prepare_vacancies:
            if prepare_vacancy['currency'] == 'rub':
                min_salary = prepare_vacancy['payment_from']
                max_salary = prepare_vacancy['payment_to']
                if min_salary or max_salary != 0:
                    number += 1 
                average_salary = predict_salary(min_salary, max_salary)
                sum_salary += average_salary
        total_salary += sum_salary
        total_number += number
    try:
        total_average_salary = int(total_salary/total_number)
    except ZeroDivisionError:
        pass
    sj_response = [profession, total_vacancies, total_number,  total_average_salary]
    return sj_response


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
    load_dotenv()
    secret_key_sj = os.getenv('SECRET_KEY')
    table_hh = []
    table_sj = []
    professions = ("C#", "Objective-C",
                   "Ruby", "Java", "C", 
                   "Typescript", "Scala",
                   "Go", "Swift", 
                   "C++", "PHP", 
                   "JavaScript", "Python")
    for profession in professions:
        hh_vacancies = get_vacancies_hh(profession)
        hh_response = predict_rub_salary_hh(hh_vacancies, profession)
        table_hh.append(hh_response)
        title_hh = 'HEADHUNTER_MOSCOW'
        sj_vacancies = get_vacancies_sj(profession, secret_key_sj)
        try:
            sj_response = predict_rub_salary_sj(sj_vacancies, profession)
            table_sj.append(sj_response)
        except (IndexError, ValueError):
            pass
        title_sj = 'SUPERJOB_MOSCOW'
    print (get_table(table_hh, title_hh))
    print()
    print (get_table(table_sj, title_sj))
    print()


if __name__ == '__main__':
    main()
