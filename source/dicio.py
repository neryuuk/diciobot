#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position
from lxml.html import fromstring, HtmlElement
from urllib import parse, request
import re


def buildEndpoint(verbete: str = None, pesquisa: bool = False):
    endpoint = "https://www.dicio.com.br"
    if pesquisa:
        endpoint += "/pesquisa.php?" + parse.urlencode({"q": verbete})
    elif verbete is not None:
        endpoint += f"/{verbete}/".replace("//", "/")

    return endpoint


def buscar(verbete: str, comando: callable) -> [str]:
    verbete = palavra(verbete)
    if not verbete:
        return [erroPalavraFaltando(comando)]

    busca = request.urlopen(buildEndpoint(verbete, True))

    tree = fromstring(str(busca.read(), "utf-8"))
    if tree is None:
        return [""]

    if "/pesquisa.php" not in busca.url:
        return chamaComando(verbete, comando, busca.url, tree)

    # Retornou uma página de busca
    pagina = tree.xpath("//ul[@class='resultados']/li/a[@class='_sugg']")
    if len(pagina) == 0:
        # Não tem nenhuma sugestao para o verbete nao encontrado
        return [""]

    # Encontrou resultados pra busca do verbete
    for each in pagina:
        content = each.xpath("span[@class='list-link']/text()")
        # Encontrou o verbete solicitado nos resultados
        if content and content[0] and (content[0].strip() == verbete):
            busca = request.urlopen(buildEndpoint(each.attrib["href"]))
            tree = fromstring(str(busca.read(), "utf-8"))
            return chamaComando(verbete, comando, busca.url, tree)

    try:
        sugestao = pagina[0].xpath("span[@class='list-link']/text()")[0]

        # Não encontrou o verbete solicitado nos resultados
        return quatroZeroQuatro(verbete, sugestao.strip())
    except:
        return quatroZeroQuatro(verbete, "")


def chamaComando(verbete: str, comando: callable, url: str, tree: HtmlElement) -> [str]:
    resultado = []
    for item in comando(verbete, tree):
        resultado.append(re.sub(r" *\n *", r"\n", item) + fonte(url))
    return resultado


def definir(verbete: str, tree: HtmlElement) -> [str]:
    definicao: str = blocoDefinicao(tree)
    significado: str = blocoSignificado(tree)

    if (len(definicao) + len(significado)) == 0:
        return [f"_O verbete_ *{verbete}* _não tem definição ou significado disponíveis._"]
    elif len(significado) == 0:
        definicao += "Significado: Não encontrado."
        return [definicao]

    return [f"{definicao}\n\n{significado}".strip().replace("[", "\[")]


def blocoDefinicao(tree: HtmlElement) -> str:
    titulo = ""
    for each in tree.xpath("//h2[@class='tit-section']/text()"):
        titulo = each.split(" ")

    if len(titulo) == 0:
        return ""

    mensagem = f"*{' '.join(titulo[:-1])}* _{titulo[-1]}_"
    definicao = tree.xpath("//p[@class='adicional']//text()")
    for each in definicao:
        if "\n" in each and not mensagem.endswith("\n"):
            mensagem += "\n"
        if len(each.strip()) > 0:
            mensagem += f"{each.strip()} "

    return mensagem.strip()


def blocoSignificado(tree: HtmlElement) -> str:
    titulos = tree.xpath("//h2[@class='tit-significado']/text()")
    if len(titulos) == 0:
        return ""

    titulo = ""
    for each in titulos:
        titulo = each.split(" ")
    mensagem = f"*{' '.join(titulo[:-1])}* _{titulo[-1]}_\n"
    for each in tree.xpath("//p[@itemprop='description']/span"):
        if type(each) == HtmlElement:
            content = each.text_content().strip().replace("*", "\*")
            if "cl" in each.classes:
                mensagem += f"{content}\n"
            elif "tag" in each.classes:
                mensagem += content
            else:
                mensagem += f"{content}\n"
        else:
            mensagem += f"{each.strip()}\n"

    return mensagem.strip()


