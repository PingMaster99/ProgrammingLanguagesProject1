"""
main.py
Main file for the Automaton program
Pablo Ruiz 18259 (PingMaster99)
"""

from automaton import AutomatonGeneration
from inputParser import InputParser

MENU = """
--------------------------
  PROGRAMA DE AUTÓMATAS
--------------------------
Seleccione una opción:
1. Construir un AFN por Thompson
2. Construir un AFD por subconjuntos a partir de AFN
3. Construir un AFD por una expresión regular
4. Simular un AFN
5. Simular un AFD
6. Salir
"""
input_parser = InputParser(MENU)
automaton_generator = AutomatonGeneration()


def match_automaton(automaton):
    simulation_string = input_parser.capture_simulation_string_input("Introduzca el token a evaluar")
    valid, tokens = automaton.match_tokens(simulation_string)
    print(f"La construcción es válida: {valid}\nTokens generados:\n")
    for token in tokens:
        print(token)


def print_automaton_generation():
    print("""
Se ha generado el autómata de forma exitosa! 
Recuerde que el estado de inicio tiene una flecha y los estados de aceptación se muestran en color verde.
Por favor vea la ventana auxiliar y ciérrela al finalizar. 
""")


def main():
    thompson_nfa = None
    thompson_regex = ''
    subset_dfa = None
    regex_dfa = None
    regex_dfa_regex = ''

    while True:
        input_parser.print_menu()
        selected_option = input_parser.capture_numeric_input("Introduzca la opción a realizar",
                                                             "ERROR: Introduzca un número del 1 al 6\n")
        if selected_option == 1:
            regex = input_parser.capture_regex_input("Introduzca la expresión regular para el AFN a generar")
            thompson_regex = regex
            thompson_nfa = automaton_generator.generate_thompson_nfa(regex)
            print_automaton_generation()
            thompson_nfa.display()
        elif selected_option == 2:
            if thompson_nfa is None:
                print("Vaya! No ha generado un AFN para convertir a AFD. Seleccione '1' para realizar esto\n")
                continue
            else:
                print(f"Generando AFD con el AFN ({thompson_regex}) guardado")
                subset_dfa = automaton_generator.convert_to_dfa(thompson_nfa)
                print_automaton_generation()
                subset_dfa.display()
        elif selected_option == 3:
            regex = input_parser.capture_regex_input("Introduzca la expresión regular para el AFN a generar")
            regex_dfa_regex = regex
            regex_dfa = automaton_generator.direct_dfa_construction(regex)
            print_automaton_generation()
            regex_dfa.display()

        elif selected_option == 4:
            if thompson_nfa is None:
                print("Vaya! No se ha detectado un AFN para simular, introduzca la opción '1' para construirlo")
                continue
            else:
                print(f"Puede simular el autómata con la expresión regular {thompson_regex}")
                match_automaton(thompson_nfa)


        elif selected_option == 5:
            if subset_dfa is None and regex_dfa is None:
                print(
                    "Vaya! No se han detectado autómatas deterministas para simular, puede usar las opciones '2' o '3' para generarlos")
                continue
            print("Los autómatas disponibles se muestran a continuación, ciérrelos para continuar")
            if subset_dfa is not None:
                print(f"Autómata por subconjuntos ({thompson_regex}) disponible!")
                if input_parser.capture_input("Introduzca '1' si desea utilizar este autómata") == '1':
                    match_automaton(subset_dfa)

            if regex_dfa is not None:
                print(f"Autómata por expresión regular ({regex_dfa_regex}) disponible!")
                if input_parser.capture_input("Introduzca '1' si desea utilizar este autómata") == '1':
                    match_automaton(regex_dfa)
        elif selected_option == 6:
            print("Gracias por haber utilizado el programa de autómatas, que tenga un feliz día!")
            break


if __name__ == '__main__':
    main()
