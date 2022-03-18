"""
dataStructures.py
Data structures used in the program (states, nodes, trees)
Pablo Ruiz 18259 (PingMaster99)
"""


class Node(object):
    """
    Node superclass
    """
    def __init__(self, identifier1=None, identifier2=None, edge1=None, edge2=None):
        self.identifier1 = identifier1
        self.identifier2 = identifier2
        self.edge1 = edge1
        self.edge2 = edge2


class SyntacticTree(object):
    """
    Syntactic tree
    """
    def __init__(self, root=None):
        self.root = root


class DirectConstructionNode(Node):
    """
    Nodes for direct construction
    """
    def __init__(self, index=None, character=None, first_position=None, last_position=None, nullable=False):
        super().__init__()
        self.index = index
        self.character = character
        self.nullable = nullable
        self.first_position = first_position
        self.last_position = last_position
        self.next_position = set([])


class State(Node):
    """
    Automata states
    """
    def __init__(self, state_number):
        super().__init__()
        self.state_number = str(state_number)
        self.is_initial = False
        self.is_acceptance = False


# Based on: https://github.com/niemaattarian/Thompsons-Construction-on-NFAs/blob/master/Project.py
def shunting_yard_algorithm(infix):
    """
    Generates a postfix expression from an infix one
    :param infix: infix
    :return: postfix
    """
    # Precedence of operators (higher = higher priority)
    operators = {'*': 4, '+': 3, '.': 2, '|': 1}

    postfix, stack = [], []

    # We iterate through all characters
    for character in infix:
        if character == '(':
            stack.append(character)

        # Parenthesis check
        elif character == ')':
            while stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()  # Removal of the opening bracket
        # Determine whether the character is in the 'operators' dictionary
        elif character in operators:
            while stack and operators.get(character, 0) <= operators.get(stack[-1], 0):
                postfix.append(stack.pop())
            stack.append(character)  # We check for operator precedence
        else:
            # Character is appended to postfix
            postfix.append(character)

    # We append to the postfix the ordered stack
    while stack:
        postfix.append(stack.pop())

    # returns postfix argument
    return postfix
