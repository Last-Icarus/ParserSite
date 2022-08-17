from bs4 import BeautifulSoup
import requests
import pandas 
import asyncio
import aiohttp
import timeit

class Frame():
    def __init__(self,df,items):
        self.df = df
        self.items = items
    def main(self,count=0):


        url = 'https://www.thecycledb.com/items'
        header = ['NAME','LOGO','K-MARKS VALUE','VALUE PER POUND','FACTION XP','XP PER POUND','WEIGHT']
        soup = BeautifulSoup(requests.get(url).text,'lxml')



        add_list = []
        for item in soup.find_all('tr',class_='hover cursor-pointer group hover:active'):
            list=[item.find('th').text]                             
            add_list.append(item.find('th').text)
            s = soup.find_all('img',alt=list[0])[1]['src']          
            list.append(f'<img src="{s}" style="height:70px">')

            for element in item.find_all('td')[0:5]:                
                a = float(element.text.replace(',',''))
                if a % 1 == 0:
                    a = int(a)
                list.append(a)

            self.items.append(list)



        self.df = pandas.DataFrame(self.items,columns=header,dtype=object) 
        pandas.options.display.float_format = '{:,}'.format 

        header = ['LOGO','NAME','K-MARKS VALUE','VALUE PER POUND','FACTION XP','XP PER POUND','WEIGHT']  
        self.df = self.df.reindex(columns=header)
        self.items = []
        for i in range(3):
            asyncio.run(self.parse(i+1))
        self.df['PURCHASE/CRAFT COST'] = self.items       


    def save(self):
        self.df['PURCHASE/CRAFT COST'] = self.df['PURCHASE/CRAFT COST'].replace(0,'Cannot be bought',regex=True) 
        self.df.to_html('main.html',index=False)

        with open('main.html','r') as file: 
            filedata = file.read()
            filedata = filedata.replace('&lt;','<').replace('&gt;','>') 
        with open('main.html','w') as file:
            file.write(filedata)

    def merge(self):
        soup = BeautifulSoup(open('Origin.html'),'lxml')                
        a = BeautifulSoup(open('main.html'),'lxml')                     
        soup.body.append(a)                                             
        with open("index.html", "w") as file:                            
            file.write(str(soup))


    def compile(self,sort_by=None,asc=False,items=5): 
        
        self.main(items)
        if sort_by != None:
            self.df = self.df.sort_values(sort_by,ascending=asc)
        self.save()
        self.merge()



    def get_tasks(self,session,i):
        tasks = []
        data = self.df['NAME'].tolist()
        for i in data[(i-1)*82:i*82]:
            tasks.append(asyncio.create_task(session.get('https://www.thecycledb.com/item/'+i.lower().replace("'",'').replace(' ','-')))) #iterate every URL
        return tasks


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


if __name__ == '__main__':
    a = timeit.default_timer()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
    obj = Frame(None,[])
    obj.compile(items = 0)
    print()
    print(timeit.default_timer() - a)
    print("DONE")


