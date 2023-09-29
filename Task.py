import streamlit as st
import pandas as pd
from constraint import *
from simpleai.search import CspProblem, backtrack
import re

st.title("Cryptarithmetic puzzle solver:robot_face::jigsaw:")
st.caption('''
Created by Daan Michielsen
           ''')
st.header("Cryptarithmetic Puzzles", divider='violet')
st.write("Cryptarithmetic puzzles, also known as alphametics or verbal arithmetic, are a type of mathematical puzzle where letters are used to represent digits. The goal is to find the correct digit substitution for each letter to make the arithmetic equation valid.")

st.header("Example: SEND + MORE = MONEY", divider='violet')
st.write("One famous example of a cryptarithmetic puzzle is the equation SEND + MORE = MONEY. In this puzzle, each letter represents a unique digit from 0 to 9. The goal is to find the correct digit substitution that satisfies the equation.")

st.write("Here's one possible solution:")
st.code("#solution\n  9 5 6 7\n  1 0 8 5\n+--------\n1 0 6 5 2")

st.write("In this solution, S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2.")
st.header("Try it yourself!", divider='violet')
puzzle = st.text_input(label="Enter you cryptarithmetic puzzle :jigsaw:", max_chars=64, placeholder="ODD+ODD=EVEN", help="Longer words may take longer to solve")
st.caption('''
Any 3 words with any operator(+-*/)
           ''')
state = st.button(label="SOLVE PUZZLE!", on_click=None, type="primary", use_container_width=False)



if state:
    if re.search(r"[-/*+=]", puzzle):
        with st.spinner('Looking for solution...:crossed_fingers:'):
            st.write(f"finding solution for:")

            words_and_operators = re.findall(r'\b\w+\b|[+*/-]', puzzle)     #split words and operators and save in list
            words = []                                                      #list for words
            operators = []                                                  #list for operators
            letters = []                                                    #list for letters
            variables = ()                                                  #Tuple for the variables
            domains = {}                                                    #Dictionary for the domains

            

            for item in words_and_operators:                                #add words to word list, operators to operator list and distinct letters to letters list
                if item.isalnum():
                    words.append(item)
                    for letter in item:
                        if letter not in letters:
                            letters.append(letter)
                else:
                    operators.append(item)

            words_streamlit = words.copy()
            words_streamlit.insert(-1, f'{operators[0]}--------')
            for word in words_streamlit:
                st.text(word)


            starting_letters = set(word[0] for word in words)               #get letters that are at the start of the words
            for letter in letters:                                          #arrange domains for all variables
                if letter in starting_letters:
                    domains.update({letter: list(range(1, 10))})            #if letter is start of word allow values 1-10
                else:
                    domains.update({letter: list(range(0, 10))})            #else allow values 0-10

            variables = tuple(letters)                                      #Assign tuple of letters list to variables

            def constraint_unique(variables, values):                       #Constraint to see if all variables are unique
                return len(values) == len(set(values))
            
            def assemble_words(words, result):
                assembled_words = []
                for word in words:
                    assembled_word = ''.join(str(result[letter]) for letter in word)
                    assembled_words.append(assembled_word)
                return assembled_words
            
            def insert_operators(words, operators):
                result = []
                for i, word in enumerate(words):
                    result.append(word)
                    if i < len(operators):
                        result.append(operators[i])
                return result
            
            def create_dataframe(dictionary):
                keys = list(dictionary.keys())
                values = list(dictionary.values())
                headers = [f"Letter {i + 1}" for i in range(len(keys))]  # Assign "letter x" as the header for each column
                df = pd.DataFrame([keys, values], columns=headers)
                return df

            def constraint_add(variables, values):
                result_str = ''   
                equation = ''                                          #Create empty string for assembling the result into a result
                
                indexes_list = [[values[variables.index(letter)] for letter in word] for word in words] #list with indexes(in variables) for each letter of each word

                for i, word in enumerate(words[:-1]):                   #assemble operation as string e.g 655+655 for ODD+ODD
                    equation += ''.join(str(index) for index in indexes_list[i])
                    if i < len(words) - 2:
                        equation += operators[0]
                result_str = ''.join(str(index) for index in indexes_list[-1]) #Create result string e.g. 1310 for EVEN
                return eval(equation) == int(result_str)

            constraints = [                                                 #Define constraints
                ((variables), constraint_unique),
                ((variables), constraint_add)
            ]

            problem = CspProblem(variables, domains, constraints)           #Setup problem
            output = backtrack(problem)                                     #Backtrack the hell out of it!
            assembled_words = assemble_words(words, output)
            assembled_words.insert(-1, f'{operators[0]}--------')
            
            if len(output) > 0:
                df=create_dataframe(output)
                st.subheader(":green[Result]")
                st.balloons()
                st.success('Solution found!', icon="🥳")
                if len(operators) == 1:
                    for word in assembled_words:
                        st.text(word)
                else:
                    st.info('Result notation for multiple operators is not complete yet', icon='⚠️')
                st.dataframe(df, hide_index=True)
                state = False
            else:
                st.subheader(":red[No result found]")
                st.error('No solution found', icon="🤕")
                state = False
    else:
        st.warning("The entered puzzle does not contain at least one operator(+-*/), '=' and 3 words!")