import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys
import re
import os

def req(url, index = 0):
    url = url.replace(".ru//", '.ru/')
    headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',}
    try:
        response = requests.post(url, headers=headers)
    except:
        url = url.replace("http:", 'https:')
        try:
            response = requests.post(url, headers=headers)
        except:
            index = index + 1
            if index == 3:
                return False
            return req(url, index)
    response.encoding = 'utf-8'
    return response.text


def getVikon(url):
    response = req(url)
    if not response:
        return []
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find_all("div", {"class": "vikon-row"})


def getH(text):
    soup = BeautifulSoup(str(text), 'html.parser')
    ret = soup.find("h4").get_text()
    return ret.strip()


def getTable(text):
    soup = BeautifulSoup(str(text), 'html.parser')
    return soup.find("table")


def get_thead(text):
    soup = BeautifulSoup(str(text), 'html.parser')
    head = soup.find("thead")
    soup = BeautifulSoup(str(head), 'html.parser')
    table_headers = []
    for tx in soup.find_all('th'):
        table_headers.append(tx.get_text())
    return table_headers


def get_tbody(text):
    soup = BeautifulSoup(str(text), 'html.parser')
    return soup.find("tbody")


def makelist(table):
    result = [[]]
    if table is None:
        return result 
    allrows = table.findAll('tr')
    for row in allrows:
        result.append([])
        allcols = row.findAll('td')
        for col in allcols:
            thestrings = [s for s in col.findAll(text=True)]
            thetext = ''.join(thestrings)
            result[-1].append(thetext)
    return result


def get_links(text):
    soup = BeautifulSoup(str(text), 'html.parser')
    a = []
    for link in soup.find_all('a', href=True):
        a.append(link['href'])
    a = list(set(a))
    return a



def parsingTable(text):
    text = str(text)
    table = getTable(text)
    thead = get_thead(table)
    tbody = get_tbody(table)
    if tbody is None:
        return []
    arr = makelist(tbody)
    arr[0] = thead
    return arr

def getTableByUrl(url):
    response = req(url)
    if not response:
        return ''
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find("table")

def save_file(folder, name, arr):
    with open(folder+"/"+name+".csv", "wb") as text_file:
        for m in range(0, len(arr)):
            string = ';'.join([str(elem).strip() for elem in arr[m]])
            string = string.replace("\n", "")
            string = string.strip()
            text_file.write(string.encode('utf-8'))
            text_file.write("\n".encode('utf-8'))
        text_file.close()

def getLinkOne(text):
    soup = BeautifulSoup(str(text), 'html.parser')
    a = []
    for link in soup.find_all('a', href=True):
        a.append(link['href'])
    a = list(set(a))
    return a

def proch(folder, name, a):
    table = parsingTable(a)
    save_file(folder, name, table)

df_ = pd.read_csv("univers.csv")
for p in range(176, len(df_['Сайт'])):
    # print(df_['Сайт'][0])
    print("_____", p, "_____")
    # print(df_['Сайт'][1])
    # print(df_['Сайт'][2])

    # url = 'http://amp1996.ru/sveden/employees/'
    url = df_['Сайт'][p]
    parsed_url = urllib.parse.urlparse(url)
    folder = 'data/'+ parsed_url.netloc
    parsed_url = parsed_url.scheme + '://' + parsed_url.netloc
    print(url+'/sveden/employees/')
    try:
        os.makedirs(folder)
        print("Directory ", folder,  " Created ")
    except FileExistsError:
        print("Directory ", folder,  " already exists")
    
    
    a = getVikon(url+'/sveden/employees/')
    print(len(a))
    for a_i in range(0, len(a)):
        try:
            name = getH(a[a_i])
        except:
            continue
        if name == 'Информация о руководителе образовательной организации':
            proch(folder, name, a[a_i])
        if name == 'Информация о заместителях руководителя образовательной организации':
            proch(folder, name, a[a_i])
        if name == 'Информация о руководителях филиалов образовательной организации':
            proch(folder, name, a[a_i])
        if name == 'Члены ученого совета':
            proch(folder, name, a[a_i])

        if name == 'Научные работники':
            table = parsingTable(a[a_i])
            if table is None or len(table) == 0:
                l = getLinkOne(a[a_i])
                if len(l) == 1:
                    url__link = parsed_url + l[0]
                    table = getVikon(url__link)
                    table = parsingTable(table[0])
            save_file(folder, name, table)
        
        if name == 'Информация о представителях работодателей':
            proch(folder, name, a[a_i])
        if name == 'Информация о прочих сотрудниках организации':
            proch(folder, name, a[a_i])

        if name == 'Информация о персональном составе педагогических работников каждой реализуемой образовательной программы':
            table = getTable(a[a_i])
            if table is None:
                l = getLinkOne(a[a_i])
                if len(l) == 1:
                    url__link = parsed_url + l[0]
                    table = getVikon(url__link)
                    name = getH(a[a_i])
                    if name != 'Информация о персональном составе педагогических работников каждой реализуемой образовательной программы':
                        print("Not found table 4")
                    table = getTable(table)
            thead = get_thead(table)
            tbody = get_tbody(table)
            if tbody is not None:
                arr = makelist(tbody)
                links = get_links(a[a_i])
                arr[0] = thead
            if len(links) < 2 or links is None:
                save_file(folder, name, arr)
            else:
                for k in range(0, len(links)):
                    number_nap = re.search('[0-9][0-9].[0-9][0-9].[0-9][0-9]', links[k])
                    if number_nap:
                        number_nap = number_nap.group(0)
                        number_nap.replace('.','_')
                    else:
                        number_nap = str(k)
                    url__link = parsed_url + links[k] 
                    print(url__link)
                    table_link = getTableByUrl(url__link)
                    thead_link = get_thead(table_link)
                    tbody_link = get_tbody(table_link)
                    if tbody is None:
                        continue
                    arr_link = makelist(tbody_link)
                    arr_link[0] = thead_link
                    save_file(folder, number_nap, arr_link)
