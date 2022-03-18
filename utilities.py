def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def GetTransitions(transitions):
    trans = ''
    for key, value in transitions.items():
        for s, n in value.items():
            s_real = s.replace(' ', '')
            trans += f'({key}, {s_real}, {n})' + ' - '
            # print(f'({key}, {s_real}, {n})')

    return trans

def getAlphabet(transicion):
    alphabet = []
    for v in transicion.values():
        for k in v.keys():
            alphabet.append(k)

    return { *alphabet }, { *[a.replace(' ', '') for a in alphabet] }
