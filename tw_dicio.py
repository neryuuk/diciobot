#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lxml import html
from urllib import request

base_url = "https://www.dicio.com.br"
pagina = request.urlopen(base_url)

tree = html.fromstring(str(pagina.read()))
doDia = tree.xpath("//*[@class='word-link']")
url = base_url + doDia[0].attrib["href"]
definir = "Palavra do dia: {}\n{}".format(doDia[0].text, url)

print(definir)
