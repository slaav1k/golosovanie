import csv
import re


def getGaragesList():
    garage_lst = []
    with open("example.csv", "r", encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            if row[16] not in ["", "Должник"]:
                garage_lst.append(row[0])
    return garage_lst


def clean_phone_number(phone_number):
    cleaned_number = re.sub(r'\D', '', phone_number)
    return cleaned_number


def get_ls_boxes(number_phone):
    number = number_phone
    with open('numbers.csv', 'r', encoding="utf-8") as File:
        a = []
        reader = csv.reader(File)
        for row in reader:
            a.append(row)
    ls_boxes = []
    for i, sublist in enumerate(a):
        for y, element in enumerate(sublist):
            if number in element:
                c = ''
                for i in sublist:
                    c += i
                c = c.split(';')
                ls_boxes.append(c[0])
    return ls_boxes

