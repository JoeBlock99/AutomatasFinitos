import SyntaxTree
import AFN
import AFD
import utilities
from time import perf_counter

exp = input('Insert regular expression: ')
w = input('Insert chain: ')
print('\n')

try:
    print('\n====== Direct AFD ======')
    syntax = SyntaxTree.Tree(exp)

    states = {s.value for s in syntax.states}
    initial_state = syntax.init_state
    accepting_state = {s for s in syntax.acceptance_states}
    alphabet = {a for a in syntax.symbols}
    transition_function = syntax.doTransitions()
    alphabet, alphabet_print = utilities.getAlphabet(transition_function)

    start1 = perf_counter()
    response = syntax.simulateDFA(w)
    total_time = (perf_counter() - start1)

    print(f'Is chain {w} in {exp}?\nResponse: ', response)
    print('Time: %.8f secs' % total_time)

except:
    print('Direct AFD error.')


try:
    print('\n====== AFN ======')
    afn = AFN.NDFA(exp)

    states = afn.GetStates()
    initial_state = str(afn.init_state.id)
    accepting_state = {str(afn.final_state.id)}
    transition_function = afn.CreateTransitionFunction()
    alphabet, alphabet_print = utilities.getAlphabet(transition_function)

    start2 = perf_counter()
    response = afn.simulateNFA(w)
    total_time1 = (perf_counter() - start2)

    print(f'Is chain {w} in {exp}?\nResponse: ', response)
    print('Time %.8f secs' % total_time1)

except:
    print('AFN ERROR')

try:
    print('\n====== AFD ======')
    dfa = AFD.DFA([s for s in alphabet_print], afn.init_state, afn.final_state)

    states = dfa.GetStates()
    initial_state = dfa.init_state.value
    accepting_state = dfa.GetAcceptingStates()
    transition_function = dfa.CreateTransitionFunction()
    alphabet, alphabet_print = utilities.getAlphabet(transition_function)

    start3 = perf_counter()
    response = dfa.simulateDFA(w)
    total_time2 = (perf_counter() - start3)

    print(f'Is chain {w} in {exp}?\nResponse: ', response)
    print('Time %.8f secs' % total_time2)
    
except:
    print('AFD ERROR')