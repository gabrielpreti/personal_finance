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

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF8')
    value = locale.atof(splitted[3].replace('R$', '').strip())

    return date, value, desc

def parse_pdf(input, output=sys.stdout):
    result = subprocess.run(['pdftotext', '-layout', input, '/dev/stdout', ], stdout=subprocess.PIPE)
    result = result.stdout.decode()
    results = re.compile('\n+').split(result)

    frame = pd.DataFrame(columns=('Data', 'Valor', 'Descrição'))
    for r in results:
        if re.match('^[0-9]{2}/[0-9]{2}/[0-9]{4}.+', r):
            print(parse_statement(r))
            frame.loc[len(frame)] = parse_statement(r)
    frame.to_excel(excel_writer=pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='mm/dd/yyyy'), columns=('Data', 'Valor', 'Descrição'), header=True, index=False)

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

    print('%s - %s' % (inputfile, outputfile))
    parse_pdf(inputfile, outputfile)
else:
    parse_pdf('/tmp/santander_cartao.pdf', '/tmp/santander_cartao.xlsx')