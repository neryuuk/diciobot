class Diciobot():
    def tudo(self, verbete):
        tudo = []
        if "_não foi encontrado._" in tudo[0]:
            return tudo
        remover = []
        for i in range(len(tudo)):
            if "* _não tem" in tudo[i]:
                remover.insert(0, i)
        for each in remover:
            tudo.pop(each)
        return tudo