def quatroZeroQuatro(verbete: str, sugestao: str) -> [str]:
    naoEncontrado = f"_O verbete_ *{verbete}* _não foi encontrado._"

    if len(sugestao) == 0:
        return [naoEncontrado]

    return [f"{naoEncontrado}\n\n_Você quis dizer_ *{sugestao}*?"]


def dia() -> str:
    pagina = request.urlopen(buildEndpoint())
    tree = fromstring(str(pagina.read(), "utf-8"))
    doDia = tree.xpath("//*[@class='word-link']/text()")[0]
    return f"*Palavra do dia:* _{doDia}_\n\n{buscar(f'/dia {doDia}', definir)[0]}"


def buscarSinonimosAntonimos(verbete: str, tree: HtmlElement, tipo: str = "Sinônimos") -> str:
    resultado = ""
    indice = None
    for i, each in enumerate(tree.xpath("//h2[contains(@class, 'subtitle-significado')]//text()")):
        if tipo in each:
            resultado = each.split(" ")
            indice = i
            break

    if len(resultado) == 0:
        return f"_O verbete_ *{verbete}* _não tem {tipo.lower()} disponíveis._"

    resultado = f"*{' '.join(resultado[:-1])}* _{resultado[-1]}_\n"

    blocos = tree.xpath("//p[@class='adicional sinonimos']")[indice]
    lista = blocos.xpath("a//text()")

    if len(lista) > 1:
        resultado += f"{', '.join(lista[:-1])} e "
    return resultado + lista[-1]


def sinonimos(verbete: str, tree: HtmlElement) -> [str]:
    return [buscarSinonimosAntonimos(verbete, tree, "Sinônimos")]


def antonimos(verbete: str, tree: HtmlElement) -> [str]:
    return [buscarSinonimosAntonimos(verbete, tree, "Antônimos")]


def exemplos(verbete: str, tree: HtmlElement) -> [str]:
    frases = blocoFrasesExemplos(tree)
    exemplos = blocoFrasesExemplos(tree, "exemplo")

    if len(frases + exemplos) == 0:
        return [f"_O verbete_ *{verbete}* _não tem frases ou exemplos disponíveis._"]

    return [f"{frases}\n\n{exemplos}".strip()]


def blocoFrasesExemplos(tree: HtmlElement, tipo: str = "frases") -> str:
    TIPO = {"frases": "Frases ", "exemplo": "Exemplos "}
    div = None
    for each in tree.xpath(f"//h3[@class='tit-{tipo}']"):
        if TIPO[tipo] in each.text_content():
            div = each
            break

    if div is None:
        return ""

    resultado = div.text_content().split(" ")
    resultado = f"*{' '.join(resultado[:-1])}* _{resultado[-1]}_:\n"
    for each in div.getparent().xpath("node()/div[@class='frase']"):
        text = re.sub(r"\s{2,}", r" ", each.text_content().strip())
        ref = each.xpath(".//em/text()")
        if len(ref) > 0:
            text = text.replace(f"{ref[0]}", f"\n_{ref[0]}_")

        resultado += f"{text}\n\n"

    return resultado.strip()


