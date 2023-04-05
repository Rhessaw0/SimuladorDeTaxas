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
    login = mensagem.text

    msg = bot.send_message(mensagem.chat.id, "Qual é a sua senha?")
    bot.register_next_step_handler(msg, loginFinal, login)

def loginFinal(mensagem, login):
    senha = mensagem.text

    checarLogin(mensagem, login, senha)

@bot.message_handler(commands=["Sim"])
def novoUsuarioSim(mensagem):
    msg = bot.send_message(mensagem.chat.id, "Digite o código de cadastro.")
    bot.register_next_step_handler(msg, novoUsuarioSimStep1)

def novoUsuarioSimStep1(mensagem):
    codigo = mensagem.text
    
    path = dirPath + r'\Seeds.json'
    seeds = ler(path)

    if codigo in seeds:
        if seeds[codigo] == 0:
            msg = bot.send_message(mensagem.chat.id, "Digite o login a ser usado para o novo usuário.")

            bot.register_next_step_handler(msg, novoUsuarioSimStep2, codigo)
        elif seeds[codigo] == 1:
            msg = bot.send_message(mensagem.chat.id, "O código está sendo usado.")
            if validarSessao(mensagem, 1): checarAdmin(mensagem)
        elif seeds[codigo] == 2:
            msg = bot.send_message(mensagem.chat.id, "O código já foi usado.")
            if validarSessao(mensagem, 1): checarAdmin(mensagem)
    else:
        msg = bot.send_message(mensagem.chat.id, "O código não existe.")
        if validarSessao(mensagem, 1): checarAdmin(mensagem)

def novoUsuarioSimStep2(mensagem, codigo):
    login = mensagem.text
    msg = bot.send_message(mensagem.chat.id, "Digite a senha a ser usada para o novo senha.")
    bot.register_next_step_handler(msg, novoUsuarioFinal, codigo, login)

def novoUsuarioFinal(mensagem, codigo, login): 
    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)

    path = dirPath + r'\Seeds.json'
    seeds = ler(path)
    
    senha = mensagem.text

    ledger[login] = senha

    seeds.pop(codigo)

    bot.send_message(mensagem.chat.id, "Usuário Cadastrado!")
    pass
    
@bot.message_handler(commands=["Nao"])
def novoUsuarioNao(mensagem):
    bot.send_message(mensagem.chat.id, "Entendido.")

@bot.message_handler(commands=["Cadastrar"])
def novoUsuario(mensagem):
    resposta = """
    Deseja cadastrar um novo usuário?
    
    Escolha uma das opções (Clique no item)
    /Sim Continuar o cadastro
    /Nao Cancelar o cadastro"""
    
    bot.send_message(mensagem.chat.id, resposta)
    pass

def checarLogin(mensagem, usuario, senha):
    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)

    try:
        if(ledger[usuario] == senha):
            checarAdmin(mensagem)
    except:
        resposta = """
        Seu usuário ou senha estão incorretos. 
        Você também pode não ser um usuário registrado. Neste caso, o comando /Cadastrar pode ser usado caso possua um código de cadastro.
        """
        bot.send_message(mensagem.chat.id, resposta)
        
def checarAdmin(mensagem):
    userID = mensagem.chat.id
    path = usersPath + str(userID)
    inputUser = ler(path)
            
    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)
    
    if ledger['Admin'] == str(userID):
        if inputUser['Sessao'] == 0: bot.send_message(userID, "Bem Vindo, Administrador!")
        
        inputUser['Sessao'] = 2
        
        escrever(path, inputUser)
        
        menuAdmin(mensagem)
    else:
        if inputUser['Sessao'] == 0: bot.send_message(userID, "Bem Vindo!")
        
        inputUser['Sessao'] = 1
        
        escrever(path, inputUser)
        
        menu(mensagem)

def checarArquivo(file):
    path = usersPath + str(file)
    try:
        ler(path)
    except:
        template = {
        'Sessao': 0
        }

        escrever(path, template)
    finally:
        pass

def checarDigito(mensagem, valor):
    if valor.isdigit():
        return True
    else:
        bot.send_message(mensagem.chat.id, "Isso não é um número. Por favor repita o processo, confirmando que apenas números foram enviados")

def validarSessao(mensagem, requerimento):
    userID = mensagem.chat.id
    path = usersPath + str(userID)
    inputUser = ler(path)

    if inputUser['Sessao'] >= requerimento:
        return True
    else:
        bot.send_message(mensagem.chat.id, "O usuário não possui permissão para usar este comando.")
        return False

