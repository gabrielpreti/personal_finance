import re

table_body_regex = re.compile('.*?<div.+class=\"tabla_datos\".*?>.*?<table>.*<tbody>(.*?)</tbody>', re.DOTALL)
table_line_regex = re.compile('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>.*?&nbsp;.*?</td>.*?<td.*?>.*?<p.*?>(.*?)</p>', re.DOTALL)

DEBITO_AUTOMATICO_DESCRIPTION='DEB. AUTOM. DE FATURA EM C/C'


with open(file='/tmp/cartao_santander.html', mode='r', encoding='utf8') as html:
    html_content = html.read()
    table_body = table_body_regex.match(html_content).group(0)
    lines = table_line_regex.findall(table_body)
    for (date, description, value) in lines:
        if description.strip() == DEBITO_AUTOMATICO_DESCRIPTION:
            continue
        print(description)