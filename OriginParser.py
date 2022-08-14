from bs4 import BeautifulSoup
import requests
import pandas 

def save():
    df.to_html('main.html',index=False)
    with open('main.html','r') as file:
        filedata = file.read()
        filedata = filedata.replace('&lt;','<').replace('&rt;','>') # Питон не понимает скобки, приходится заменять их прямо в файле
    with open('main.html','w') as file:
        file.write(filedata)

def sort(sort_by=None,asc=False):
    if sort_by == None:
        return
    global df                                                       # global позволяет манипулировать таблицей на всех уровнях
    column_list = []
    if sort_by=='NAME':                                             # Случай, когда у нас идёт сортировка по названию
        df = df.sort_values('NAME',ascending=asc)
        return
    for i in df[sort_by]:
        try: 
            column_list.append(float(i.replace(',','')))            # Сортировка чисел. Весь этот модуль существует только потому, что числа записываются через чёртову запятую
        except(ValueError):                                         # Но что поделать, так красиво
            column_list.append(0)                                   # Некоторые предметы не имеют стоимости, тогда вместо ошибки значения им будет присвоен ноль
    df['SortCol']=column_list
    df = df.sort_values('SortCol',ascending=asc)
    del df['SortCol']

def merge():
    soup = BeautifulSoup(open('Origin.html'),'lxml')                 # Обёртка HTML
    a = BeautifulSoup(open('main.html'),'lxml')                      # Сама таблица, переконвертированная в HTML
    soup.body.append(a)                                              # Объединение файлов
    with open("child.html", "w") as file:                            # Запись нового файла
        file.write(str(soup))

def main():
    url = 'https://www.thecycledb.com/items'
    header = ['NAME','LOGO','K-MARKS VALUE','VALUE PER WEIGHT','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
    soup = BeautifulSoup(requests.get(url).text,'lxml')

    items = []

    for item in soup.find_all('tr',class_='hover cursor-pointer group hover:active'):
        list=[item.find('th').text]
        s = soup.find_all('img',alt=list[0])[1]['src']
        list.append(f'<img src="{s}" style="height:70px">')
        for element in item.find_all('td')[0:5]:
            list.append(element.text)

        item_soup = BeautifulSoup(requests.get(url[:-1]+'/'+list[0].lower().replace("'",'').replace(' ','-')).text,'lxml')  # Парсинг рыночной стоимости с заходом на страницу предмета
        try:
            a = item_soup.find('h3',string='Shop Price')
            list.append(a.next_element.next_element.text)
        except(AttributeError):
            list.append("Can't be bought")
        items.append(list)

    global df                                                        # global позволяет манипулировать таблицей на всех уровнях
    df = pandas.DataFrame(items,columns=header)
    columns_titles = ['LOGO','NAME','K-MARKS VALUE','VALUE PER WEIGHT','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
    df = df.reindex(columns=columns_titles)


def compile(sort_by=None): 
    main()
    sort(sort_by)
    save()
    merge()

if __name__ == '__main__':
    compile()