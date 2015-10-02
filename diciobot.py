#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import telegram
import configparser
from lxml import html


class Diciobot():

    """() -> ()
    Classe Diciobot.
    """

    options = ["start", "help", "ajuda", "d", "definir", "s", "sinonimos",
               "r", "rimas", "ana", "anagramas", "c", "conjugar", "dia"]
    helpMessage = """As opções *disponíveis* são as _seguintes_:

/definir ou /d - Obter a *definição* de um _verbete_;
/sinonimos ou /s - Obter *sinônimos* de um _verbete_;
/rimas ou /r - Obter *rimas* de um _verbete_;
/anagramas ou /ana - Obter *anagramas* de um _verbete_;
/conjugar ou /c - *Conjugar* um _verbo_;
/dia - *Palavra do dia*."""

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
            for update in self.bot.getUpdates(offset=self.lastUpdate,
                                              timeout=10):
                chat_id = update.message.chat_id
                message = update.message.text
                message_id = update.message.message_id

                if message:
                    if "@diciobot" in message:
                        botid = "@diciobot"
                        message = message[:message.find(botid)]
                        message += message[message.find(botid) + len(botid):]

                    if(message.startswith('/')):
                        command, _, arguments = message.partition(' ')
                        command = command.lower()
                        if command[1:] in Diciobot.options:
                            noArgument = arguments == ''
                            text = "A utilização correta é "
                            text += command + " _verbete_."
                            if command in ['/start']:
                                self.bot.sendMessage(chat_id=chat_id,
                                                     text="Vamos *começar*?",
                                                     parse_mode="Markdown")
                                self.bot.sendMessage(chat_id=chat_id,
                                                     text=Diciobot.helpMessage,
                                                     parse_mode="Markdown")

                            elif command in ['/help', '/ajuda']:
                                self.bot.sendMessage(chat_id=chat_id,
                                                     text=Diciobot.helpMessage,
                                                     parse_mode="Markdown")

                            elif command in ['/d', '/definir']:
                                if noArgument:
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        reply_to_message_id=message_id)
                                else:
                                    text = self.definir(arguments)
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                            elif command in ['/s', '/sinonimos']:
                                if noArgument:
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        reply_to_message_id=message_id)
                                else:
                                    text = self.sinonimos(arguments)
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                            elif command in ['/r', '/rimas']:
                                if noArgument:
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        reply_to_message_id=message_id)
                                else:
                                    text = self.rimas(arguments)
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                            elif command in ['/ana', '/anagramas']:
                                if noArgument:
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        reply_to_message_id=message_id)
                                else:
                                    text = self.anagramas(arguments)
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                            elif command in ['/c', '/conjugar']:
                                if noArgument:
                                    text = text.replace("verbete", "verbo")
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        reply_to_message_id=message_id)
                                else:
                                    text = self.conjugar(arguments)
                                    self.bot.sendMessage(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                            elif command in ['/dia']:
                                text = self.palavraDoDia()
                                self.bot.sendMessage(
                                    chat_id=chat_id,
                                    text=text,
                                    parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_to_message_id=message_id)

                            elif command in ['/a', '/antonimos']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                            elif command in ['/e', '/exemplos']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                            elif command in ['/t', '/tudo']:
                                if noArgument:
                                    pass
                                else:
                                    pass

                    else:
                        text = "Você precisa executar um dos *comandos* "
                        text += "_disponíveis_."
                        self.bot.sendMessage(
                            chat_id=chat_id,
                            text=text,
                            parse_mode="Markdown")
                        self.bot.sendMessage(
                            chat_id=chat_id,
                            text=Diciobot.helpMessage,
                            parse_mode="Markdown")

                    self.lastUpdate = update.update_id + 1

    def tudo(self, verbete):
        # definicao = self.definir(verbete)
        # sinonimos = self.sinonimos(verbete)
        # rimas = self.rimas(verbete)
        # anagramas = self.anagramas(verbete)
        # conjugacoes = self.conjugar(verbete)
        pass

    def definir(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete
        naoDisponivel += "* _não tem definição ou significado disponíveis._"
        pagina, sugestao = self.buscar(verbete)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbete, sugestao)
        fonte = "\n\n*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        titulos_def = tree.xpath('//*[@class="tit-section"]/text()')
        titulo_def = ""
        for each in titulos_def:
            if 'Definição' in each:
                titulo_def = each.split(' ')
        if len(titulo_def) == 0:
            significado = ''
        else:
            significado = '*' + ' '.join(titulo_def[:-1])
            significado += '* _' + titulo_def[-1] + "_\n"
            definicao = tree.xpath('//*[@class="adicional"][1]//node()')
            for each in definicao:
                if type(each) == html.HtmlElement:
                    if each.tag == "br":
                        significado += "\n"
                else:
                    significado += each
            significado += "\n"
        titulo = tree.xpath('//*[@id="tit-significado"]/text()')
        if len(titulo) + len(significado) == 0:
            return naoDisponivel
        elif len(titulo) == 0:
            significado += "Significado: Não encontrado."
            return significado.replace("\n ", "\n") + fonte
        titulo = ''.join(tree.xpath('//*[@id="tit-significado"]/text()'))
        titulo = titulo.split(' ')
        titulo = '*' + ' '.join(titulo[:-1]) + '* _' + titulo[-1] + '_'
        elemento = tree.xpath('//*[@id="significado"]//node()')
        significado += titulo + "\n"
        for each in elemento:
            if type(each) == html.HtmlElement:
                if each.tag == "br":
                    significado += "\n"
            else:
                significado += each.replace("*", "\*")
        return significado.replace("\n ", "\n") + fonte

    def sinonimos(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete
        naoDisponivel += "* _não tem sinônimos disponíveis._"
        pagina, sugestao = self.buscar(verbete)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbete, sugestao)
        fonte = "\n\n*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        titulos = tree.xpath('//*[@class="tit-section"]/text()')
        sinonimos = ''
        for each in titulos:
            if 'Sinônimos' in each:
                sinonimos = each.split(' ')
        if len(sinonimos) == 0:
            return naoDisponivel + fonte
        sinonimos = '*' + ' '.join(sinonimos[:-1]) + '* _' + sinonimos[-1]
        sinonimos += "_\n"
        elemento = tree.xpath('//*[@class="adicional cols"]/span//node()')
        listaSinonimos = []
        for each in elemento:
            if type(each) != html.HtmlElement:
                listaSinonimos.append('_' + each + '_')
        if len(listaSinonimos) > 1:
            sinonimos += ', '.join(listaSinonimos[:-1]) + ' e '
        sinonimos += listaSinonimos[-1]
        return sinonimos + fonte

    def rimas(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete
        naoDisponivel += "* _não tem rimas disponíveis._"
        pagina, sugestao = self.buscar(verbete)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbete, sugestao)
        fonte = "\n\n*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        titulos = tree.xpath('//*[@class="tit-other"]/text()')
        rimas = ''
        for each in titulos:
            if 'Rimas' in each:
                rimas = each.split(' ')
        if len(rimas) == 0:
            return naoDisponivel + fonte
        rimas = '*' + ' '.join(rimas[:-1]) + '* _' + rimas[-1] + "_\n"
        elemento = tree.xpath('//*[@class="list col-4 small"][1]/li/text()')
        if len(elemento) > 1:
            rimas += '_' + ', '.join(elemento[:-1]) + '_ e '
        rimas += '_' + elemento[-1] + "_"
        return rimas + fonte

    def anagramas(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete
        naoDisponivel += "* _não tem anagramas disponíveis._"
        pagina, sugestao = self.buscar(verbete)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbete, sugestao)
        fonte = "\n\n*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        titulos = tree.xpath('//*[@class="tit-other"]/text()')
        anagramas = ''
        for each in titulos:
            if 'Anagramas' in each:
                anagramas = each.split(' ')
        if len(anagramas) == 0:
            return naoDisponivel + fonte
        anagramas = '*' + ' '.join(anagramas[:-1]) + '* _' + anagramas[-1]
        anagramas += "_\n"
        elemento = tree.xpath('//*[@class="list col-4 small"][2]/li/text()')
        if len(elemento) > 1:
            anagramas += '_' + ', '.join(elemento[:-1]) + '_ e '
        anagramas += '_' + elemento[-1] + "_"
        return anagramas + fonte

    def conjugar(self, verbo):
        naoDisponivel = "_O verbete_ *" + verbo
        naoDisponivel += "* _não tem conjugação disponível._"
        naoDisponivel += "\n_Tente um verbo no_ *infinitivo*."
        pagina, sugestao = self.buscar(verbo)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbo, sugestao, True)
        fonte = "*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        conjugacoes = tree.xpath('//*[@id="conjugacao"]//node()')
        if len(conjugacoes) == 0:
            return naoDisponivel + "\n\n" + fonte
        titulos = tree.xpath('//*[@class="tit-other"]/text()')
        for each in titulos:
            if 'Conjugação' in each:
                conjugacao = each.split(' ')
        conjugacao = '*' + ' '.join(conjugacao[:-1]) + '* _' + conjugacao[-1]
        conjugacao += "_\n"
        def_verbo = tree.xpath('//*[@id="conjugacao"]/p//node()')
        for each in def_verbo:
            if type(each) == html.HtmlElement:
                if each.tag == "br":
                    conjugacao += "\n"
            else:
                conjugacao += each.replace("*", "\*")
        conjugacao += "\n"
        modos_nome = tree.xpath('//*[@class="modo"]//text()')
        verb_wrapper = tree.xpath('//*[@class="verb-wrapper"]/ul')
        modos = []
        for each in verb_wrapper:
            modos.append(each.findall('li'))
        for i in range(len(modos)):
            conjugacao += "*" + modos_nome[i] + "*\n"
            for j in range(len(modos[i])):
                conjugacao += "*" + modos[i][j].find('div').text_content()
                conjugacao += "*\n"
                modos[i][j].find('div').drop_tree()
                for each in modos[i][j].xpath('.//node()'):
                    if type(each) == html.HtmlElement:
                        if each.tag == "br":
                            conjugacao += "\n"
                    else:
                        conjugacao += each.replace("*", "\*")
                conjugacao += "\n"
        return conjugacao.replace("\n ", "\n") + fonte

    def palavraDoDia(self):
        pagina = requests.get("http://www.dicio.com.br")
        tree = html.fromstring(pagina.text)
        doDia = tree.xpath('//*[@id="dia"]/a/text()')[0]
        definir = self.definir(doDia)
        doDia = "*Palavra do dia:* _" + doDia + "_\n\n"
        return doDia + definir

    def antonimos(self, verbete):
        pass

    def exemplos(self, verbete):
        pass

    def quatroZeroQuatro(self, verbete, sugestao, verbo=False):
        naoEncontrado = "_O verbete_ *" + verbete + "* _não foi encontrado._"
        if verbo:
            naoEncontrado = naoEncontrado.replace("verbete", "verbo")
        if len(sugestao) == 0:
            return naoEncontrado
        naoEncontrado += "\n\n_Você quis dizer_ *" + sugestao + "*?"
        return naoEncontrado

    def buscar(self, verbete):
        base_url = "http://www.dicio.com.br"
        search_url = "http://www.dicio.com.br/pesquisa.php?q=" + verbete
        busca = requests.get(search_url)
        tree = html.fromstring(busca.text)
        if "/pesquisa.php" in busca.url:
            # Retornou uma página de busca
            pagina = tree.xpath('//*[@class="found"]')
            if len(pagina) == 0:
                # Não encontrou resultados pra busca do verbete
                pagina = tree.xpath('//*[@id="enchant"]/a[1]')
                if len(pagina) == 0:
                    # Não tem nenhuma sugestao para o verbete nao encontrado
                    return requests.get(base_url + "/404"), ""

                # Tem sugestões para o verbete não encontrado
                sugestao = pagina[0].text
                return requests.get(base_url + "/404"), sugestao

            # Encontrou resultados pra busca do verbete
            pagina = tree.xpath('//*[@class="resultados"][1]/li/a[1]')
            for each in pagina:
                href = each.values()[0]
                sugestao = each.text
                if sugestao == verbete:
                    # Encontrou o verbete solicitado nos resultados
                    busca = requests.get(base_url + href)
                    return busca, ""

            # Não encontrou o verbete solicitado nos resultados
            return requests.get(base_url + "/404"), sugestao

        # Retornou diretamente a página do verbete
        return busca, ""


def main():

    diciobot = Diciobot()
    diciobot.startBot()

if __name__ == '__main__':
    main()
