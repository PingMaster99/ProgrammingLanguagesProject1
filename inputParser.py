"""
inputParser.py
Parses inputs for the Automaton program
Pablo Ruiz 18259 (PingMaster99)
"""


class InputParser(object):
    def __init__(self, menu_text):
        self.menu_text = menu_text

    def print_menu(self):
        print(self.menu_text)

    @staticmethod
    def capture_input(input_prompt):
        user_input = input(input_prompt + '\n>>').lower()
        return user_input

    def capture_numeric_input(self, input_prompt, error_message, number_range_inclusive=None):
        while True:
            user_input = self.capture_input(input_prompt)
            try:
                user_input = int(user_input)
                if number_range_inclusive is not None:
                    if user_input > number_range_inclusive[1] or user_input < number_range_inclusive[0]:
                        print(f"Número introducido fuera de rango {number_range_inclusive[0]} - "
                              f"{number_range_inclusive[1]}")
                break
            except ValueError:
                print(error_message)
                continue
        return user_input

    def capture_regex_input(self, input_prompt):
        while True:
            user_input = self.capture_input(input_prompt)
            valid, message = self.validate_regex(user_input)
            if valid:
                return user_input
            else:
                print(message)

    def capture_simulation_string_input(self, input_prompt):
        while True:
            user_input = self.capture_input(input_prompt)
            valid, message = self.validate_simulation_string(user_input)
            if valid:
                return user_input
            else:
                print(message)

    def validate_simulation_string(self, string):
        for character in string:
            if character != 'a' and character != 'b':
                return False, "Recuerde que debe introducir solo caracteres 'a' y 'b'"
        return True, ''

    def validate_regex(self, regex):
        valid_characters = ['.', '+', '*', '|', 'a', 'b', '(', ')']
        invalid_constructions = ['ab', 'ba', '*a', '*b', '+a', '+b', 'bb', 'aa', '..', '||']
        character_index = 0

        for character in regex:
            if character not in valid_characters:
                return False, f'Caracter inválido en la posición {character_index} de la expresión regular'
            character_index += 1

        if any(invalid_string in regex for invalid_string in invalid_constructions):
            return False, 'Construcción inválida detectada, recuerde incluir puntos para la concatenación'

        if regex.count('(') != regex.count(')'):
            return False, 'La cuenta de paréntesis de apertura no es igual a la cuenta de paréntesis de cerradura'

        return True, ''

