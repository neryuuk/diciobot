#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import telegram
import configparser
from unicodedata import normalize
from lxml import html

class DicioBot():
    options = ["start", "help", "ajuda", "d", "definir", "r", "rimas"]
    helpMessage = """As opções *disponíveis* são as _seguintes_:

/definir (/d) - Obter a *definição* de um _verbete_
/rimas, (/r) - Obter *rimas* de um _verbete_
    """
    default_url = 'http://www.dicio.com.br/VERBETE/'

    def __init__(self):
        """() -> ()
        Inicializa o bot.
        """
        self.config = configparser.ConfigParser()
        self.config.read("diciobot.ini")
        self.token = self.config.get("Token", "token")
        self.bot = telegram.Bot(self.token)

        try:
            self.lastUpdate = self.bot.getUpdates()[-1].update_id
        except IndexError:
            self.lastUpdate = None

    def startBot(self):
        while True:
            for update in self.bot.getUpdates(offset=self.lastUpdate, timeout=10):
                chat_id = update.message.chat_id
                message = update.message.text
                message_id = update.message.message_id

                if message:
                    if "@diciobot" in message:
                        botid = "@diciobot"
                        message = message[:message.find(botid)] + message[message.find(botid) + len(botid):]

                    if(message.startswith('/')):
                        command, _, arguments = message.partition(' ')
                        if command[1:] in DicioBot.options:
                            noArgument = arguments == ''
                            if command == '/start':
                                self.bot.sendMessage(chat_id=chat_id, text="Vamos *começar*?", parse_mode="Markdown")
                                self.bot.sendMessage(chat_id=chat_id, text=DicioBot.helpMessage, parse_mode="Markdown")

                            elif command in ['/help','/ajuda']:
                                self.bot.sendMessage(chat_id=chat_id, text=DicioBot.helpMessage, parse_mode="Markdown")

                            elif command in ['/d','/definir']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbete_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.definirVerbete(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/r','/rimas']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbete_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.obterRimas(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/c','/conjugar']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbo_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.conjugarVerbo(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/s','/sinonimos']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                            elif command in ['/a','/antonimos']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                            elif command in ['/ana','/anagramas']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                            elif command in ['/e','/exemplos']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                            elif command in ['/t','/tudo']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                    else:
                        self.bot.sendMessage(chat_id=chat_id, text="Você precisa executar um dos *comandos* _disponíveis_.", parse_mode="Markdown")
                        self.bot.sendMessage(chat_id=chat_id, text=DicioBot.helpMessage, parse_mode="Markdown")

                    self.lastUpdate = update.update_id + 1

    def obterTudo(self, verbete):
        tudo = verbete
        return tudo

    def definirVerbete(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete + "* _não tem definição ou significado disponíveis._"
        pagina, url = self.obterPagina(verbete)
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbete)
        titulos_def = arvore.xpath('//*[@class="tit-section"]/text()')
        for each in titulos_def:
            if 'Definição' in each:
                titulo_def = each.split(' ')
        if len(titulo_def) == 0:
            significado = ''
        else:
            significado = '*' + ' '.join(titulo_def[:-1]) + '* _' + titulo_def[-1] + "_\n"
            definicao = arvore.xpath('//*[@class="adicional"][1]//node()')
            for each in definicao:
                if type(each) == html.HtmlElement:
                    if each.tag == "br":
                        significado += "\n"
                else:
                    significado += each
            significado += "\n"
        titulo = arvore.xpath('//*[@id="tit-significado"]/text()')
        if len(titulo) + len(significado) == 0:
            return naoDisponivel
        elif len(titulo) == 0:
            significado += "Significado: Não encontrado.\n"
            significado += "\n*Fonte:* " + url.replace("_", "\_")
            return significado.replace("\n ","\n")
        titulo = ''.join(arvore.xpath('//*[@id="tit-significado"]/text()')).split(' ')
        titulo = '*' + ' '.join(titulo[:-1]) + '* _' + titulo[-1] + '_'
        elemento = arvore.xpath('//*[@id="significado"]//node()')
        significado += titulo + "\n"
        for each in elemento:
            if type(each) == html.HtmlElement:
                if each.tag == "br":
                    significado += "\n"
            else:
                significado += each.replace("*", "\*")
        significado += "\n\n*Fonte:* " + url.replace("_", "\_")
        return significado.replace("\n ","\n")

    def obterRimas(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete + "* _não tem rimas disponíveis._"
        pagina, url = self.obterPagina(verbete)
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbete)
        titulos = arvore.xpath('//*[@class="tit-other"]/text()')
        titulo = ''
        for each in titulos:
            if 'Rimas' in each:
                titulo = each.split(' ')
        if len(titulo) == 0:
            return naoDisponivel
        titulo = '*' + ' '.join(titulo[:-1]) + '* _' + titulo[-1] + '_'
        rimas = titulo + "\n"
        elemento = arvore.xpath('//*[@class="list col-4 small"][1]/li/text()')
        if len(elemento) > 1:
            rimas += '_' + ', '.join(elemento[:-1]) + '_ e '
        rimas += '_' + elemento[-1] + "_\n"
        rimas += "\n*Fonte:* " + url
        return rimas

    def conjugarVerbo(self, verbo):
        naoDisponivel = "_O verbete_ *" + verbo + "* _não tem conjugação disponível._"
        pagina, url = self.obterPagina(verbo)
        arvore = html.fromstring(pagina.text)
        titulos = arvore.xpath('//*[@class="tit-other"]/text()')
        titulo = ''
        for each in titulos:
            if 'Conjugação' in each:
                titulo = each.split(' ')
        if len(titulo) == 0:
            return naoDisponivel
        titulo = '*' + ' '.join(titulo[:-1]) + '* _' + titulo[-1] + '_'
        conjugacao = titulo + "\n"
        conjugacao += "\n*Fonte:* " + url
        elemento = arvore.xpath('//*[@id="conjugacao"]/text()')
        return conjugacao

    def obterSinonimos(self, verbete):
        sinonimos = verbete
        return sinonimos

    def obterAntonimos(self, verbete):
        antonimos = verbete
        return antonimos

    def obterAnagramas(self, verbete):
        anagramas = verbete
        return anagramas

    def obterExemplos(self, verbete):
        exemplos = verbete
        return exemplos

    def quatroZeroQuatro(self, arvore, verbete, verbo=False):
        naoEncontrado = "_O verbete_ *" + verbete + "* _não foi encontrado._"
        if verbo:
            naoEncontrado = naoEncontrado.replace("verbete", "verbo")
        sugestao = arvore.xpath('//*[@id="enchant"]/a[1]/text()')
        if len(sugestao) == 0:
            return naoEncontrado
        sugestao = "\n_Você quis dizer_ *" + sugestao[0] + "*?"
        return naoEncontrado + sugestao

    def obterPagina(self, verbete):
        # Receita obtida em http://wiki.python.org.br/RemovedorDeAcentos
        sem_acento = normalize('NFKD', verbete).encode('ASCII','ignore').decode('ASCII').lower()
        url = DicioBot.default_url.replace("VERBETE", sem_acento)
        pagina = requests.get(url)
        return pagina, url

def main():
    diciobot = DicioBot()
    diciobot.startBot()

if __name__ == '__main__':
    main()