def imprimirSimulacao(nomes, valores):
    resposta = ["SIMULAÇÃO REDECRED\n"]

    for n, v in zip (nomes, valores):
            linha = (f"{n : <}{':' : ^1}{'' : ^2}{v : >}")
            resposta.append(linha)
    
    respostaFinal = '\n'.join(resposta)
    print(respostaFinal)
    return respostaFinal

def calcularSimulacao(modo, valor, prazo):
    inputTaxa = ler(dirPath + r"\Taxas.json")

    r_taxa = int(inputTaxa[str(prazo)])
    
    if(modo == 'Quantia'):
        taxaQ = (100 + r_taxa) / 100
        total = valor * taxaQ
        parcela = total / prazo
    elif(modo == 'Limite'):
        taxaL = r_taxa / 100
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
    if not validarSessao(mensagem, 1): return
    
    modo = 'Quantia'

    msg = bot.send_message(mensagem.chat.id, "Qual é o valor?")
    bot.register_next_step_handler(msg, simularValor, modo) 
    pass

@bot.message_handler(commands=["Limite"])
def simularLimite(mensagem):
    if not validarSessao(mensagem, 1): return

    modo = 'Limite'
    
    msg = bot.send_message(mensagem.chat.id, "Qual é o valor?")
    bot.register_next_step_handler(msg, simularValor, modo) 
    pass

@bot.message_handler(commands=["Simular"])
def simular(mensagem):
    if not validarSessao(mensagem, 1): return

    text = """
    Deseja simular por Quantia ou Limite?

    /Quantia Aplicar juros em cima do valor
    /Limite Aplicar abatimento no limite
    """
    bot.send_message(mensagem.chat.id, text)
    pass

def simularValor(mensagem, modo):
    valor = mensagem.text
    if checarDigito(mensagem, valor): 
        msg = bot.send_message(mensagem.chat.id, "Qual é o Prazo?")
        bot.register_next_step_handler(msg, simularPrazo, modo, valor)

def simularPrazo(mensagem, modo, valor):
    prazo = mensagem.text
    if checarDigito(mensagem, prazo):
        resultado = calcularSimulacao(modo, int(valor), int(prazo))
        enviarResultado(mensagem, resultado)
    
    respostaInicial(mensagem)
    
def mudarTaxa(mensagem, taxa):
    prazo = mensagem.text
    
    output = ler(dirPath + r'\Taxas.json')
    output[prazo] = taxa

    
    if checarDigito(mensagem, taxa):
        escrever(dirPath + r'\Taxas.json', output)

        bot.send_message(mensagem.chat.id, "Taxa Registrada")

    respostaInicial(mensagem)

@bot.message_handler(commands=["VerTaxa"])
def mostrarTaxas(mensagem):
    output = ler(dirPath + r'\Taxas.json')

    resposta = ""
    
    for key in output:
        resposta = resposta + key + ": " + output[key] + '\n'

    output = "As taxas atuais são: \n" + resposta

    bot.send_message(mensagem.chat.id, output)

@bot.message_handler(commands=["NovaTaxa"])
def registrarTaxa(mensagem):
    if not validarSessao(mensagem, 2): return

    msg = bot.send_message(mensagem.chat.id, "Qual taxa deseja usar?")
    bot.register_next_step_handler(msg, registrarTaxaFinal)
    pass

def registrarTaxaFinal(mensagem):
    taxa = mensagem.text

    msg = bot.send_message(mensagem.chat.id, "Para qual prazo a taxa deve ser usada?")
    bot.register_next_step_handler(msg, mudarTaxa, taxa)
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
    if not validarSessao(mensagem, 2): return

    pathLedger = dirPath + r'\Ledger.json'
    ledger = ler(pathLedger)
    resposta = ""
    
    for key in ledger.keys():
        resposta = resposta + key + '\n'

    print(resposta)

    bot.send_message(mensagem.chat.id, resposta)

    respostaInicial(mensagem)
    
@bot.message_handler(commands=["Codigo"])
def registrarCodigo(mensagem):
    if not validarSessao(mensagem, 2): return
    
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
    
    respostaInicial(mensagem)

@bot.message_handler(commands=["Gerenciar"])
def gerenciar(mensagem):
    if not validarSessao(mensagem, 2): return

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
    /NovaTaxa Registrar Taxa
    /VerTaxa Ver taxas atuais
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