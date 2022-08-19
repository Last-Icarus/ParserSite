Простая программа на Python для обучения парсингу 

[Оригинальная таблица](https://www.thecycledb.com/items)

[Результат](https://last-icarus.github.io/ParserSite/)
____
Изначально я планировал сделать свой парсер с нуля, обрабатывая полученные через библиотеку request данные, но очень быстро осознал, насколько это смелая и ненужная задумка. Потому быстро перешёл к уже готовым инструментам. Изначально подразумевалось сделать программу, которая просто будет собирать данные с одной страницы, но в итоге пришёл к асинхронному парсингу страниц с записью данных в Pandas Dataframe, который конвертируется в таблицу HTML с настраиваемым отдельно head`ом. 

Также пришлось писать не простой последовательный код, а реализовать всё через методы класса. Сначала я разделили всю программу на набор функций для логического разделения программы на удобно редактируемые модули. Затем возникла ожидаемая проблемы с инкапсуляцией при работе с общими элементами, потому я привёл всё к одному классу.

Визуальное оформление я решил сделать через HTML + CSS. Для меня это наиболее знакомый, удобный и быстрый способ привести таблицу к читаемому виду. Тем более что делаю я это для подготовки к полноценному проекту на Django. Для этого с помощью метода библиотеки BeautifulSoup я объединил заранее заготовленный HTML с прописанным head`ом, у которого идёт привязка к CSS, и HTML-таблицу, которую я вывожу с помощью Pandas. При желании до конвертации я могу проводить с таблицей любые вычисления, которые мне может позволить Pandas и matplotlib, но для такого простого массива данных я не стал реализовывать ничего сложнее чем простая сортировка по столбцу

Главная проблема всей программы - это невозможность асинхронно сделать запрос для каждого из 246 элементов. Сайт за раз позволяет сделать фиксированное ограниченное количество запросов за раз, потому самым простым решением было сделать порционные запросы, чтобы сайт не прерывал передачу данных. С другими сайтами такой проблемы нет, поэтому полагаю, что это индивидуальная проблема этого сайта. Тем не менее, использование ассинхронного метода ускорило парсинг примерно в четыре раза (с 40 секунд до 9-12 секунд). При этом основную часть временм занимает парсинг индивидуальных страниц (и всё из-за необходимости делать паузы между запросами). Без них компиляция проходит меньше чем за 2 секунды. 

