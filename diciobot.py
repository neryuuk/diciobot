#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import telegram
import cloudant
import json
from lxml import html


class Diciobot():

    """() -> ()
    Classe Diciobot.
    """

    simple_opt = ["start", "help", "ajuda", "dia"]
    options = ["d", "definir", "s", "sinonimos", "a", "antonimos",
               "r", "rimas", "ana", "anagramas", "e", "exemplos",
               "c", "conjugar", "t", "tudo"]
    dica = "*Dica*: Quando estiver falando *diretamente* com o bot, "
    dica += "você pode mandar diversas palavras separadas por "
    dica += "*vírgula* para obter suas definições. "
    dica += "(Sem precisar do comando /definir)"
    helpMessage = """As opções *disponíveis* são as _seguintes_:

/definir ou /d - *definição* de um _verbete_;
/sinonimos ou /s - *sinônimos* de um _verbete_;
/antonimos ou /a - *antônimos* de um _verbete_;
/exemplos ou /e - *exemplos* de utilização de um _verbete_;
/conjugar ou /c - *conjugar* um _verbo_;
/rimas ou /r - *rimas* de um _verbete_;
/anagramas ou /ana - *anagramas* de um _verbete_;
/tudo ou /t - *todas* as opções *disponíveis* de um _verbete_;
/dia - *Palavra do dia*."""

    def __init__(self):
        """() -> ()
        Inicializa o bot.
        """
        with open('diciobot.json') as config_file:
            self.config = json.load(config_file)
        self.token = self.config["Telegram"]["token"]
        self.bot = telegram.Bot(self.token)
        self.botid = self.config["Telegram"]["bot_id"]
        # self.account = self.config["Database"]["account"]
        # self.api_key = self.config["Database"]["api_key"]
        # self.api_pass = self.config["Database"]["api_pass"]
        # self.name = self.config["Database"]["name"]
        # self.stats = StatsLog(self.account, self.api_key, self.api_pass)
        # self.diciobot_log = self.stats.getDatabase(self.name)

        try:
            self.lastUpdate = self.bot.getUpdates(limit=1)[0].update_id
        except IndexError:
            self.lastUpdate = None

    def startBot(self):
        while True:
            for update in self.bot.getUpdates(
                    offset=self.lastUpdate,
                    timeout=5):
                chat_id = update.message.chat_id
                message = update.message.text.lower()
                message_id = update.message.message_id
                first_name = update.message.from_user.first_name
                info = self.getInfo(update)

                if message:
                    if self.botid in message:
                        message = message.replace(self.botid, "").strip()

                    if(message.startswith('/')):
                        command, _, arguments = message.partition(' ')
                        command = command[1:]
                        noArgument = arguments == ''
                        if command in Diciobot.options + Diciobot.simple_opt:
                            info["command"] = command
                            info["word"] = arguments
                            simple = command not in Diciobot.simple_opt
                            if noArgument and simple:
                                text = "Desculpe, _" + first_name
                                text += "_, mas a utilização correta é /"
                                text += command + " _verbete_."
                                self.send(
                                    chat_id=chat_id,
                                    text=text,
                                    parse_mode="Markdown",
                                    reply_to_message_id=message_id)
                            else:
                                if command in ['start', 'help', 'ajuda']:
                                    if command in ["start"]:
                                        start = "Vamos *começar*, _"
                                        start += first_name + "_?"
                                        self.send(
                                            chat_id=chat_id,
                                            text=start,
                                            parse_mode="Markdown")
                                    self.send(
                                        chat_id=chat_id,
                                        text=Diciobot.helpMessage,
                                        parse_mode="Markdown")
                                    if update.message.chat.type == "private":
                                        self.send(
                                            chat_id=chat_id,
                                            text=Diciobot.dica,
                                            parse_mode="Markdown")

                                elif command in ['d', 'definir']:
                                    text = self.definir(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['s', 'sinonimos']:
                                    text = self.sinonimos(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['a', 'antonimos']:
                                    text = self.antonimos(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['e', 'exemplos']:
                                    text = self.exemplos(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['c', 'conjugar']:
                                    text = self.conjugar(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['r', 'rimas']:
                                    text = self.rimas(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['ana', 'anagramas']:
                                    text = self.anagramas(arguments)
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                elif command in ['t', 'tudo']:
                                    tudo = self.tudo(arguments)
                                    for each in tudo:
                                        self.send(
                                            chat_id=chat_id,
                                            text=each,
                                            parse_mode="Markdown",
                                            disable_web_page_preview=True,
                                            reply_to_message_id=message_id)

                                elif command in ['dia']:
                                    text, info["word"] = self.palavraDoDia()
                                    self.send(
                                        chat_id=chat_id,
                                        text=text,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True,
                                        reply_to_message_id=message_id)

                                # response = self.stats.log(info)
                                # print(info, response.ok)
                                print(info)

                    # elif update.message.chat.type == "private":
                    else:
                        message = message.split(",")
                        info["command"] = "d_quick"
                        for msg in message:
                            if len(msg.strip()) != 0:
                                info["word"] = msg.strip()
                                text = self.definir(msg.strip())
                                self.send(
                                    chat_id=chat_id,
                                    text=text,
                                    parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_to_message_id=message_id)

                                # response = self.stats.log(info)
                                # print(info, response.ok)
                                print(info)

                    self.lastUpdate = update.update_id + 1

    def send(self, **kwargs):
        try:
            self.bot.sendMessage(**kwargs)
        except telegram.error.TelegramError:
            pass

    def getInfo(self, update):
        chat_type = update.message.chat.type
        info = {}
        info["update_id"] = update.update_id
        info["message_id"] = update.message.message_id
        info["date"] = str(update.message.date)
        info["chat_type"] = chat_type

        if chat_type != "channel":
            info["user_id"] = update.message.from_user.id
            if chat_type == "group":
                info["group_id"] = update.message.chat.id
        else:
            info["channel_id"] = update.message.chat.id

        return info

    def tudo(self, verbete):
        tudo = []
        tudo.append(self.definir(verbete))
        if "_não foi encontrado._" in tudo[0]:
            return tudo
        tudo.append(self.sinonimos(verbete))
        tudo.append(self.antonimos(verbete))
        tudo.append(self.exemplos(verbete))
        tudo.append(self.conjugar(verbete))
        tudo.append(self.rimas(verbete))
        tudo.append(self.anagramas(verbete))
        remover = []
        for i in range(len(tudo)):
            if "* _não tem" in tudo[i]:
                remover.insert(0, i)
        for each in remover:
            tudo.pop(each)
        return tudo

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
        titulos = tree.xpath('//*[@id="tit-sinonimos"]/text()')
        sinonimos = ''
        for each in titulos:
            if 'Sinônimos' in each:
                sinonimos = each.split(' ')
        if len(sinonimos) == 0:
            return naoDisponivel + fonte
        sinonimos = '*' + ' '.join(sinonimos[:-1]) + '* _' + sinonimos[-1]
        sinonimos += "_\n"
        listaSinonimos = []
        elem = tree.xpath('//*[@class="adicional sinonimos"][1]//a//node()')
        if len(elem) == 0:
            elem = tree.xpath('//*[@class="adicional"][1]//a//node()')
        for each in elem:
            listaSinonimos.append('_' + each + '_')
        if len(listaSinonimos) > 1:
            sinonimos += ', '.join(listaSinonimos[:-1]) + ' e '
        sinonimos += listaSinonimos[-1]
        return sinonimos + fonte

    def antonimos(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete
        naoDisponivel += "* _não tem antônimos disponíveis._"
        pagina, sugestao = self.buscar(verbete)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbete, sugestao)
        fonte = "\n\n*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        titulos = tree.xpath('//*[@id="tit-antonimos"]/text()')
        antonimos = ''
        for each in titulos:
            if 'Antônimos' in each:
                antonimos = each.split(' ')
        if len(antonimos) == 0:
            return naoDisponivel + fonte
        antonimos = '*' + ' '.join(antonimos[:-1]) + '* _' + antonimos[-1]
        antonimos += "_\n"
        listaAntonimos = []
        elem = tree.xpath('//*[@class="adicional sinonimos"][2]//a//node()')
        if len(elem) == 0:
            elem = tree.xpath('//*[@class="adicional"][2]//a//node()')
        for each in elem:
            listaAntonimos.append('_' + each + '_')
        if len(listaAntonimos) > 1:
            antonimos += ', '.join(listaAntonimos[:-1]) + ' e '
        antonimos += listaAntonimos[-1]
        return antonimos + fonte

    def exemplos(self, verbete):
        naoDisponivel = "_O verbete_ *" + verbete
        naoDisponivel += "* _não tem frases ou exemplos disponíveis._"
        pagina, sugestao = self.buscar(verbete)
        if pagina.status_code == 404:
            return self.quatroZeroQuatro(verbete, sugestao)
        fonte = "*Fonte:* " + pagina.url.replace("_", "\_")
        tree = html.fromstring(pagina.text)
        titulo_frases = tree.xpath('//*[@class="tit-frases"]/text()')
        frases = ''
        xpath = '//*[@class="frases"][1]/node()'
        for each in titulo_frases:
            if 'Frase' in each:
                frases = each.split(' ')
        if len(frases) != 0:
            frases = '*' + ' '.join(frases[:-1]) + '* _' + frases[-1] + "_:\n"
            elemento = tree.xpath(xpath)
            xpath = '//*[@class="frases"][2]/node()'
            elemento = elemento[1:]
            for cada in elemento:
                elem = cada.xpath('./span/node()')
                for each in elem:
                    if type(each) == html.HtmlElement:
                        if each.tag == 'strong':
                            frases += '*' + each.text + '*'
                        elif each.tag == 'em':
                            frases += "\n_" + each.text + "_\n"
                    else:
                        frases += each
                frases += "\n"

        titulo_exemplos = tree.xpath('//*[@class="tit-exemplo"]/text()')
        exemplos = ''
        for each in titulo_exemplos:
            if 'Exemplo' in each:
                exemplos = each.split(' ')
        if len(exemplos) != 0:
            exemplos = '*' + ' '.join(exemplos[:-1]) + '* _' + exemplos[-1]
            exemplos += "_:\n"
            elemento = tree.xpath(xpath)
            for cada in elemento:
                elem = cada.xpath('./node()')
                for each in elem:
                    if type(each) == html.HtmlElement:
                        if each.tag == 'strong':
                            exemplos += '*' + each.text + '*'
                        elif each.tag == 'em':
                            exemplos += "\n_" + each.text + "_\n"
                    else:
                        exemplos += each
                exemplos += "\n"

        if len(frases + exemplos) == 0:
            return naoDisponivel + "\n\n" + fonte

        return (frases + exemplos + fonte).replace("\n ", "\n")

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

    def palavraDoDia(self):
        pagina = requests.get("http://www.dicio.com.br")
        tree = html.fromstring(pagina.text)
        doDia = tree.xpath('//*[@id="dia"]/a/text()')[0]
        definir = "*Palavra do dia:* _" + doDia + "_\n\n"
        definir += self.definir(doDia)
        return definir, doDia

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
        try:
            busca = requests.get(search_url)
        except requests.exceptions.TooManyRedirects:
            pass
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


class StatsLog():

    def __init__(self, account, api_key, api_pass):
        """
        Initializes the DB client and logs into the database,
        returning the login status code.

        :param account: account user string
        :param api_key: api key string
        :param api_pass: api password string
        """
        self.account = cloudant.Account(account)
        self.login = self.account.login(api_key, api_pass)

    def getDatabase(self, name):
        """(String) -> (Response Object)
        Instantiate the database and returns the reponse object.

        :param name: A string containing the database name.
        :returns: Response object
        """
        self.db = self.account.database(name)
        return self.db.get()

    def log(self, info):
        """(Dictionary) -> (Response Object)
        Tries (up to 3 times) to make a post request
        containing the log info

        :param info: A dictionary object.
        :returns: Response object
        """
        ok = False
        attempts = 0
        while not ok and attempts < 3:
            response = self.db.post(params=info)
            ok = response.ok
            attempts += 1
        return response


def main():

    diciobot = Diciobot()
    diciobot.startBot()

if __name__ == '__main__':
    main()
