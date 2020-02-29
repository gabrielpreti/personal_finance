# -*- coding: utf-8 -*-

import subprocess
import re
from datetime import datetime
import locale
import pandas as pd
import sys, getopt

def parse_statement(rawstatement):
    splitted = re.split('\s{2,}', rawstatement)
    date = datetime.strptime(splitted[0], '%d/%m/%Y')
    desc = splitted[1]

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    value = locale.atof(splitted[3].replace('R$', '').strip())

    return date, value, desc

def parse_pdf(input, output=sys.stdout):
    result = subprocess.run(['pdftotext', '-layout', '-enc',  'UTF-8', input, '/dev/stdout', ], stdout=subprocess.PIPE)
    result = result.stdout.decode()
    results = re.compile('\n+').split(result)

    frame = pd.DataFrame(columns=('Data', 'Valor', 'Descrição'))
    for r in results:
        if re.match('^[0-9]{2}/[0-9]{2}/[0-9]{4}.+', r):
            print(parse_statement(r))
            frame.loc[len(frame)] = parse_statement(r)

    excel_writer = pd.ExcelWriter(path=output, engine='xlsxwriter', datetime_format='mm/dd/yyyy')
    frame.to_excel(excel_writer, columns=('Data', 'Valor', 'Descrição'), header=True, index=False)
    excel_writer.save()

def parse_html(input_file, output=sys.stdout):
    table_body_regex = re.compile('.*?<div.+class=\"tabla_datos\".*?>.*?<table>.*<tbody>(.*?)</tbody>', re.DOTALL)
    table_line_regex = re.compile(
        '<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>.*?&nbsp;.*?</td>.*?<td.*?>.*?<p.*?>(.*?)</p>', re.DOTALL)
    DEBITO_AUTOMATICO_DESCRIPTION = 'DEB. AUTOM. DE FATURA EM C/C'
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    frame = pd.DataFrame(columns=('Data', 'Valor', 'Descrição'))
    with open(file=input_file, mode='r', encoding='utf8') as html:
        html_content = html.read()
        table_body = table_body_regex.match(html_content).group(0)
        lines = table_line_regex.findall(table_body)
        for (date, description, value) in lines:
            if description.strip() == DEBITO_AUTOMATICO_DESCRIPTION:
                continue
            if not date.strip() or not description.strip() or not value.strip():
                print("Warning: ignoring line date='%s' description='%s' value='%s'" % (date.strip(), description.strip(), value.strip()))
                continue

            date = datetime.strptime(date.strip(), '%d/%m/%Y')
            description = description.strip()
            value = locale.atof(value.replace('R$', '').strip())

            frame.loc[len(frame)] = (date, value, description)

    print(frame)
    frame.to_excel(excel_writer=pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='mm/dd/yyyy'),
                   columns=('Data', 'Valor', 'Descrição'), header=True, index=False)



if __name__ == "__main__":
    argv = sys.argv[1:]
    print(argv)
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:")
    except getopt.GetoptError:
        print
        'santander_pdf_parser.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print
            'santander_pdf_parser.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if inputfile.endswith('pdf'):
        parse_pdf(inputfile, outputfile)
    else:
        parse_html(inputfile, outputfile)
else:
    #parse_html('/tmp/cartao_santander.html', '/tmp/santander_cartao.xlsx')
    parse_pdf('/tmp/cartao_santander.pdf', '/tmp/cartao_santander.xlsx')
