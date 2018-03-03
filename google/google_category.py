import requests

r = requests.get(
    'https://www.google.com/basepages/producttype/taxonomy-with-ids.it-IT.txt')
text = r.text
lines = text.splitlines()
result = []
for n, line in enumerate(lines):
    if n != 0:
        current = {}
        for i, element in enumerate(line.split('-')):
            if i == 0:
                current['id'] = element.lstrip()
            elif i == 1:
                current['value'] = element.lstrip()
            else:
                current['value'] = current['value'] + ' > ' + element.lstrip()
        result.append(current)

# https://www.google.com/basepages/producttype/taxonomy-with-ids.it-IT.txt
