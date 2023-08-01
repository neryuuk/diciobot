#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position
import requests
from lxml import html
from urllib import request, parse


def buildEndpoint(verbete: str = None, pesquisa: bool = False):
    endpoint = "https://www.dicio.com.br"
    if pesquisa:
        endpoint += "/pesquisa.php?" + parse.urlencode({'q': verbete})
    elif verbete is not None:
        endpoint += f"/{verbete}/".replace("//", "/")

    return endpoint


def buscar(verbete: str) -> (any, any, str):
    try:
        busca = request.urlopen(buildEndpoint(verbete, True))
    except requests.exceptions.TooManyRedirects:
        pass

    tree = html.fromstring(str(busca.read(), "utf-8"))
    if "/pesquisa.php" not in busca.url:
        return busca, tree, ""

    # Retornou uma página de busca
    pagina = tree.xpath('//div[@class="found"]')
    if len(pagina) == 0:
        # Não encontrou resultados pra busca do verbete
        pagina = tree.xpath('//div[@id="enchant"]')
        if len(pagina) == 0:
            # Não tem nenhuma sugestao para o verbete nao encontrado
            return None, None, ""

        # Tem sugestões para o verbete não encontrado
        sugestao = pagina[0].text
        return None, None, sugestao

    # Encontrou resultados pra busca do verbete
    pagina = tree.xpath('//a[@class="_sugg"]')
    for each in pagina:
        content = each.xpath('span[@class="list-link"]/text()')
        # Encontrou o verbete solicitado nos resultados
        if content and content[0] and (content[0] == verbete):
            busca = request.urlopen(buildEndpoint(each.attrib["href"]))
            tree = html.fromstring(str(busca.read(), "utf-8"))
            return busca, tree, ""

    # Não encontrou o verbete solicitado nos resultados
    busca = request.urlopen(buildEndpoint("/404"))
    tree = html.fromstring(str(busca.read(), "utf-8"))
    return busca, tree, sugestao


def buscarDefinicao(verbete: str) -> str:
    verbete = palavra(verbete)
    if not verbete:
        return erroPalavraFaltando("definir")

    pagina, tree, sugestao = buscar(verbete)

    if pagina is None:
        return quatroZeroQuatro(verbete, sugestao)

    if tree is None:
        return ''

    definicao = blocoDefinicao(tree)
    significado = blocoSignificado(tree)

    if (len(definicao) + len(significado)) == 0:
        return f"_O verbete_ *{verbete}* _não tem definição ou significado disponíveis._"
    elif len(significado) == 0:
        definicao += "Significado: Não encontrado."
        return definicao + fonte(pagina)

    return f"{definicao}{significado}{fonte(pagina)}".replace("[", "\[")


def blocoDefinicao(tree) -> str:
    titulo = ''
    for each in tree.xpath('//h2[@class="tit-section"]/text()'):
        titulo = each.split(' ')

    if len(titulo) == 0:
        return ''

    mensagem = f"*{' '.join(titulo[:-1])}* _{titulo[-1]}_"
    definicao = tree.xpath('//p[@class="adicional"]//text()')
    for each in definicao:
        if "\n" in each and not mensagem.endswith("\n"):
            mensagem += "\n"
        if len(each.strip()) > 0:
            mensagem += f"{each.strip()} "

    return f"{mensagem}\n\n".replace(" \n", "\n").replace("\n ", "\n")


def blocoSignificado(tree) -> str:
    titulos = tree.xpath('//h2[@class="tit-significado"]/text()')
    if len(titulos) == 0:
        return ""

    titulo = ""
    for each in titulos:
        titulo = each.split(' ')
    mensagem = f"*{' '.join(titulo[:-1])}* _{titulo[-1]}_\n"
    for each in tree.xpath('//p[@itemprop="description"]/span'):
        if type(each) == html.HtmlElement:
            content = each.text_content().strip().replace("*", "\*")
            if "cl" in each.classes:
                mensagem += f"{content}\n"
            elif "tag" in each.classes:
                mensagem += content
            else:
                mensagem += f"{content}\n"
        else:
            mensagem += f"{each.strip()}\n"

    return f"{mensagem}".replace(" \n", "\n").replace("\n ", "\n")


