"""
automaton.py
Automaton logic and building for the Automaton program
Pablo Ruiz 18259 (PingMaster99)
"""

from dataStructures import State
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pylab
from dataStructures import DirectConstructionNode, shunting_yard_algorithm


class FiniteAutomaton(object):
    """
    Models finite automatons
    """

    def __init__(self, initial_state, acceptance_states, is_deterministic=False):
        self.initial_state = initial_state
        self.acceptance_states = acceptance_states
        self.states = []
        self.is_deterministic = is_deterministic

    # Epsilon closure for NFAs
    def epsilon_closure(self, state):
        """
        Epsilon closure for NFAs
        :param state: current state to validate
        :return: set with all states
        """
        # Create a new set, with state as its only member
        states = set()
        states.add(state)

        # Check if there are epsilon transitions to follow recursively
        if state.identifier1 == 'ε':
            if state.edge1 is not None:
                states |= self.epsilon_closure(state.edge1)
        if state.identifier2 == 'ε':
            if state.edge2 is not None:
                states |= self.epsilon_closure(state.edge2)

        # Returns the set of states
        return states

    # Generates a list with all tokens according to an input string
    def match_tokens(self, string):
        """
        Matches an input string and generates tokens
        :param string: string to validate
        :return: if string is valid + tokens
        """
        current = set()
        next_states = set()
        tokens = []
        current_iterating_string = ''
        current_acceptance_string = ''

        # Initial state(s)
        current |= self.epsilon_closure(self.initial_state)

        while len(string) > 0:
            for character in string:
                current_iterating_string += character
                for c in current:
                    # If state has a transition with the current character
                    if c.identifier1 == character:
                        if self.is_deterministic:
                            next_states = {c.edge1}
                        else:
                            next_states |= self.epsilon_closure(c.edge1)
                    elif c.identifier2 == character:
                        if self.is_deterministic:
                            next_states = {c.edge2}
                        else:
                            next_states |= self.epsilon_closure(c.edge2)
                    elif self.is_deterministic:
                        break
                current = next_states
                next_states = set()

                for state in self.acceptance_states:
                    if state in current:
                        current_acceptance_string = current_iterating_string
                        break
            # If after iterating through the whole string we get an acceptance string
            if len(current_acceptance_string) > 0:
                tokens.append(current_acceptance_string)
                string = string[len(current_acceptance_string)::]
                current_iterating_string = ''
                current_acceptance_string = ''
                current = self.epsilon_closure(self.initial_state)
            # No acceptance strings
            else:
                tokens.append('INVALID EXPRESSION, Invalid tokens ->')
                tokens.append(string)
                return False, tokens

        if len(tokens) > 0:
            return True, tokens
        else:
            for state in self.acceptance_states:
                if state in current:
                    return True, tokens

        tokens.append('INVALID EXPRESSION, Invalid tokens ->')
        tokens.append(string)
        return False, tokens

    def display(self):
        """
        Displays an automaton (graphically)
        """
        graph = nx.DiGraph()
        color_map = []
        acceptance_states = []
        for state in self.states:
            if state.edge1 is not None:
                graph.add_edges_from([(state.state_number, state.edge1.state_number)], label=state.identifier1)

            if state.edge2 is not None:
                graph.add_edges_from([(state.state_number, state.edge2.state_number)], label=state.identifier2)

            if state.is_acceptance:
                acceptance_states.append(state.state_number)

        for node in graph:
            if node in acceptance_states:
                color_map.append('green')
            else:
                color_map.append('gray')

        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, node_size=1500, with_labels=True, node_color=color_map,
                connectionstyle='arc3, rad=0.07',
                alpha=0.7, font_size=10)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=nx.get_edge_attributes(graph, 'label'), label_pos=0.7,
                                     bbox=None, horizontalalignment='left',
                                     verticalalignment='baseline')
        pylab.show()


