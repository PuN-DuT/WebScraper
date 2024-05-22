import os
from datetime import datetime
import PySimpleGUI as sg
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import get


def soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/107.0.0.0 Safari/537.36'
    }
    page = get(url, headers=headers)
    return BeautifulSoup(page.text, 'html.parser')


def write_csv(name, dataframe):
    if not os.path.isdir(''):
        os.mkdir('')
    file_name = datetime.now().strftime(f'{name}_%Y-%m-%d_%H-%M.csv')
    dataframe.to_csv(f'Yahoo screeners/{file_name}')


def progress_bar(current_value, end):
    sg.one_line_progress_meter('Progress',
                               orientation='h',
                               no_titlebar=True,
                               no_button=True,
                               current_value=current_value,
                               max_value=end)


def scraper(url):
    screener_url = f'{url}?count=100&offset=0'
    soup_screener = soup(screener_url)

    columns_name = list(map(lambda x: x.string, soup_screener.find('tr').find_all('th', string=True)))[:-1]

    file_name = soup_screener.find('h1',
                                   class_='Fw(b) Fz(17px) D(ib)',
                                   string=True).string

    rows_count = soup_screener.find('span',
                                    class_='Mstart(15px) Fw(500) Fz(s)',
                                    string=True).string.split()[2]

    page_count = int(rows_count) // 100 + 1
    screener_page_all = []

    for page_num in range(page_count + 1):
        progress_bar(current_value=page_num, end=page_count)

        if page_num < page_count:
            url = screener_url[:-1] + str(page_num * 100)

            screener_elements = soup(url).find_all('tr')
            screener_page = map(lambda screener_element:
                                list(map(lambda name: screener_element.find(attrs={'aria-label': name},
                                                                            string=True).string,
                                         columns_name)),
                                screener_elements[1:])
            screener_page_all.extend(screener_page)

    df_stocks = DataFrame(screener_page_all, columns=columns_name)
    write_csv(file_name, df_stocks)


def main():
    base_url = 'https://finance.yahoo.com'

    soup_all_screeners = soup(f'{base_url}/screener').find_all('tr')
    screeners = dict(map(lambda el: (el.td.find('a', string=True).string, el.td.find('a', href=True)['href']),
                         soup_all_screeners[1:]))

    layout = [[sg.Combo(list(screeners.keys()),
                        default_value='Выберите скринер',
                        enable_events=True,
                        readonly=True,
                        key='-COMBO-')],
              [sg.Text('', expand_x=True)],
              [sg.Text('Начать парсинг?'), sg.Button('Ok'), sg.Button('Отмена')]]

    window = sg.Window('Scraper Yahoo', layout)
    flag = False

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Отмена':
            break
        if event == '-COMBO-':
            flag = True
            screener_url = screeners[values['-COMBO-']]
            url = f'{base_url}{screener_url[:-1]}'
        if event == 'Ok' and flag:
            scraper(url)
            sg.popup('Успешно', no_titlebar=True)

    window.close()


if __name__ == '__main__':
    main()
