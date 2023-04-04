import telebot
import json
import os

BotKey = "6169247456:AAGpUvK2yl-FGdTPyu4HUkSrY3HypMbCJo4"

bot = telebot.TeleBot(BotKey)

truePath = os.path.realpath(__file__)
dirPath = os.path.dirname(truePath)
usersPath = dirPath + r'\Users\\'

def formatar(num):
    texto = f'{num:,.2f}'.replace(',', '/').replace('.', ',').replace('/', '.')
    resultado = "R$ " + texto
    return resultado

def enviarResultado(mensagem, resultado):
    bot.send_message(mensagem.chat.id, resultado)

def ler(file):
    root, extension = os.path.splitext(file)
    if(extension == '.json'):
        nome = file
        with open(nome, 'r') as input:
            resultado = json.load(input)
    else:
        nome = file + '.json'
        with open(nome, 'r') as input:
            resultado = json.load(input)
    return resultado

def escrever(file, dic):
    if '.json' in file:
        nome = file
        with open(nome, 'w') as output:
            output.write(json.dumps(dic))
    else:
        nome = file + '.json'
        with open(nome, 'w') as output:
            output.write(json.dumps(dic))

def login(mensagem):
    checarArquivo(mensagem.chat.id)    
    msg = bot.send_message(mensagem.chat.id, "Qual é o seu nome de usuário?")
    bot.register_next_step_handler(msg, loginNext)

def loginNext(mensagem):
    path = usersPath + str(mensagem.chat.id)
    inputUser = ler(path)

    inputUser['Recente'] = mensagem.text
    escrever(path, inputUser)

    msg = bot.send_message(mensagem.chat.id, "Qual é a sua senha?")
    bot.register_next_step_handler(msg, loginFinal)

def loginFinal(mensagem):
    path = usersPath + str(mensagem.chat.id)
    inputUser = ler(path)

    checarLogin(mensagem, inputUser['Recente'], mensagem.text)

def checarLogin(mensagem, usuario, senha):
    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)

    try:
        if(ledger[usuario] == senha):
            checarAdmin(mensagem)
    except:
        bot.send_message(mensagem.chat.id, "Seu usuário ou senha estão incorretos. Você também pode não ser um usuário registrado.")
        
def checarAdmin(mensagem):
    userID = mensagem.chat.id
    path = usersPath + str(userID)
    inputUser = ler(path)
            
    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)
    
    if ledger['Admin'] == str(userID):
        bot.send_message(userID, "Bem Vindo, Administrador!")
        
        inputUser['Sessao'] = 1
        
        escrever(path, inputUser)
        
        menuAdmin(mensagem)
    else:
        bot.send_message(userID, "Bem Vindo!")
        
        inputUser['Sessao'] = 2
        
        escrever(path, inputUser)
        
        menu(mensagem)

def checarArquivo(file):
    path = usersPath + str(file)
    try:
        ler(path)
    except:
        template = {
        'Valor': '0',
        'Prazo': '0',
        'Taxa': '0',
        'Modo': 'Limite',
        'Recente': '',
        'Sessao': 0
        }

        escrever(path, template)
    finally:
        pass

def checarDigito(mensagem, valor):
    if valor.isdigit():
        return True
    else:
        bot.send_message(mensagem.chat.id, "Isso não é um número. Por favor tente novamente, confirmando que apenas números foram enviados")

def validarSessao(mensagem, requerimento):
    userID = mensagem.chat.id
    path = usersPath + str(userID)
    inputUser = ler(path)

    sessao = inputUser['Sessao']

    if sessao == requerimento:
        pass
    else:
        bot.send_message(mensagem.chat.id, "O usuário não possui permissão para usar este comando.")

def imprimirSimulacao(nomes, valores):
    resposta = ["SIMULAÇÃO REDECRED\n"]

    for n, v in zip (nomes, valores):
            linha = (f"{n : <}{':' : ^1}{'' : ^2}{v : >}")
            resposta.append(linha)
    
    respostaFinal = '\n'.join(resposta)
    print(respostaFinal)
    return respostaFinal

def calcularSimulacao(file):
    inputTaxa = ler(dirPath + r"\Taxas.json")
    inputUser = ler(file)

    i_valor = inputUser['Valor']
    i_prazo = inputUser['Prazo']
    i_modo = inputUser['Modo']

    valor = int(i_valor)
    prazo = int(i_prazo)

    r_taxa = int(inputTaxa[str(prazo)])
    taxaQ = (100 + r_taxa) / 100
    taxaL = r_taxa / 100
    
    if(i_modo == 'Quantia'):
        total = valor * taxaQ
        parcela = total / prazo
    elif(i_modo == 'Limite'):
        abatimento = valor * taxaL
        total = valor - abatimento
        parcela = valor / prazo
        

    nomes = ['VALOR LIBERADO', 'PRAZO', 'PARCELA', 'TOTAL']
    valores = [valor, prazo, parcela, total]

    p_valor = formatar(valores[0])
    p_prazo = str(valores[1]) + "x"
    p_parcela = formatar(valores[2])
    p_total = formatar(valores[3])

    valoresString = [p_valor, p_prazo, p_parcela, p_total]

    resultado = imprimirSimulacao(nomes, valoresString)
    
    return resultado

