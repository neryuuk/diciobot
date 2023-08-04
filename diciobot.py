from lxml import html


class Diciobot():
    def tudo(self, verbete):
        tudo = []
        tudo.append(self.definir(verbete))
        if "_não foi encontrado._" in tudo[0]:
            return tudo
        tudo.append(self.exemplos(verbete))
        tudo.append(self.conjugar(verbete))
        tudo.append(self.anagramas(verbete))
        remover = []
        for i in range(len(tudo)):
            if "* _não tem" in tudo[i]:
                remover.insert(0, i)
        for each in remover:
            tudo.pop(each)
        return tudo

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
