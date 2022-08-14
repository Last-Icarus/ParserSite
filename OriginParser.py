from bs4 import BeautifulSoup
import requests
import pandas 



def save():
    df.to_html('main.html',index=False)
    with open('main.html','r') as file:
        filedata = file.read()
        filedata = filedata.replace('&lt;','<').replace('&gt;','>') # Питон не понимает скобки, приходится заменять их прямо в файле
    with open('main.html','w') as file:
        file.write(filedata)

def merge():
    soup = BeautifulSoup(open('Origin.html'),'lxml')                 # Обёртка HTML
    a = BeautifulSoup(open('main.html'),'lxml')                      # Сама таблица, переконвертированная в HTML
    soup.body.append(a)                                              # Объединение файлов
    with open("index.html", "w") as file:                            # Запись нового файла
        file.write(str(soup))

def main(count=5):
    url = 'https://www.thecycledb.com/items'
    header = ['NAME','LOGO','K-MARKS VALUE','VALUE PER WEIGHT','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
    soup = BeautifulSoup(requests.get(url).text,'lxml')

    items = []
    #-------------
    counter = 0
    #-------------

    for item in soup.find_all('tr',class_='hover cursor-pointer group hover:active'):
        list=[item.find('th').text]
        s = soup.find_all('img',alt=list[0])[1]['src']
        list.append(f'<img src="{s}" style="height:70px">')
        for element in item.find_all('td')[0:5]:
            a = float(element.text.replace(',',''))
            if a % 1 == 0:
                a = int(a)
            list.append(a)

        item_soup = BeautifulSoup(requests.get(url[:-1]+'/'+list[0].lower().replace("'",'').replace(' ','-')).text,'lxml')  # Парсинг рыночной стоимости с заходом на страницу предмета
        try:
            a = item_soup.find('h3',string='Shop Price')
            list.append(a.next_element.next_element.text.replace(',',''))
        except(AttributeError):
            list.append("Can't be bought")
        items.append(list)
    #-------------
        counter+=1
        if counter==count:
            break
    #-------------

    global df                                                         # global позволяет манипулировать таблицей на всех уровнях(Заглушка, потом реализую через ООП)
    df = pandas.DataFrame(items,columns=header)
    pandas.options.display.float_format = '{:,}'.format
    header = ['LOGO','NAME','K-MARKS VALUE','VALUE PER WEIGHT','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
    df = df.reindex(columns=header)


def compile(sort_by=None,asc=False): 
    main(6)
    if sort_by != None:
        global df
        df = df.sort_values(sort_by,ascending=asc)
    save()
    merge()

if __name__ == '__main__':
    compile('K-MARKS VALUE')


