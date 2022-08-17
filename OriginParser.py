from bs4 import BeautifulSoup
import requests
import pandas 
import asyncio
import aiohttp
import timeit

class Frame():
    def __init__(self,df = None,items = []):
        self.df = df
        self.items = items
    def main(self):
        print('Starting main')
        print('Parsing columns')
        url = 'https://www.thecycledb.com/items'
        header = ['NAME','LOGO','K-MARKS VALUE','VALUE PER POUND','FACTION XP','XP PER POUND','WEIGHT']
        soup = BeautifulSoup(requests.get(url).text,'lxml')


        add_list = []
        for item in soup.find_all('tr',class_='hover cursor-pointer group hover:active'):  # Парсинг всех элементов таблицы
            # Парсинг параметров для каждого элемента
            # Сначала идёт парсинг названия затем по названию идёт парсинг картинки элемента
            # Такой порядок выглядит не очень, но без названия не найти картинку, т.к. различить их можно только по параметру alt
            # Чтобы было красивее, я потом меняю столбцы названия и изображений
            list=[item.find('th').text]                             
            add_list.append(item.find('th').text)
            s = soup.find_all('img',alt=list[0])[1]['src']          
            list.append(f'<img src="{s}" style="height:70px">')

            # Парсинг оставшихся элементов (кроме последнего столбца, с ним сложнее)
            for element in item.find_all('td')[0:5]:                
                a = float(element.text.replace(',',''))
                if a % 1 == 0:
                    a = int(a)          # конвертация в int позволяет не отображать .0 у чисел без дробной части, так красивее
                list.append(a)

            self.items.append(list)


        print('Creating main df')
        self.df = pandas.DataFrame(self.items,columns=header,dtype=object) 
        pandas.options.display.float_format = '{:,}'.format 

        # Меняю местами столб с изображениями и названиями
        header[0], header[1] = header[1], header[0]     
        self.df = self.df.reindex(columns=header)

        # Парсинг последнего столбца. Для этого надо заходить на страницу каждого элемента отдельно.   
        # Это очень долго, если делать это обычным способом, поэтому использовался асинхронный метод
        self.items = []
        print('Async parsing last column')
        for i in range(3):                  # Если делать все 246 запросов за раз, то сайт перестаёт отвечать, поэтому я сделал три раза по 82. Медленнее, зато работает
            asyncio.run(self.parse(i+1))
        print('Parsing is done')
        print('Appending the column')
        self.df['PURCHASE/CRAFT COST'] = self.items       


    # Асинхронный парсинг последнего столбца
    # Сайт не позволяет делать слишком много запросов за раз, поэтому полностью ассинхронного парсинга не вышло, вместо это пришлось парсить по 82 элемента за раз
    # Намного медленнее, чем делать это полностью ассинхронно, но это единственный способ заставить это работать
    # И даже так программа работает в четыре раза быстрее, так что я не жалею, что заморочился
    async def parse(self,i):
        async with aiohttp.ClientSession() as session:

            price = []
            tasks = self.get_tasks(session,i)    

            responses = await asyncio.gather(*tasks) 

            for i in responses:                                                            
                item_soup = BeautifulSoup(await i.text(),'lxml')  
                try:
                    a = item_soup.find('h3',string='Shop Price')
                    price.append(int(a.next_element.next_element.text.replace(',','')))
                except(AttributeError):
                    price.append(0)

            self.items += price

    def get_tasks(self,session,i):
        print('Parsing:', i,'/ 3')
        tasks = []
        data = self.df['NAME'].tolist()
        for i in data[(i-1)*82:i*82]:
            tasks.append(asyncio.create_task(session.get('https://www.thecycledb.com/item/'+i.lower().replace("'",'').replace(' ','-')))) #iterate every URL
        return tasks


    def save(self):
        print('Saving...')
        # Не у всех предметов есть цена, поэтому для них было присвоено значение 0 для того, чтобы работала без конфликтов 
        # Если сразу вставлять надпись, то сортировка выдаст ошибку при попытке сравнить числа и строки.
        # Потому замена нуля на надпись просходит уже после потенциальной сортировки
        self.df['PURCHASE/CRAFT COST'] = self.df['PURCHASE/CRAFT COST'].replace(0,'Cannot be bought',regex=True) 

        # Сохранение таблицы в формат .html
        self.df.to_html('main.html',index=False)
        # При конвертации в html теряются скобки, приходится их возвращать. Костыль, но лучше способа я не нашёл
        with open('main.html','r') as file: 
            filedata = file.read()
            filedata = filedata.replace('&lt;','<').replace('&gt;','>') 
        with open('main.html','w') as file:
            file.write(filedata)

    def merge(self):
        # Сама по себе конвертированная в html таблица выглядит грустно
        # Поэтому я связываю её с html с прописанным head`ом, в котором идёт связка с CSS
        #   Технически, можно было обыграть эту ситуацию через текстовые файлы (html можно и в одну строку написать), но код не стал
        # хоть сколько-нибудь медленее или нечитаемее, поэтому нет смысла жертвовать удобством редактирования
        print('Merging htmls')
        soup = BeautifulSoup(open('Origin.html'),'lxml')                
        a = BeautifulSoup(open('main.html'),'lxml')                     
        soup.body.append(a)                                             
        with open("index.html", "w") as file:                            
            file.write(str(soup))

    # Просто запуск всех функций в нужно порядке с возможностью ипользовать параметры сортировки
    def compile(self,sort_by=None,asc=False): 
        print('Start compiling')
        self.main()
        if sort_by != None:
            self.df = self.df.sort_values(sort_by,ascending=asc)
        self.save()
        self.merge()



# Основной модуль запуска
#   В obj.compile можно прописать параметры sort_by и asc, которые отвечают за то, по какому столбцу будет 
# сортировка и будет ли она убывающей (asc=True) или возрастающей(asc=False)
# Столбцы можно сортировать по названию:
# ['NAME','LOGO','K-MARKS VALUE','VALUE PER POUND','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
if __name__ == '__main__':
    a = timeit.default_timer() # Считает время выполнения

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Убирает RuntimeError

    obj = Frame()
    obj.compile()

    print()
    print("Done in {:.5f}".format(timeit.default_timer() - a),'seconds')
    print()
