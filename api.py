from flask import Flask, request, jsonify
import numpy as np
import twitter
from textblob import TextBlob

api_key = "your Twitter api key"
api_secret_key = "Your Twitter api secret key"

access_token = "Your acess token"
access_token_secret = "Your acess token secret"

api = twitter.Api(consumer_key=api_key,
                      consumer_secret=api_secret_key,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)
api.VerifyCredentials()
data = []
app = Flask(__name__)

@app.route('/')
def principalPage():
    return (jsonify({'Help': "Por favor, siga as instrucoes recomendadas e todos os dados a serem inseridos no formato Text - 'text' : 'conteudo'", '1)': "Caso queira pesquisar um banco de dados especifico, insira a word(GET) a ser pesquisada no seguinte formato: 'localhost:5000/pesquisa/str/value' onde 'str' sera a palavra que deve ser pesquisada e 'value' a quantidade de frases a ser buscada em tweets (pode ir de 0 a 100).",
            '2)' : "Caso queira verificar todas as frases atualmente no banco de dados, utilize o caminho 'localhost:5000/databank",
            '3)' : "Caso queira fazer uma correcao automatica das frases para melhor aproximacao do algoritmo, acesse por(GET): 'localhost:5000/atualize' (E um pouco demorado).",
            '4)' : "Caso queira adicionar algo do banco de dados, utilize o caminho 'localhost:5000/data com o metodo POST",
            '5)' : "Caso queira modificar/remover algo do banco de dados, utilize o caminho 'localhost:5000/data/index' onde 'index' sera a posicao a ser alterada/removida com os metodos PUT ou DELETE",
            '6)' : "Caso queira fazer uma analise sobre o banco de dados com um simples algoritmo de processamento de linguagem natural pra verificar se os tweets relacionados a palavra buscada criticam ou apoiam o tema sobre o que estao falando, acesse por : 'localhost:5000/analise'",
            '7)' : "Caso queira limpar o banco de dados, utilize: 'localhost:5000/databank/zero'"}))
@app.route('/pesquisa/<string:str>/<int:value>')
def search(str, value):
    list = api.GetSearch(geocode=None, since_id=None, term=str, lang='en', count=value, result_type='recent',
                         return_json=True)
    tweets_list = []
    for index in range(value):
        tweets_list.append(list['statuses'][index]['text'])

    for i in range(len(tweets_list)):
        dictaux = "'text' : '" + tweets_list[i] +"'"
        dictaux = dictaux.replace("“", "''")
        dictaux = dictaux.replace("”", "''")
        dictaux = dictaux.replace("’", "'")
        dictaux = dictaux.replace("…", "...")
        dictaux = dictaux.replace("\n", "")
        dictaux = dictaux.replace("\"", "''")
        data.append(dictaux)
    return ("O banco de dados sobre a palavra pesquisada em posts no Twitter foi criado.")
@app.route('/databank')
def databank():
    if len(data) > 0 :
        return(jsonify(data))
    else:
        return("Desculpe! O banco de dados está vazio.")

@app.route('/atualize')
def atualize():
    if(len(data) > 0):
        for i in range(len(data)):
            str_b = TextBlob(data[i])
            str_b = str(str_b.correct())
            data[i] = str_b
            print(data[i])
        return ("A atualização foi concluída.")
    else:
        return("O banco de dados está vazio! Primeiramente preencha-o.")

@app.route('/data', methods=["POST"])
def add():
    dados = str(request.data)
    dados = dados.replace("b\"", "")
    dados = dados.replace("\"", "")
    data.append(dados)
    return ("O dado foi adicionado corretamente.")

@app.route('/data/<int:value>', methods=['PUT', 'DELETE'])
def modif(value):
    if request.method == 'PUT':
        try:
            dados = str(request.data)
            dados = dados.replace("b\"", "")
            dados = dados.replace("\"", "")
            data[value] = dados
            return ("A posição no banco foi modificada com sucesso!")
        except IndexError:
            return ("Erro! A posição no banco de dados não foi encontrada.")
    else:
        try:
            data.pop(value)
            return ("A posição no banco de dados foi removida com sucesso!")
        except IndexError:
            return ("Erro! A posição no banco de dados não encontrada.")

@app.route('/analise')
def analise():
    scores = []
    analysis = None
    for i in range(len(data)):
        analysis = TextBlob(data[i])
        scores.append(analysis.sentiment.polarity)
    result = np.mean(scores)
    if result >= 0.5:
        return ("A avialiação dos tweets sobre o assunto afirma que apoiam em maior parte o tema debatido.")
    elif result > 0 and result < 0.5:
        return ("A avialiação dos tweets sobre o assunto afirma que apoiam levemente o tema debatido.")
    elif result == 0:
        return ("A avialiação dos tweets sobre o assunto afirma que nem apoiam e nem desapoiam. É equilibrado.")
    elif result > -0.5 and result < 0:
        return ("A avialiação dos tweets sobre o assunto afirma que desapoiam levemente o tema debatido.")
    else:
        return ("A avialiação dos tweets sobre o assunto afirma que desapoiam em maior parte o tema debatido.")

@app.route('/databank/zero')
def databank_zero():
    data.clear()
    return ("O banco de dados foi limpo.")

if __name__ == '__main__':
    app.run(debug=True)