def quatroZeroQuatro(verbete: str, sugestao: str, verbo: bool = False) -> str:
    naoEncontrado = "_O {}_ *{}* _não foi encontrado._".format(
        "verbo" if verbo else "verbete",
        verbete
    )

    if len(sugestao) == 0:
        return naoEncontrado

    naoEncontrado += "\n\n_Você quis dizer_ *{}*?".format(sugestao)
    return naoEncontrado


def buscarPalavraDoDia() -> str:
    pagina = request.urlopen(buildEndpoint())
    tree = html.fromstring(str(pagina.read(), "utf-8"))
    doDia = tree.xpath("//*[@class='word-link']/text()")[0]
    content = "*Palavra do dia:* _{}_\n\n{}".format(
        doDia, buscarDefinicao(doDia)
    )
    return content


def buscarSinonimosAntonimos(verbete: str, tipo: str = 'Sinônimos') -> str:
    verbete = palavra(verbete)
    if not verbete:
        return erroPalavraFaltando(tipo.lower().replace("ô", "o"))

    pagina, tree, sugestao = buscar(verbete)

    if pagina is None:
        return quatroZeroQuatro(verbete, sugestao)

    if tree is None:
        return ''

    titulos = tree.xpath(
        '//h2[contains(@class, "subtitle-significado")]//text()'
    )

    resultado = ''
    indice = None
    for i, each in enumerate(titulos):
        if tipo in each:
            resultado = each.split(' ')
            indice = i

    if len(resultado) == 0:
        return f"_O verbete_ *{verbete}* _não tem {tipo.lower()} disponíveis._{fonte(pagina)}"

    resultado = f"*{' '.join(resultado[:-1])}* _{resultado[-1]}_\n"

    blocos = tree.xpath('//p[@class="adicional sinonimos"]')[indice]
    lista = blocos.xpath('a//text()')

    if len(lista) > 1:
        resultado += ', '.join(lista[:-1]) + ' e '
    resultado += lista[-1]

    return f"{resultado}{fonte(pagina)}"


def buscarSinonimos(verbete: str) -> str:
    return buscarSinonimosAntonimos(verbete, "Sinônimos")


def buscarAntonimos(verbete: str) -> str:
    return buscarSinonimosAntonimos(verbete, "Antônimos")


def buscarExemplos(verbete: str) -> str:
    pass


def buscarConjugacao(verbete: str) -> str:
    pass


def buscarRimas(verbete: str) -> str:
    pass


def buscarAnagramas(verbete: str) -> str:
    pass


def buscarTudo(verbete: str) -> str:
    pass


def palavra(conteudo: str) -> str:
    if not conteudo.lower().strip():
        return None

    conteudo = conteudo.lower().strip().split(' ', 1)
    if len(conteudo) < 2:
        return None

    return conteudo[-1]


def erroPalavraFaltando(comando: str) -> str:
    return "\n".join([
        "Você precisa informar uma palavra junto com o comando.",
        "", "Exemplos:",
        f"/definir palavra",
        f"/sinonimos palavra",
    ])


def manutencao() -> str:
    return f"Essa opção está em manutenção :(\n\n{ajuda()}"


def fonte(pagina) -> str:
    if not pagina:
        return ''
    if not pagina.url:
        return ''

    return "\n\n*Fonte:* " + pagina.url.replace("_", "\_")


def ajuda() -> str:
    return "\n".join([
        "As opções *disponíveis* são as _seguintes_:",
        "",
        "/definir ou /d - *definição* de um _verbete_",
        "/sinonimos ou /s - *sinônimos* de um _verbete_",
        "/antonimos ou /a - *antônimos* de um _verbete_",
        # "/exemplos ou /e - *exemplos* de utilização de um _verbete_",
        # "/conjugar ou /c - *conjugar* um _verbo_",
        # "/rimas ou /r - *rimas* de um _verbete_",
        # "/anagramas ou /ana - *anagramas* de um _verbete_",
        # "/tudo ou /t - *todas* as opções *disponíveis* de um _verbete_",
        "/dia - *Palavra do dia*."
    ])


def dica() -> str:
    return " ".join([
        "*Dica*: Quando estiver falando *diretamente* com o bot,",
        "você pode mandar diversas palavras separadas por",
        "*vírgula* para obter suas definições.",
        "(Sem precisar do comando /definir)\n",
    ])
