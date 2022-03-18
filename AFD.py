import functools
epsilon = 'ε'

class NodeDFA():
    def __init__(self, value, nodes, isDirect = False):
        self.value = value
        self.id = None
        self.conjunto_nodes = nodes
        self.transitions = []
        self.isMarked = False
        self.isFinal = False

        if not isDirect:
            self.CreateID(nodes)
        else:
            self.CreateID2(nodes)

    def CreateID(self, nodes):
        a = [n.id for n in nodes]
        a.sort()
        a = [str(i) for i in a]
        self.id = ', '.join(a)

    def CreateID2(self, nodes):
        a = [n for n in nodes]
        a.sort()
        a = [str(i) for i in a]
        self.id = ', '.join(a)

    def Mark(self):
        self.isMarked = True

    def isAcceptingState(self):
        self.isFinal = True

class DFA():
    def __init__(self, symbols, first_state, fin_state):
        self.states = []
        self.init_state = None
        self.acceptance_states = []
        self.transiciones = []
        self.symbols = symbols

        self.count = 0
        self.rounds = 1

        self.CreateDFA(first_state, fin_state)

    def simulateDFA(self, exp):
        S = self.init_state.value

        for e in exp:
            S = self.moveSimulation(S, e)

            if S == None:
                return 'no'

        if S in self.acceptance_states:
            return 'yes'
            
        return 'no'

    def CreateTransitionFunction(self):
        f = {}
        for t in self.transiciones:
            i, s, fi = [*t]

            if i not in f.keys():
                f[i] = {}
            f[i][s] = fi

        return f

    def GetStates(self):
        return {s.value for s in self.states}

    def GetAcceptingStates(self):
        return {s for s in self.acceptance_states}

    def CreateDFA(self, init, final):
        initial_state_DFA = self.e_closure([init])

        self.init_state = NodeDFA(self.GetName(), initial_state_DFA)
        self.states.append(self.init_state)

        if final.id in [c.id for c in initial_state_DFA]:
            self.init_state.isAcceptingState()
            self.acceptance_states.append(self.init_state.value)

        while not self.MarkedState():
            T = self.GetFirstUnmarkedState()
            T.Mark()

            for symbol in self.symbols:
                if symbol != epsilon:
                    move = self.Move(T.conjunto_nodes, symbol)

                    if len(move) > 0:
                        cerradura = self.e_closure(move)
                        U = NodeDFA(self.GetName(), cerradura)
                        
                        if U.id not in [s.id for s in self.states]:
                            if final.id in [c.id for c in cerradura]:
                                U.isAcceptingState()
                                self.acceptance_states.append(U.value)
                            self.states.append(U)
                            self.transiciones.append((T.value, symbol, U.value))
                        else:
                            self.count -= 1
                            for s in self.states:
                                if U.id == s.id:
                                    self.transiciones.append((T.value, symbol, s.value))
                            
    def GetName(self):
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

    def GetFirstUnmarkedState(self):
        for n in self.states:
            if not n.isMarked:
                return n
        
    def MarkedState(self):
        marks = [n.isMarked for n in self.states]
        return functools.reduce(lambda a, b: a and b, marks)

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

    def moveSimulation(self, Nodo, symbol):
        move = None
        for i in self.transiciones:
            if i[0] == Nodo and i[1] == symbol:
                move = i[2]

        return move