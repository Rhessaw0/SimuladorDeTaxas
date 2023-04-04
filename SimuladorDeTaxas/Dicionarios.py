import json
import pathlib
import os

taxaDic = {
    'Valor': '0',
    'Prazo': '0',
    'Taxa': '0',
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
print(dirPath)

file = '5254302571.json'
filePath = dirPath + r'\Users\\' + file

root, targetPath = os.path.splitext(filePath)
output = ler(filePath)

print(output)

output['Valor'] = 17
output2 = output['Valor']

print(output)
print(output2)