def conjugar(verbete: str, tree: HtmlElement) -> [str]:
    if len(tree.xpath("//div[@id='conjugacao']//node()")) == 0:
        return [f"_O verbete_ *{verbete}* _não tem conjugação disponível._\n_Tente um verbo no_ *infinitivo*."]

    resultado: str = None
    for each in tree.xpath("//h3[@class='tit-other']/text()"):
        if "Conjugação " in each:
            resultado = each.split(" ")
            resultado = f"*{' '.join(resultado[:-1])}* _{resultado[-1]}_\n\n"
            break

    for each in tree.xpath("//div[@id='conjugacao']/p"):
        if type(each) == HtmlElement:
            resultado += re.sub(r" {2,}", r" ", each.text_content().strip())
    resultado += "\n\n"

    modos_nome = tree.xpath("//div[@class='modo']//text()")
    for i, modo in enumerate(tree.xpath("//div[contains(@class, 'verb-wrapper')]/ul")):
        resultado += f"*{modos_nome[i]}*\n"
        for tempo in modo.findall('li'):
            resultado += f"*{tempo.find('div').text_content().strip()}*\n"
            tempo.find('div').drop_tree()
            texto = tempo.text_content().strip() + "\n\n"
            resultado += re.sub(r" {2,}", r" ", texto).replace("*", "\*")

    return [resultado.strip()]


def rimasAnagramas(verbete: str, tree: HtmlElement, tipo: str = "Rimas") -> str:
    resultado = ""
    indice = None
    for i, each in enumerate(tree.xpath("//h3[@class='tit-other']/text()")):
        if tipo in each:
            resultado = each.split(" ")
            indice = i
            break

    if len(resultado) == 0:
        return f"_O verbete_ *{verbete}* _não tem {tipo.lower()} disponíveis._"

    resultado = f"*{' '.join(resultado[:-1])}* _{resultado[-1]}_\n\n"
    elemento = tree.xpath(
        "//div[@class='wrap-section']/h3[@class='tit-other']/..")[indice].xpath("./ul/li//text()")
    if len(elemento) > 1:
        resultado += f"{', '.join(elemento[:-1])} e "
    return resultado + elemento[-1]


def rimas(verbete: str, tree: HtmlElement) -> [str]:
    return [rimasAnagramas(verbete, tree, "Rimas")]


def anagramas(verbete: str, tree: HtmlElement) -> [str]:
    return [rimasAnagramas(verbete, tree, "Anagramas")]


def tudo(verbete: str, tree: HtmlElement) -> [str]:
    return (
        definir(verbete, tree) +
        sinonimos(verbete, tree) +
        antonimos(verbete, tree) +
        exemplos(verbete, tree) +
        conjugar(verbete, tree) +
        rimas(verbete, tree) +
        anagramas(verbete, tree)
    )


def palavra(conteudo: str) -> str:
    if not conteudo.lower().strip():
        return None

    conteudo = conteudo.lower().strip().split(" ", 1)
    if len(conteudo) < 2:
        return None

    return conteudo[-1]


def erroPalavraFaltando(comando: callable) -> str:
    return (
        f"Você precisa informar uma palavra junto com o comando.\n"
        f"\n"
        f"Exemplo:\n"
        f"/{comando.__name__} palavra\n"
    )


def fonte(pagina) -> str:
    if not pagina:
        return ""

    return f"\n\n*Fonte:* {pagina}"


def ajuda() -> str:
    return (
        f"As opções *disponíveis* são as _seguintes_:\n"
        f"\n"
        f"/definir ou /d - *definição* de um _verbete_\n"
        f"/sinonimos ou /s - *sinônimos* de um _verbete_\n"
        f"/antonimos ou /a - *antônimos* de um _verbete_\n"
        f"/exemplos ou /e - *exemplos* de utilização de um _verbete_\n"
        f"/conjugar ou /c - *conjugar* um _verbo_\n"
        f"/rimas ou /r - *rimas* de um _verbete_\n"
        f"/anagramas ou /ana - *anagramas* de um _verbete_\n"
        f"/tudo ou /t - *todas* as opções *disponíveis* de um _verbete_\n"
        f"/dia - *Palavra do dia*."
    )


def dica() -> str:
    return (
        f"*Dica*: Quando estiver falando *diretamente* com o bot, "
        f"você pode mandar diversas palavras separadas por "
        f"*vírgula* para obter suas definições. "
        f"(Sem precisar do comando /definir)\n"
    )
