import requests


def get_google_categories():
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
                    current['id'] = element.lstrip().rstrip()
                elif i == 1:
                    current['value'] = element.lstrip()
                else:
                    current['value'] = current['value'] + \
                        ' > ' + element.lstrip()
            result.append(current)
    return result

    # https://www.google.com/basepages/producttype/taxonomy-with-ids.it-IT.txt
