import AFD
import functools

epsilon = 'ε'

class Leaf():
    def __init__(self, value, position, is_operation, children, nullable):
        self.value = value
        self.position = position
        self.is_operation = is_operation
        self.children = children
        self.nullable = nullable

        self.first_pos = []
        self.last_pos = []
        self.follow_pos = []
        if self.value == epsilon:
            self.nullable = True
        
        self.AddFirstPos()
        self.AddLastPos()

    def GetName(self):
        return f'{self.value} - {self.position}'

    def AddFirstPos(self):
        if self.is_operation:
            if self.value == '|':
                self.first_pos = self.children[0].first_pos + self.children[1].first_pos
            elif self.value == '.':
                if self.children[0].nullable:
                    self.first_pos = self.children[0].first_pos + self.children[1].first_pos
                else:
                    self.first_pos += self.children[0].first_pos
            elif self.value == '*':
                self.first_pos += self.children[0].first_pos
        else:
            if self.value != epsilon:
                self.first_pos.append(self.position)

    def AddLastPos(self):
        if self.is_operation:
            if self.value == '|':
                self.last_pos = self.children[0].last_pos + self.children[1].last_pos
            elif self.value == '.':
                if self.children[1].nullable:
                    self.last_pos = self.children[0].last_pos + self.children[1].last_pos
                else:
                    self.last_pos += self.children[1].last_pos
            elif self.value == '*':
                self.last_pos += self.children[0].last_pos
        else:
            if self.value != epsilon:
                self.last_pos.append(self.position)

