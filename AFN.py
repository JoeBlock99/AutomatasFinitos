epsilon = 'ε'

class Node():
    def __init__(self, codigo, transitions = []):
        self.id = codigo
        self.transitions = transitions

    def toString(self):
        return (f'Nodo: {self.id} --- {self.checkTransitions()}')

    def AddTransition(self, symbol, state):
        self.transitions.append((symbol, state))

    def checkTransitions(self):
        sTransicion = ''
        for t in self.transitions:
            sTransicion += f'\n\t{self.id} --> "{t[0]}" --> {t[1].id}'

        return sTransicion

class NDFA():
    def __init__(self, regular_expression):
        self.init_state = None
        self.final_state = None
        self.states = []
        self.symbols = []
        self.ids = 0

        regular_expression = self.OperationSubstitution(regular_expression)
        regular_expression = self.createChains(regular_expression)
        print('Expression filtered:', regular_expression)
        self.Evaluar(regular_expression)

    def simulateNFA(self, exp):
        S = self.e_closure([self.init_state])

        for e in exp:
            S = self.e_closure(self.Move(S, e))

        if str(self.final_state.id) in [str(s.id) for s in S]:
            return 'yes'
        else:
            return 'no'

    def CheckArrayStates(self, states, n):
        return str(n.id) in [str(s.id) for s in states]

    def e_closure(self, states):
        stack = [] + states
        closure = [] + states

        while len(stack) != 0:
            t = stack.pop()

            for transition in t.transitions:
                s, state = [*transition]
                if epsilon == s:
                    if not self.CheckArrayStates(closure, state):
                        stack.append(state)
                        closure.append(state)

        return closure

    def Move(self, T, symbol):
        moves = []
        for t in T:
            for transition in t.transitions:
                s, state = [*transition]
                if symbol == s:
                    moves.append(state)

        return moves

    def GetStates(self):
        return {str(s.id) for s in self.states}

    def CreateTransitionFunction(self):
        f = {}
        for e in self.states:
            cont = 1
            f[str(e.id)] = {}

            for t in e.transitions:
                symbol, node = [*t]

                if str(symbol) in f[str(e.id)].keys():
                    f[str(e.id)][str(symbol) + ' '*cont] = str(node.id)
                    cont += 1
                else:
                    f[str(e.id)][str(symbol)] = str(node.id)
        return f

    def createChains(self, expression):
        new = ''
        operations = ['*','|','(','?','+']
        cont = 0
        while cont < len(expression):
            if cont+1 >= len(expression):
                new += expression[-1]
                break

            if expression[cont] == '*' and not (expression[cont+1] in operations) and expression[cont+1] != ')':
                new += expression[cont]+'.'
            elif expression[cont] == '*' and expression[cont+1] == '(':
                new += expression[cont]+'.'
            elif expression[cont] == '?' and not (expression[cont+1] in operations) and expression[cont+1] != ')':
                new += expression[cont]+'.'
            elif expression[cont] == '?' and expression[cont+1] == '(':
                new += expression[cont]+'.'
            elif not (expression[cont] in operations) and expression[cont+1] == ')':
                new += expression[cont]
            elif (not (expression[cont] in operations) and not (expression[cont+1] in operations)) or (not (expression[cont] in operations) and (expression[cont+1] == '(')):
                new += expression[cont]+'.'
            else:
                new += expression[cont]
        
            cont += 1
        return new

    def OperationSubstitution(self, regular):
        real = []
        exp = []
        hasExpression = False
        hasPlus = False
        initial = []
        final = 0
        i = 0

        if ')+' in regular:
            while i < len(regular):
                if regular[i] == '(':
                    initial.append(i)                        

                if regular[i] == ')' and i < len(regular) - 1:
                    real.append(regular[i])
                    if regular[i + 1] == '+':
                        final = i + 1
                        real.append('*')
                        # real.append('.')
                        real.append(regular[initial.pop() : final])
                        i += 1
                    else:
                        initial.pop()

                else:
                    real.append(regular[i])
                i += 1

            regular = ''.join(real)

        if ')?' in regular:
            while i < len(regular):
                if regular[i] == '(':
                    initial.append(i)                        

                if regular[i] == ')':
                    real.append(regular[i])
                    if regular[i + 1] == '?':
                        final = i + 1
                        real.append('|')
                        real.append(epsilon)
                        real.append(')')
                        real.insert(initial[-1], '(')
                        i += 1
                    else:
                        initial.pop()

                else:
                    real.append(regular[i])
                i += 1

            regular = ''.join(real)

        regular_copy = regular
        if '+' in regular:
            while '+' in regular_copy:
                i = regular_copy.find('+')
                symbol = regular_copy[i - 1]

                regular_copy = regular_copy.replace(symbol + '+', '(' + symbol + '*' + symbol + ')')

        if '?' in regular_copy:
            while '?' in regular_copy:
                i = regular_copy.find('?')
                symbol = regular_copy[i - 1]

                regular_copy = regular_copy.replace(symbol + '?', '(' + symbol + '|' + epsilon + ')')

        if regular_copy.count('(') > regular_copy.count(')'):
            for i in range(regular_copy.count('(') - regular_copy.count(')')):
                regular_copy += ')'
                print(regular_copy)

        elif regular_copy.count('(') < regular_copy.count(')'):
            for i in range(regular_copy.count(')') - regular_copy.count('(')):
                regular_copy = '(' + regular_copy

        return regular_copy

    def MergeNodes(self, nodeA, nodeB):
        # Quitar de states
        nodeA.transitions += nodeB.transitions
        i = self.states.index(nodeB)
        self.states.pop(i)

    def CreateORNodes(self, a, b):
        if type(a) == tuple and type(b) == tuple:
            a_inicial, a_final = [*a]
            b_inicial, b_final = [*b]

            # Nodo final de OR
            nodeF = Node(self.ids + 2, [])

            # Nodo init de OR
            nodeI = Node(self.ids + 1, [(epsilon, a_inicial), (epsilon, b_inicial)])

            a_final.AddTransition(epsilon, nodeF)
            b_final.AddTransition(epsilon, nodeF)

            self.ids += 2

            # Estados
            self.states.append(nodeF)
            self.states.append(nodeI)

            return nodeI, nodeF
            
        elif type(a) != tuple and type(b) != tuple:
            # Nodo final de OR
            nodeF = Node(self.ids + 6, [])

            nodeFinalA = Node(self.ids + 5, [(epsilon, nodeF)])
            nodeFinalB = Node(self.ids + 4, [(epsilon, nodeF)])

            nodeInicialA = Node(self.ids + 3, [(a, nodeFinalA)])
            nodeInicialB = Node(self.ids + 2, [(b, nodeFinalB)])

            # Nodo init de OR
            nodeI = Node(self.ids + 1, [(epsilon, nodeInicialA), (epsilon, nodeInicialB)])

            self.ids += 6

            # Estados
            self.states.append(nodeF)
            self.states.append(nodeFinalA)
            self.states.append(nodeFinalB)
            self.states.append(nodeInicialA)
            self.states.append(nodeInicialB)
            self.states.append(nodeI)

            return nodeI, nodeF
        elif type(a) != tuple and type(b) == tuple:
            b_inicial, b_final = [*b]

            nodeF = Node(self.ids + 4, [])

            nodeFinalA = Node(self.ids + 3, [(epsilon, nodeF)])
            nodeInicialA = Node(self.ids + 2, [(a, nodeFinalA)])

            nodeI = Node(self.ids + 1, [(epsilon, b_inicial), (epsilon, nodeInicialA)])
            b_final.AddTransition(epsilon, nodeF)

            self.ids += 4

            # Estados
            self.states.append(nodeF)
            self.states.append(nodeFinalA)
            self.states.append(nodeInicialA)
            self.states.append(nodeI)

            return nodeI, nodeF
        elif type(a) == tuple and type(b) != tuple:
            a_inicial, a_final = [*a]
            nodeF = Node(self.ids + 4, [])

            nodeFinalB = Node(self.ids + 3, [(epsilon, nodeF)])
            nodeInicialB = Node(self.ids + 2, [(b, nodeFinalB)])

            nodeI = Node(self.ids + 1, [(epsilon, a_inicial), (epsilon, nodeInicialB)])
            a_final.AddTransition(epsilon, nodeF)

            self.ids += 4

            # Estados
            self.states.append(nodeF)
            self.states.append(nodeFinalB)
            self.states.append(nodeInicialB)
            self.states.append(nodeI)
            return nodeI, nodeF  

    def CreateCATNodes(self, a, b):
        if type(a) == tuple and type(b) == tuple:
            a_inicial, a_final = [*a]
            b_inicial, b_final = [*b]

            self.MergeNodes(a_final, b_inicial)
            return a_inicial, b_final
        elif type(a) != tuple and type(b) != tuple:
            # Nodo final de CAT
            node3 = Node(self.ids + 3, [])

            # Nodo en medio de CAT
            node2 = Node(self.ids + 2, [(b, node3)])

            # Nodo init de CAT
            node1 = Node(self.ids + 1, [(a, node2)])
            self.ids += 3

            self.states.append(node1)
            self.states.append(node2)
            self.states.append(node3)            

            return node1, node3
        elif type(a) != tuple and type(b) == tuple:
            b_inicial, b_final = [*b]

            nodeI = Node(self.ids + 1, [(a, b_inicial)])
            self.states.append(nodeI)
            self.ids += 1

            return nodeI, b_final
        elif type(a) == tuple and type(b) != tuple:
            a_inicial, a_final = [*a]

            nodeF = Node(self.ids + 1, [])
            self.states.append(nodeF)
            a_final.AddTransition(b, nodeF)
            self.ids += 1
            
            return a_inicial, nodeF

    def CreateSTARNodes(self, a, haGeneradoPrimerGrafo = False, nodeInicial = None, nodeFA = None, nodeIB = None, nodeFinal = None):
        if type(a) == tuple:
            a_inicial, a_final = [*a]
            
            # Nodo final de *
            node4 = Node(self.ids + 2, [])

            # Nodo init de *
            node1 = Node(self.ids + 1, [(epsilon, a_inicial), (epsilon, node4)])

            a_final.AddTransition(epsilon, node4)
            a_final.AddTransition(epsilon, a_inicial)
            self.ids += 2

            self.states.append(node1)
            self.states.append(node4)
            return node1, node4
        else:
            # Nodo final de *
            node4 = Node(self.ids + 4, [])

            # Nodo en medio final de *
            node3 = Node(self.ids + 3, [(epsilon, node4)])

            # Nodo en medio init de *
            node2 = Node(self.ids + 2, [(a, node3)])

            # Nodo init de *
            node1 = Node(self.ids + 1, [(epsilon, node2), (epsilon, node4)])

            node3.AddTransition(epsilon, node2)
            self.ids += 4

            self.states.append(node1)
            self.states.append(node2)
            self.states.append(node3)
            self.states.append(node4)
            return node1, node4

    def ObtenerPrecedencia(self, operation):
        if operation == '|':
            return 1
        if operation == '.':
            return 2
        if operation == '*' or operation == '+' or operation == '?':
            return 3
        return 0

    def Operar(self, x, y, operation):
        if operation == '|': return self.CreateORNodes(x, y)
        if operation == '.': return self.CreateCATNodes(x, y)
        if operation == '*': return self.CreateSTARNodes(y)

    def EsSimbolo(self, digit):
        digitos = 'abcdefghijklmnopqrstuvwxyz0123456789' + epsilon
        if digit in digitos:
            return True
        return False

    def Evaluar(self, expression):
        symbols = []
        operaciones = []
        i = 0

        haGeneradoPrimerGrafo = False
        while i < len(expression):
            if expression[i] == '(':
                operaciones.append(expression[i])

            elif self.EsSimbolo(expression[i]):
                val = ''

                while i < len(expression) and self.EsSimbolo(expression[i]):
                    val += expression[i]
                    i += 1

                symbols.append(val)
                i -= 1

            elif expression[i] == ')':
                while len(operaciones) != 0 and operaciones[-1] != '(':
                    op = operaciones.pop()
                    val2 = symbols.pop()
                    val1 = None

                    if op != '*' and op != '+' and op != '?':
                        val1 = symbols.pop()
                    
                    start, end = self.Operar(val1, val2, op)
                    symbols.append((start, end))

                operaciones.pop()

            else:
                while (len(operaciones) != 0
                    and self.ObtenerPrecedencia(operaciones[-1]) >= self.ObtenerPrecedencia(expression[i])):
                    op = operaciones.pop()
                    val2 = symbols.pop()
                    val1 = None

                    if op != '*' and op != '+' and op != '?':
                        val1 = symbols.pop()
                    
                    start, end = self.Operar(val1, val2, op)
                    symbols.append((start, end))
                operaciones.append(expression[i])

            i += 1

        while len(operaciones) != 0:
            op = operaciones.pop()
            val2 = symbols.pop()
            val1 = None

            if op != '*' and op != '+' and op != '?':
                val1 = symbols.pop()
            
            start, end = self.Operar(val1, val2, op)
            symbols.append((start, end))
        
        self.init_state, self.final_state = symbols.pop()
