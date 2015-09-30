#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import telegram
import configparser
from unicodedata import normalize
from lxml import html, etree

class DicioBot():
    options = ["start","help","ajuda","d","definir","s","sinonimos",\
               "r","rimas","ana","anagramas","c","conjugar"]
    helpMessage = """As opções *disponíveis* são as _seguintes_:

/definir ou /d - Obter a *definição* de um _verbete_;
/sinonimos ou /s - Obter *sinônimos* de um _verbete_;
/rimas ou /r - Obter *rimas* de um _verbete_;
/anagramas ou /ana - Obter *anagramas* de um _verbete_;
/conjugar ou /c - *Conjugar* um _verbo_.
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

                            elif command in ['/s','/sinonimos']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbete_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.obterSinonimos(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/r','/rimas']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbete_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.obterRimas(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/ana','/anagramas']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbete_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.obterAnagramas(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/c','/conjugar']:
                                if noArgument:
                                    self.bot.sendMessage(chat_id=chat_id, text="A utilização correta é " + command + " _verbo_.", parse_mode="Markdown", reply_to_message_id=message_id)
                                else:
                                    msg_text = self.conjugarVerbo(arguments)
                                    self.bot.sendMessage(chat_id=chat_id, text=msg_text, parse_mode="Markdown", disable_web_page_preview=True, reply_to_message_id=message_id)

                            elif command in ['/a','/antonimos']:
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
        pass

    def definirVerbete(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete + "* _não tem definição ou significado disponíveis._"
        pagina, url = self.obterPagina(verbete)
        fonte = "\n\n*Fonte:* " + url.replace("_", "\_")
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbete)
        titulos_def, titulo_def = arvore.xpath('//*[@class="tit-section"]/text()'), ""
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
            significado += "Significado: Não encontrado."
            return significado.replace("\n ","\n") + fonte
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
        return significado.replace("\n ","\n") + fonte

    def obterSinonimos(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete + "* _não tem sinônimos disponíveis._"
        pagina, url = self.obterPagina(verbete)
        fonte = "\n\n*Fonte:* " + url.replace("_", "\_")
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbete)
        titulos = arvore.xpath('//*[@class="tit-section"]/text()')
        sinonimos = ''
        for each in titulos:
            if 'Sinônimos' in each:
                sinonimos = each.split(' ')
        if len(sinonimos) == 0:
            return naoDisponivel + fonte
        sinonimos = '*' + ' '.join(sinonimos[:-1]) + '* _' + sinonimos[-1] + "_\n"
        elemento = arvore.xpath('//*[@class="adicional cols"]/span//node()')
        listaSinonimos = []
        for each in elemento:
            if type(each) != html.HtmlElement:
                listaSinonimos.append('_' + each + '_')
        if len(listaSinonimos) > 1:
            sinonimos += ', '.join(listaSinonimos[:-1]) + ' e '
        sinonimos += listaSinonimos[-1]
        return sinonimos + fonte

    def obterRimas(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete + "* _não tem rimas disponíveis._"
        pagina, url = self.obterPagina(verbete)
        fonte = "\n\n*Fonte:* " + url
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbete)
        titulos = arvore.xpath('//*[@class="tit-other"]/text()')
        titulo = ''
        for each in titulos:
            if 'Rimas' in each:
                titulo = each.split(' ')
        if len(titulo) == 0:
            return naoDisponivel + fonte
        titulo = '*' + ' '.join(titulo[:-1]) + '* _' + titulo[-1] + '_'
        rimas = titulo + "\n"
        elemento = arvore.xpath('//*[@class="list col-4 small"][1]/li/text()')
        if len(elemento) > 1:
            rimas += '_' + ', '.join(elemento[:-1]) + '_ e '
        rimas += '_' + elemento[-1] + "_"
        return rimas + fonte

    def obterAnagramas(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete + "* _não tem anagramas disponíveis._"
        pagina, url = self.obterPagina(verbete)
        fonte = "\n\n*Fonte:* " + url
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbete)
        titulos = arvore.xpath('//*[@class="tit-other"]/text()')
        titulo = ''
        for each in titulos:
            if 'Anagramas' in each:
                titulo = each.split(' ')
        if len(titulo) == 0:
            return naoDisponivel + fonte
        titulo = '*' + ' '.join(titulo[:-1]) + '* _' + titulo[-1] + '_'
        anagramas = titulo + "\n"
        elemento = arvore.xpath('//*[@class="list col-4 small"][2]/li/text()')
        if len(elemento) > 1:
            anagramas += '_' + ', '.join(elemento[:-1]) + '_ e '
        anagramas += '_' + elemento[-1] + "_"
        return anagramas + fonte

    def conjugarVerbo(self, verbo):
        naoDisponivel = "_O verbete_ *" + verbo + "* _não tem conjugação disponível._"
        naoDisponivel += "\n_Tente um verbo no_ *infinitivo*."
        pagina, url = self.obterPagina(verbo)
        fonte = "*Fonte:* " + url.replace("_", "\_")
        arvore = html.fromstring(pagina.text)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(arvore, verbo, True)
        conjugacoes = arvore.xpath('//*[@id="conjugacao"]//node()')
        if len(conjugacoes) == 0:
            return naoDisponivel + "\n\n" + fonte
        titulos = arvore.xpath('//*[@class="tit-other"]/text()')
        for each in titulos:
            if 'Conjugação' in each:
                conjugacao = each.split(' ')
        conjugacao = '*' + ' '.join(conjugacao[:-1]) + '* _' + conjugacao[-1] + "_\n"
        def_verbo = arvore.xpath('//*[@id="conjugacao"]/p//node()')
        for each in def_verbo:
            if type(each) == html.HtmlElement:
                if each.tag == "br":
                    conjugacao += "\n"
            else:
                conjugacao += each.replace("*", "\*")
        conjugacao += "\n"
        modos_nome = arvore.xpath('//*[@class="modo"]//text()')
        verb_wrapper = arvore.xpath('//*[@class="verb-wrapper"]/ul')
        modos = []
        for each in verb_wrapper:
            modos.append(each.findall('li'))
        for i in range(len(modos)):
            conjugacao += "*" + modos_nome[i] + "*\n"
            for j in range(len(modos[i])):
                conjugacao += "*" + modos[i][j].find('div').text_content() + "*\n"
                modos[i][j].find('div').drop_tree()
                for each in modos[i][j].xpath('.//node()'):
                    if type(each) == html.HtmlElement:
                        if each.tag == "br":
                            conjugacao += "\n"
                    else:
                        conjugacao += each.replace("*","\*")
                conjugacao += "\n"
        return conjugacao.replace("\n ","\n") + fonte

    def obterAntonimos(self, verbete):
        pass

    def obterExemplos(self, verbete):
        pass

    def quatroZeroQuatro(self, arvore, verbete, verbo=False):
        naoEncontrado = "_O verbete_ *" + verbete + "* _não foi encontrado._"
        if verbo:
            naoEncontrado = naoEncontrado.replace("verbete", "verbo")
        sugestao = arvore.xpath('//*[@id="enchant"]/a[1]/text()')
        if len(sugestao) == 0:
            return naoEncontrado
        sugestao = "\n\n_Você quis dizer_ *" + sugestao[0] + "*?"
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
