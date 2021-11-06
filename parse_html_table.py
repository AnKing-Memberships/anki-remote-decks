from bs4 import BeautifulSoup

with open("clozeAnking.html") as f:
    html = f.read()
    
soup = BeautifulSoup(html, "html.parser")
tables = soup.find_all("table")
table = tables[3]
result = []
for i, row in enumerate(table.find_all('tr')):
    result.append([])
    for j, column in enumerate(row.find_all('td')):
        result[-1].append(column)
print(result)