class Tree():
    def __init__(self, regular_expression):
        self.count = 0
        self.rounds = 1
        self.states = []

        self.symbols = []
        self.transiciones = []
        self.acceptance_states = []
        self.init_state = None
        
        self.nodes = []
        self.root = None
        self.id = 0
        self.primera_vez = True
        self.final_state = None

        self.follow_pos = {}
        regular_expression = self.OperationSubstitution(regular_expression)
        regular_expression = self.createChains(regular_expression)
        print('Expression filtered:', regular_expression)
        self.trigerTree(regular_expression)
        for n in self.nodes:
            if n.value == '#':
                self.final_state = n.position
                break
        self.findTrail()
        print(self.follow_pos)
        self.generateDFA()

    def simulateDFA(self, exp):
        S = self.init_state

        for e in exp:
            S = self.moveSimulation(S, e)

            if S == None:
                return 'no'

        if S in self.acceptance_states:
            return 'yes'
            
        return 'no'
        
    def moveSimulation(self, Nodo, symbol):
        move = None
        for i in self.transiciones:
            if i[0] == Nodo and i[1] == symbol:
                move = i[2]

        return move
    
    def createChains(self, expresion):
        new = ''
        operations = ['*','|','(','?','+']
        cont = 0
        while cont < len(expresion):
            if cont+1 >= len(expresion):
                new += expresion[-1]
                break

            if expresion[cont] == '*' and not (expresion[cont+1] in operations) and expresion[cont+1] != ')':
                new += expresion[cont]+'.'
            elif expresion[cont] == '*' and expresion[cont+1] == '(':
                new += expresion[cont]+'.'
            elif expresion[cont] == '?' and not (expresion[cont+1] in operations) and expresion[cont+1] != ')':
                new += expresion[cont]+'.'
            elif expresion[cont] == '?' and expresion[cont+1] == '(':
                new += expresion[cont]+'.'
            elif not (expresion[cont] in operations) and expresion[cont+1] == ')':
                new += expresion[cont]
            elif (not (expresion[cont] in operations) and not (expresion[cont+1] in operations)) or (not (expresion[cont] in operations) and (expresion[cont+1] == '(')):
                new += expresion[cont]+'.'
            else:
                new += expresion[cont]
        
            cont += 1
        return new

    def doTransitions(self):
        f = {}
        for t in self.transiciones:
            i, s, fi = [*t]

            if i not in f.keys():
                f[i] = {}
            f[i][s] = fi

        return f

    def generateDFA(self):
        s0 = self.root.first_pos
        print(s0)
        s0_dfa = AFD.NodeDFA(self.getName(), s0, True)
        self.states.append(s0_dfa)
        self.init_state = s0_dfa.value

        if self.final_state in [u for u in s0_dfa.conjunto_nodes]:
            self.acceptance_states.append(s0_dfa.value)

        while not self.checkMarkedState():
            T = self.getUnmarkedState()
            
            T.Mark()

            for s in self.symbols:
                fp = []
                
                for u in T.conjunto_nodes:
                    if self.getLeafByName(u).value == s:
                        fp += self.follow_pos[u]
                fp = {a for a in fp}
                fp = [a for a in fp]
                if len(fp) == 0:
                    continue

                U = AFD.NodeDFA(self.getName(), fp, True)

                if U.id not in [n.id for n in self.states]:
                    print(fp)
                    if self.final_state in [u for u in U.conjunto_nodes]:
                        self.acceptance_states.append(U.value)
                    
                    self.states.append(U)
                    print((T.conjunto_nodes, s, U.conjunto_nodes))
                    self.transiciones.append((T.value, s, U.value))
                else:
                    self.count -= 1
                    for state in self.states:
                        if U.id == state.id:
                            self.transiciones.append((T.value, s, state.value))
                            print((T.conjunto_nodes, s, state.conjunto_nodes))

    def getLeafByName(self, value):
        for n in self.nodes:
            if n.position == value:
                return n

    def getUnmarkedState(self):
        for n in self.states:
            if not n.isMarked:
                return n

    def getName(self):
        if self.count == 0:
            self.count += 1
            return 'S'

        possible_values = ' ABCDEFGHIJKLMNOPQRTUVWXYZ'
        value = possible_values[self.count]
        self.count += 1

        if self.count == len(possible_values):
            self.rounds += 1
            self.count = 0

        return value * self.rounds

    def findTrail(self):
        for n in self.nodes:
            if not n.is_operation and not n.nullable:
                self.addTrail(n.position, [])

        for n in self.nodes:
            if n.value == '.':
                c1, c2 = [*n.children]

                for i in c1.last_pos:
                    self.addTrail(i, c2.first_pos)

            elif n.value == '*':
                for i in n.last_pos:
                    self.addTrail(i, n.first_pos)                

    def checkMarkedState(self):
        marks = [n.isMarked for n in self.states]
        return functools.reduce(lambda a, b: a and b, marks)

    def addTrail(self, pos, val):
        if pos not in self.follow_pos.keys():
            self.follow_pos[pos] = []

        self.follow_pos[pos] += val
        self.follow_pos[pos] = {i for i in self.follow_pos[pos]}
        self.follow_pos[pos] = [i for i in self.follow_pos[pos]]

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

        elif regular_copy.count('(') < regular_copy.count(')'):
            for i in range(regular_copy.count(')') - regular_copy.count('(')):
                regular_copy = '(' + regular_copy

        regular_copy = '(' + regular_copy + ')#'
        return regular_copy

    def last(self, stack):
        return stack[-1] if stack else None

    def checkSymbol(self, s):
        digitos = 'abcdefghijklmnopqrstuvwxyz0123456789#' + epsilon
        if s in digitos:
            return True
        return False

    def getNodeID(self):
        self.id += 1
        return self.id

    def doOperation(self, operations, values):
        operation = operations.pop()
        right = values.pop()
        left = '@'

        if right not in self.symbols and right != epsilon and right != '@' and right != '#':
            self.symbols.append(right)

        if operation != '*' and operation != '+' and operation != '?':
            left = values.pop()

            if left not in self.symbols and left != epsilon and left != '@' and left != '#':
                self.symbols.append(left)

        if operation == '|': return self.opOR(left, right)
        elif operation == '.': return self.opChain(left, right)
        elif operation == '*': return self.opKleene(right)

    def opKleene(self, leaf):
        operation = '*'
        if isinstance(leaf, Leaf):
            root = Leaf(operation, None, True, [leaf], True)
            self.nodes += [root]
            return root

        else:
            id_left = None
            if leaf != epsilon:
                id_left = self.getNodeID()

            left_leaf = Leaf(leaf, id_left, False, [], False)
            root = Leaf(operation, None, True, [left_leaf], True)
            self.nodes += [left_leaf, root]

            return root

    def opOR(self, left, right):
        operation = '|'
        if isinstance(left, Leaf) and isinstance(right, Leaf):
            root = Leaf(operation, None, True, [left, right], left.nullable or right.nullable)
            self.nodes += [root]
            return root

        elif not isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_left = None
            id_right = None
            if left != epsilon:
                id_left = self.getNodeID()
            if right != epsilon:
                id_right = self.getNodeID()

            left_leaf = Leaf(left, id_left, False, [], False)
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operation, None, True, [left_leaf, right_leaf], left_leaf.nullable or right_leaf.nullable)

            self.nodes += [left_leaf, right_leaf, root]
            return root

        elif isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_right = None
            if right != epsilon:
                id_right = self.getNodeID()
            
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operation, None, True, [left, right_leaf], left.nullable or right_leaf.nullable)

            self.nodes += [right_leaf, root]
            return root

        elif not isinstance(left, Leaf) and isinstance(right, Leaf):
            id_left = None
            if left != epsilon:
                id_left = self.getNodeID()
            
            left_leaf = Leaf(left, id_left, False, [], False)
            root = Leaf(operation, None, True, [left_leaf, right], left_leaf.nullable or right.nullable)

            self.nodes += [left_leaf, root]
            return root

    def opChain(self, left, right):
        operation = '.'
        if isinstance(left, Leaf) and isinstance(right, Leaf):
            root = Leaf(operation, None, True, [left, right], left.nullable and right.nullable)
            self.nodes += [root]
            return root

        elif not isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_left = None
            id_right = None
            if left != epsilon:
                id_left = self.getNodeID()
            if right != epsilon:
                id_right = self.getNodeID()

            left_leaf = Leaf(left, id_left, False, [], False)
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operation, None, True, [left_leaf, right_leaf], left_leaf.nullable and right_leaf.nullable)

            self.nodes += [left_leaf, right_leaf, root]
            return root

        elif isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_right = None
            if right != epsilon:
                id_right = self.getNodeID()
            
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operation, None, True, [left, right_leaf], left.nullable and right_leaf.nullable)

            self.nodes += [right_leaf, root]
            return root
        
        elif not isinstance(left, Leaf) and isinstance(right, Leaf):
            id_left = None
            if left != epsilon:
                id_left = self.getNodeID()
            
            left_leaf = Leaf(left, id_left, False, [], False)
            root = Leaf(operation, None, True, [left_leaf, right], left_leaf.nullable and right.nullable)

            self.nodes += [left_leaf, root]
            return root

    def opOrder(self, op1, op2):
        precedences = {'|' : 0, '.' : 1, '*' : 2}
        return precedences[op1] >= precedences[op2]
    
    def trigerTree(self, expression):
        values = []
        operations = []
        for token in expression:
            if self.checkSymbol(token):
                values.append(token)

            elif token == '(':
                operations.append(token)

            elif token == ')':
                top = self.last(operations)

                while top is not None and top != '(':
                    root = self.doOperation(operations, values)
                    values.append(root)
                    top = self.last(operations)
                operations.pop()

            else:
                top = self.last(operations)

                while top is not None and top not in '()' and self.opOrder(top, token):
                    root = self.doOperation(operations, values)
                    values.append(root)
                    top = self.last(operations)
                operations.append(token)

        while self.last(operations) is not None:
            root = self.doOperation(operations, values)
            values.append(root)
        self.root = values.pop()