from bs4 import BeautifulSoup
import requests
import pandas 


class Frame():
    def __init__(self,df):
        self.df = df

    def main(self,count=0):

        # Шапка и запрос сайта с таблицей

        url = 'https://www.thecycledb.com/items'
        header = ['NAME','LOGO','K-MARKS VALUE','VALUE PER POUND','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
        soup = BeautifulSoup(requests.get(url).text,'lxml')

        items = []

        #-------------
        counter = 0
        #-------------

        # Основной модуль парсинга

        for item in soup.find_all('tr',class_='hover cursor-pointer group hover:active'):
            list=[item.find('th').text]                             # Парсинг имени

            s = soup.find_all('img',alt=list[0])[1]['src']          # Парсинг иконки по имени
            list.append(f'<img src="{s}" style="height:70px">')

            for element in item.find_all('td')[0:5]:                # Парсинг остальных элементов кроме последнего
                a = float(element.text.replace(',',''))
                if a % 1 == 0:
                    a = int(a)
                list.append(a)

            item_soup = BeautifulSoup(requests.get(url[:-1]+'/'+list[0].lower().replace("'",'').replace(' ','-')).text,'lxml')  # Парсинг последнего эелемента со страницы предмета
            try:
                a = item_soup.find('h3',string='Shop Price')
                list.append(int(a.next_element.next_element.text.replace(',','')))
            except(AttributeError):
                list.append(0)
            items.append(list)
        #-------------
            counter+=1
            if counter==count:
                break
        #-------------

        # Сохранение 

        self.df = pandas.DataFrame(items,columns=header,dtype=object) # dtype для того, чтобы столб воспринимал одновременно int и float, иначе будет автоконвертация
        pandas.options.display.float_format = '{:,}'.format # Сделал так, чтобы тысячи отделялись запятой, потому что так красивее

        header = ['LOGO','NAME','K-MARKS VALUE','VALUE PER POUND','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']  # Поменял местами картинки и названия, потому что так красивее
        self.df = self.df.reindex(columns=header)

    def save(self):
        self.df['PURCHASE/CRAFT COST'] = self.df['PURCHASE/CRAFT COST'].replace(0,'Cannot be bought',regex=True) # Изначально поставил нули, т.к. Pandas не может сравнивать числа и строки. Теперь меняю их а что-то покрасивее
        self.df.to_html('main.html',index=False) # Конвертировал в HTML и выключил индексы потому что зачем они нужны

        with open('main.html','r') as file: # Питон не понимает скобки, приходится заменять их прямо в файле, если бы не это, можно было бы использовать на один файл меньше
            filedata = file.read()
            filedata = filedata.replace('&lt;','<').replace('&gt;','>') 
        with open('main.html','w') as file:
            file.write(filedata)

    def merge(self):
        soup = BeautifulSoup(open('Origin.html'),'lxml')                 # Обёртка HTML, прописанная отдельно
        a = BeautifulSoup(open('main.html'),'lxml')                      # Сама таблица, конвертированная в HTML
        soup.body.append(a)                                              # Объединение файлов
        with open("index.html", "w") as file:                            # Запись нового файла
            file.write(str(soup))


    def compile(self,sort_by=None,asc=False,items=5): 
        self.main(items)
        if sort_by != None:
            self.df = self.df.sort_values(sort_by,ascending=asc)
        self.save()
        self.merge()



if __name__ == '__main__':
    obj = Frame(None)
    obj.compile('VALUE PER POUND',items=10,asc=False)