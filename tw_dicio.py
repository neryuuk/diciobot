#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import twitter
import json
from lxml import html

base_url = "http://www.dicio.com.br"
pagina = requests.get(base_url)
tree = html.fromstring(pagina.text)
doDia = tree.xpath('//*[@id="dia"]/a/text()')[0]
p = tree.xpath('//*[@id="dia"]/p/text()')[0].replace("\n", " ")
print(len(doDia + p))
url = base_url + tree.xpath('//*[@id="dia"]/a/@href')[0]
definir = "Palavra do dia: " + doDia + "\n" + p + "\n" + url

print(definir)
