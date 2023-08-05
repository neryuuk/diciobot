from lxml import html


class Diciobot():
    def tudo(self, verbete):
        tudo = []
        tudo.append(self.definir(verbete))
        if "_não foi encontrado._" in tudo[0]:
            return tudo
        tudo.append(self.conjugar(verbete))
        remover = []
        for i in range(len(tudo)):
            if "* _não tem" in tudo[i]:
                remover.insert(0, i)
        for each in remover:
            tudo.pop(each)
        return tudo

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
