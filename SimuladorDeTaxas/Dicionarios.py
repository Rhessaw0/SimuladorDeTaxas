import json
import pathlib
import os

Dic = {
    'Admin': '5254302579',
    '5254302579': ['Saymon', 'senha'],
}

def ler(file):
    try:
        nome = file
        with open(nome, 'r') as input:
            resultado = json.load(input)
        print('pog')
    except:
        nome = file + '.json'
        with open(nome, 'r') as input:
            resultado = json.load(input)
        print('sadge')
    finally:
        return resultado

def escrever(file, dic):
    with open((file), 'w') as output:
        output.write(json.dumps(dic))

def paraDic(file):
    print()

filepath = os.path.realpath(__file__)
dirPath = os.path.dirname(filepath)

escrever('Ledger.json', Dic)