#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument, wrong-import-position
from dicio import *

print(dia())

print(buscar("/d ornitorrinco", definir))

print(buscar("/d maca", definir))

print(buscar("/d label", definir))

print(buscar("/s subir", sinonimos))

print(buscar("/s gorgona", sinonimos))

print(buscar("/a descer", antonimos))

print(buscar("/a gorgona", antonimos))

print(buscar("/r carro", rimas))

print(buscar("/r orfã", rimas))

print(buscar("/ana carro", anagramas))

print(buscar("/ana chicharro", anagramas))

print(buscar("/e carro", exemplos))

print(buscar("/e pseudocristão", exemplos))