class AutomatonGeneration(object):
    """
    Generates automatons
    """

    def generate_thompson_nfa(self, regexp):
        """
        Generates an NFA from a regexp with the Thompson Algorithm
        Inspired by niemaattarian
        :param regexp: regular expression
        :return: NFA
        """
        postfix = shunting_yard_algorithm(regexp)
        nfa_stack = []
        states = []
        state_number = 0

        # Looping through the postfix expression
        for c in postfix:
            # Kleene base automaton
            if c == '*':
                nfa1 = nfa_stack.pop()
                # New initial and acceptance states
                initial, accept = State(state_number), State(state_number + 1)
                state_number += 2
                states.append(initial)
                states.append(accept)
                # We join the automaton
                initial.edge1, initial.edge2 = nfa1.initial_state, accept
                initial.identifier1 = 'ε'
                initial.identifier2 = 'ε'
                # Join old accept state to the new accept state and NFA's initial state
                nfa1.acceptance_states.edge1, nfa1.acceptance_states.edge2 = nfa1.initial_state, accept
                nfa1.acceptance_states.identifier1 = 'ε'
                nfa1.acceptance_states.identifier2 = 'ε'
                # NFA foes back into the stack
                nfa_stack.append(FiniteAutomaton(initial, accept))
            # Concatenation
            elif c == '.':
                nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
                # Automatons are merged
                nfa1.acceptance_states.edge1 = nfa2.initial_state
                nfa1.acceptance_states.identifier1 = 'ε'
                nfa_stack.append(FiniteAutomaton(nfa1.initial_state, nfa2.acceptance_states))
            # Or
            elif c == '|':
                # Popping the stack
                nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
                # Initial state
                initial = State(state_number)
                initial.edge1, initial.edge2 = nfa1.initial_state, nfa2.initial_state
                initial.identifier1 = 'ε'
                initial.identifier2 = 'ε'
                # Acceptance state
                accept = State(state_number + 1)
                state_number += 2
                states.append(initial)
                states.append(accept)
                # Acceptance state is connected
                nfa1.acceptance_states.edge1, nfa2.acceptance_states.edge1 = accept, accept
                nfa1.acceptance_states.identifier1 = 'ε'
                nfa2.acceptance_states.identifier1 = 'ε'
                nfa_stack.append(FiniteAutomaton(initial, accept))
            # Positive closure
            elif c == '+':
                nfa1 = nfa_stack.pop()
                accept, initial = State(state_number), State(state_number + 1)
                state_number += 2
                states.append(initial)
                states.append(accept)
                # NFAs are joined
                initial.edge1 = nfa1.initial_state
                initial.identifier1 = 'ε'
                nfa1.acceptance_states.edge1, nfa1.acceptance_states.edge2 = nfa1.initial_state, accept
                nfa1.acceptance_states.identifier1 = 'ε'
                nfa1.acceptance_states.identifier2 = 'ε'
                nfa_stack.append(FiniteAutomaton(initial, accept))
            else:
                # Base case for a or b literals
                accept, initial = State(state_number), State(state_number + 1)
                state_number += 2
                states.append(initial)
                states.append(accept)
                # Character joins the states
                initial.identifier1, initial.edge1 = c, accept
                nfa_stack.append(FiniteAutomaton(initial, accept))

        # Once the stack is complete, we pop the finalized NFA and update its states
        final_nfa = nfa_stack.pop()
        states[states.index(final_nfa.acceptance_states)].is_acceptance = True
        states[states.index(final_nfa.initial_state)].is_initial = True
        states[states.index(final_nfa.initial_state)].state_number = '→' + states[
            states.index(final_nfa.initial_state)].state_number

        final_nfa.states = states
        final_nfa.acceptance_states = [states[states.index(final_nfa.acceptance_states)]]

        self.nfa = final_nfa
        return self.nfa

    @staticmethod
    def afd_conversion_transition(nfa, checking_state, character):
        """
        Checks for a move operation
        :param nfa: NFA
        :param checking_state: state to check
        :param character: character to check
        :return: state set
        """
        current_state_construction = set()
        for state in checking_state:
            if state.identifier1 == character:
                current_state_construction.add(state.edge1)
            if state.identifier2 == character:
                current_state_construction.add(state.edge2)
        final_state_construction = current_state_construction.copy()
        for construction_state in current_state_construction:
            final_state_construction |= nfa.epsilon_closure(construction_state)
        return final_state_construction

    def convert_to_dfa(self, nfa):
        """
        Converts an NFA to a DFA with the subset method
        :param nfa: NFA
        :return: DFA
        """
        unchecked_states = []
        dfa_states = []
        transitions = []

        unchecked_states.append(nfa.epsilon_closure(nfa.initial_state))
        # Building the subsets and transition table
        while len(unchecked_states) > 0:
            checking_state = unchecked_states.pop(0)
            if checking_state not in dfa_states:
                current_transitions = [None, None]
                dfa_states.append(checking_state)
                a_transition_set = self.afd_conversion_transition(nfa, checking_state, 'a')
                b_transition_set = self.afd_conversion_transition(nfa, checking_state, 'b')
                if a_transition_set not in dfa_states and len(a_transition_set) > 0:
                    if a_transition_set not in unchecked_states:
                        unchecked_states.append(a_transition_set)
                    current_transitions[0] = len(dfa_states) + unchecked_states.index(a_transition_set)
                elif len(a_transition_set) > 0:
                    current_transitions[0] = dfa_states.index(a_transition_set)

                if b_transition_set not in dfa_states and len(b_transition_set) > 0:
                    if b_transition_set not in unchecked_states:
                        unchecked_states.append(b_transition_set)
                    current_transitions[1] = len(dfa_states) + unchecked_states.index(b_transition_set)
                elif len(b_transition_set) > 0:
                    current_transitions[1] = dfa_states.index(b_transition_set)

                transitions.append(current_transitions)

        deterministic_finite_automaton = FiniteAutomaton(None, [], True)

        dfa_linked_states = [State(None) for i in range(len(transitions))]

        # Linking all states
        for dfa_state_number in range(len(transitions)):

            current_state = dfa_linked_states[dfa_state_number]
            a_transition, b_transition = transitions[dfa_state_number]
            current_state.state_number = dfa_state_number

            if a_transition is not None:
                current_state.identifier1 = 'a'
                current_state.edge1 = dfa_linked_states[a_transition]
            if b_transition is not None:
                current_state.identifier2 = 'b'
                current_state.edge2 = dfa_linked_states[b_transition]

            for state in dfa_states[dfa_state_number]:
                if state in nfa.acceptance_states:
                    current_state.is_acceptance = True
                    deterministic_finite_automaton.acceptance_states.append(current_state)

            if dfa_state_number == 0:
                current_state.is_initial = True
                deterministic_finite_automaton.initial_state = current_state

        # Instancing DFA
        deterministic_finite_automaton.states = dfa_linked_states
        deterministic_finite_automaton.is_deterministic = True
        return deterministic_finite_automaton

    @staticmethod
    def get_node(index, node_list):
        """
        Gets a node with an index
        :param index: index
        :param node_list: list of all nodes
        :return:
        """
        for node in node_list:
            if node.index == index:
                return node

    @staticmethod
    def get_transition_nodes(character, node_dictionary, current_node):
        """
        Gets all the transition nodes for direct construction table
        :param character: character to check
        :param node_dictionary: node dictionary table
        :param current_node: current node
        :return: node list with transition nodes
        """
        character_node_list = []

        for node in current_node:
            if node_dictionary[node][0] == character:
                for index in node_dictionary[node][1]:
                    character_node_list.append(index)

        return list(set(character_node_list))

    def direct_dfa_construction(self, regexp):
        """
        Constructs a DFA from a regular expression
        :param regexp: regular expression
        :return: DFA
        """
        syntactic_tree_node_list = []
        postfix_expression = shunting_yard_algorithm(regexp)
        postfix_expression.append('#')
        postfix_expression.append('.')
        operators = {'*': 4, '+': 3, '.': 2, '|': 1}
        nullable_characters = ['ε', '*']
        all_nodes = []
        current_character_index = 0

        # We build the tree and calculate first position, last position, and next position
        for character in postfix_expression:
            new_node = DirectConstructionNode(character=character)

            if character in nullable_characters:
                new_node.nullable = True

            if character not in operators:
                new_node.index = current_character_index
                if character != 'ε':
                    new_node.first_position = {current_character_index}
                    new_node.last_position = {current_character_index}
                else:
                    new_node.first_position = set([])
                    new_node.last_position = set([])
                current_character_index += 1

            elif character == '*' or character == '+':
                new_node.edge1 = syntactic_tree_node_list.pop()
                new_node.first_position = new_node.edge1.first_position.copy()
                new_node.last_position = new_node.edge1.last_position.copy()

                # Next position calculation
                for node in new_node.edge1.last_position:
                    node = self.get_node(node, all_nodes)
                    node.next_position |= new_node.edge1.first_position
            else:
                new_node.edge2 = syntactic_tree_node_list.pop()
                new_node.edge1 = syntactic_tree_node_list.pop()
                if character == '|':
                    new_node.nullable = new_node.edge1.nullable or new_node.edge2.nullable
                    new_node.first_position = new_node.edge1.first_position | new_node.edge2.first_position
                    new_node.last_position = new_node.edge1.last_position | new_node.edge2.last_position
                    new_node.next_position = new_node.first_position.copy()
                elif character == '.':
                    new_node.nullable = new_node.edge1.nullable and new_node.edge2.nullable
                    if new_node.nullable:
                        new_node.first_position = new_node.edge1.first_position | new_node.edge2.first_position
                        new_node.last_position = new_node.edge1.last_position | new_node.edge2.last_position
                    else:
                        new_node.first_position = new_node.edge1.first_position.copy()
                        new_node.last_position = new_node.edge2.last_position.copy()

                    # Next position calculation
                    for node in new_node.edge1.last_position:
                        node = self.get_node(node, all_nodes)
                        node.next_position |= new_node.edge2.first_position
            syntactic_tree_node_list.append(new_node)
            all_nodes.append(new_node)

        state_table = []

        # Build table with states
        for i in range(current_character_index):
            state_table.append(self.get_node(i, all_nodes))

        acceptance_index = len(state_table) - 1
        initial_index = 0
        unchecked_states = []
        dfa_states = []
        transitions = []
        state_dictionary = {}

        # We build the position list with next position function result
        for i in range(len(state_table)):
            current_state = state_table[i]
            position_list = []
            for index in current_state.next_position:
                position_list.append(index)

            state_dictionary[i] = [state_table[i].character, position_list]

        # Initial state
        for i in range(len(state_dictionary)):
            if 0 not in state_dictionary[i][1]:
                continue
            else:
                initial_index = i
                unchecked_states.append(state_dictionary[0][1])
                break

        if len(unchecked_states) <= 0:
            unchecked_states.append([0])

        # We build the DFA states from the next position dictionary
        while len(unchecked_states) > 0:
            current_node = unchecked_states.pop(0)
            if current_node not in dfa_states:
                current_transition = [None, None]
                dfa_states.append(current_node)
                a_transition = self.get_transition_nodes('a', state_dictionary, current_node)
                b_transition = self.get_transition_nodes('b', state_dictionary, current_node)
                if a_transition not in dfa_states and len(a_transition) > 0:
                    if a_transition not in unchecked_states:
                        unchecked_states.append(a_transition)
                    current_transition[0] = len(dfa_states) + unchecked_states.index(a_transition)
                elif len(a_transition) > 0:
                    current_transition[0] = dfa_states.index(a_transition)

                if b_transition not in dfa_states and len(b_transition) > 0:
                    if b_transition not in unchecked_states:
                        unchecked_states.append(b_transition)
                    current_transition[1] = len(dfa_states) + unchecked_states.index(b_transition)
                elif len(b_transition) > 0:
                    current_transition[1] = dfa_states.index(b_transition)
                transitions.append(current_transition)

        deterministic_finite_automaton = FiniteAutomaton(None, [], True)

        dfa_linked_states = [State(None) for i in range(len(transitions))]

        # States are linked
        for dfa_state_number in range(len(transitions)):
            current_state = dfa_linked_states[dfa_state_number]
            a_transition, b_transition = transitions[dfa_state_number]
            current_state.state_number = dfa_state_number

            if a_transition is not None:
                current_state.identifier1 = 'a'
                current_state.edge1 = dfa_linked_states[a_transition]
            if b_transition is not None:
                current_state.identifier2 = 'b'
                current_state.edge2 = dfa_linked_states[b_transition]

            for state in dfa_states[dfa_state_number]:
                if state == acceptance_index:
                    current_state.is_acceptance = True
                    deterministic_finite_automaton.acceptance_states.append(current_state)

            if dfa_state_number == initial_index:
                current_state.is_initial = True
                current_state.state_number = '→' + str(current_state.state_number)
                deterministic_finite_automaton.initial_state = current_state

        # DFA is returned
        deterministic_finite_automaton.states = dfa_linked_states
        return deterministic_finite_automaton
