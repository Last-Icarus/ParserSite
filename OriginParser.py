from itertools import count
from bs4 import BeautifulSoup
import requests
import pandas 

def save():
    with open('C:/Users/MihaNik/Desktop/VsCodeCode/projects/main.html', 'r') as file:
        filedata = file.read()
        filedata = filedata.replace('&lt;','<').replace('&rt;','>')
    with open('C:/Users/MihaNik/Desktop/VsCodeCode/projects/main.html', 'w') as file:
        file.write(filedata)



# Main parser module

url = 'https://www.thecycledb.com/items'
header = ['NAME','LOGO','K-MARKS VALUE','VALUE PER WEIGHT','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']

soup = BeautifulSoup(requests.get(url).text,'lxml')

items = []
counter = 0

for item in soup.find_all('tr',class_='hover cursor-pointer group hover:active'):
    list=[item.find('th').text]
    s = soup.find_all('img',alt=list[0])[1]['src']
    list.append(f'<img src="{s}" style="height:70px">')
    for element in item.find_all('td')[0:5]:
        list.append(element.text)
    item_soup = BeautifulSoup(requests.get(url[:-1]+'/'+list[0].lower().replace("'",'').replace(' ','-')).text,'lxml')
    try:
        a = item_soup.find('h3',string='Shop Price')
        list.append(a.next_element.next_element.text)
    except(AttributeError):
        list.append("Can't be bought")
        print(url[:-1]+'/'+list[0].lower())

    items.append(list)
    counter += 1
    if counter == 10:
        break


df = pandas.DataFrame(items,columns=header)

columns_titles = ['LOGO','NAME','K-MARKS VALUE','VALUE PER WEIGHT','FACTION XP','XP PER POUND','WEIGHT','PURCHASE/CRAFT COST']
df = df.reindex(columns=columns_titles)
df.to_html('C:/Users/MihaNik/Desktop/VsCodeCode/projects/main.html')

save()

#----------------------------------------------------------------------------------------------------------------------




soup = BeautifulSoup(open('C:/Users/MihaNik/Desktop/VsCodeCode/Projects/Origin.html'),'lxml')

a = BeautifulSoup(open('C:/Users/MihaNik/Desktop/VsCodeCode/Projects/main.html'),'lxml')


soup.body.append(a)



with open("C:/Users/MihaNik/Desktop/VsCodeCode/Projects/child.html", "w") as file:
    file.write(str(soup))
#print(soup.prettify())