@bot.message_handler(commands=["Quantia"])
def simularQuantia(mensagem):
    path = usersPath + str(mensagem.chat.id)
    input = ler(path)
    
    input['Modo'] = 'Quantia'
    
    escrever(path, input)
    
    msg = bot.send_message(mensagem.chat.id, "Qual é o valor?")
    bot.register_next_step_handler(msg, simularValor) 
    pass

@bot.message_handler(commands=["Limite"])
def simularLimite(mensagem):
    path = usersPath + str(mensagem.chat.id)
    input = ler(path)
    
    input['Modo'] = 'Limite'
    
    escrever(path, input)
    
    msg = bot.send_message(mensagem.chat.id, "Qual é o valor?")
    bot.register_next_step_handler(msg, simularValor) 
    pass

@bot.message_handler(commands=["Simular"])
def simular(mensagem):
    text = """
    Deseja simular por Quantia ou Limite?

    /Quantia Aplicar juros em cima do valor
    /Limite Aplicar abatimento no limite
    """
    bot.send_message(mensagem.chat.id, text)
    pass

def simularValor(mensagem):
    path = usersPath + str(mensagem.chat.id)
    input = ler(path)
    valor = mensagem.text
    if checarDigito(mensagem, valor): 
        input['Valor'] = valor
        
        escrever(path, input)
        
        msg = bot.send_message(mensagem.chat.id, "Qual é o Prazo?")
        bot.register_next_step_handler(msg, simularPrazo)

def simularPrazo(mensagem):
    path = usersPath + str(mensagem.chat.id)
    input = ler(path)
    prazo = mensagem.text
    if checarDigito(mensagem, prazo): 
        input['Prazo'] = prazo
        
        escrever(path, input)
        resultado = calcularSimulacao(path)
        enviarResultado(mensagem, resultado)
    
def mudarTaxa(mensagem):
    prazo = mensagem.text
    
    path = usersPath + str(mensagem.chat.id)
    input = ler(path)
    
    taxa = input['Taxa']

    if checarDigito(mensagem, taxa):
        output = ler(dirPath + r'\Taxas.json')
        output[prazo] = taxa

        escrever('Taxas.json', output)

        bot.send_message(mensagem.chat.id, "Taxa Registrada")

@bot.message_handler(commands=["Taxa"])
def registrarTaxa(mensagem):
    msg = bot.send_message(mensagem.chat.id, "Qual taxa deseja usar?")
    bot.register_next_step_handler(msg, registrarTaxaFinal)
    pass

def registrarTaxaFinal(mensagem):
    taxa = mensagem.text

    path = usersPath + str(mensagem.chat.id)
    input = ler(path)

    input['Taxa'] = taxa

    escrever(path, input)
    
    msg = bot.send_message(mensagem.chat.id, "Para qual prazo a taxa deve ser usada?")
    bot.register_next_step_handler(msg, mudarTaxa)
    pass

@bot.message_handler(commands=["Sair"])
def sair(mensagem):
    userID = mensagem.chat.id
    path = usersPath + str(userID)
    inputUser = ler(path)
    
    inputUser['Sessao'] = 0

    escrever(path, inputUser)

    bot.send_message(userID, "Até a próxima!")

@bot.message_handler(commands=["Lista"])
def listarUsuarios(mensagem):    
    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)
    resposta = ""
    
    for key in ledger.keys():
        resposta = resposta + key + '\n'

    print(resposta)

    bot.send_message(mensagem.chat.id, resposta)
    
@bot.message_handler(commands=["Codigo"])
def registrarCodigo(mensagem):    
    msg = bot.send_message(mensagem.chat.id, "Digite um código de cadastro de sua escolha")
    bot.register_next_step_handler(msg, registrarCodigoNext)

def registrarCodigoNext(mensagem):
    path = dirPath + r'\Seeds.json'
    seeds = ler(path)
    key = mensagem.text

    seeds[key] = 0

    escrever(path, seeds)

    resposta = """
    Código de cadastro registrado.

    Você pode passar o código para outro usuário e ele poderá se cadastrar usando o comando /Cadastrar
    """

    bot.send_message(mensagem.chat.id, resposta)

@bot.message_handler(commands=["Gerenciar"])
def gerenciar(mensagem):
    resposta = """
    Escolha uma das opções (Clique no item)
    
    /Lista Ver usuários existentes
    /Codigo Iniciar processo para cadastrar novo usuário
    """
    
    bot.send_message(mensagem.chat.id, resposta)

def verificar(mensagem):
    return True

def menu(mensagem):
    resposta = """
    Escolha uma das opções (Clique no item)
    /Simular Realizar Simulação
    /Sair Sair da sessão"""
    
    bot.send_message(mensagem.chat.id, resposta)

def menuAdmin(mensagem):
    resposta = """
    USUÁRIO ADMINISTRADOR

    Escolha uma das opções (Clique no item)
    /Simular Realizar Simulação
    /Taxa Registrar Taxa
    /Gerenciar Ver usuários existentes ou cadastrar novos
    /Sair Sair da sessão"""
    
    bot.send_message(mensagem.chat.id, resposta)


@bot.message_handler(func=verificar)
def respostaInicial(mensagem):
    path = usersPath + str(mensagem.chat.id)
    inputUser = ler(path)

    if int(inputUser['Sessao'] == 0):
        login(mensagem)
    else:
        checarAdmin(mensagem)


bot.polling()