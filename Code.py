import sys
sys.path.insert(0, "../..")

f = open('ez.py', 'r+')
tabs = 0
if sys.version_info[0] >= 3:
    raw_input = input

#reserved = {
#    'press_start' : 'BLKST',
#    'game_over' : 'BLKEN'
#}

tokens = [ 'NAME', 'NUMBER', 'IF', 'ELSE', 'GTE', 'NEQ', 'EQ', 'LTE', 'WHILE', 'INFI', 'BLKST', 'BLKEN', 'DEF', 'CALL', 'AND', 'OR', 'INPUT', 'PRINT', 'BREAK', 'RET', 'COMMENT']    

literals = ['=', '+', '-', '*', '/', '(', ')', '>', '!', '<', '%']

# Tokens

# General

#I/O
t_PRINT = r'View'
t_INPUT = r'Accept'

#Relational
t_AND = r'VS'
t_OR = r'COOP'

# If/Else
t_IF = r'Good'
t_ELSE = r'Bad'

# Blocking
t_BLKST = r'PRESS_START'
t_BLKEN = r'GAME_OVER'

# Loops
t_WHILE = r'Spam'
t_INFI = r'Infinite'
t_BREAK = r'Shutdown'

# Functions
t_DEF = r'Quest'
t_CALL = r'Start_Quest'
t_RET = r'Reward'

# Inequalities
t_NEQ = r'!='
t_EQ = r'=='
t_GTE = r'>='
t_LTE = r'<='

#Variables
t_NAME = r'[a-z][a-zA-Z0-9_]*'
#t_COMMENT = r'[->][a-zA-Z0-9_]+'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Error at line %s: Illegal character '%s'" % (t.lexer.lineno, t.value[0]))
    quit()

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)

# dictionary of names
names = {}

def p_prog(p):
    'prog : statement'
    f.write(p[1])

# General
def p_ignore(p):
    'statement : COMMENT'
    p[0] = '# {}'.format(str(p[2]))

# Input/Output
def p_print(p):
    'statement : PRINT "(" expression ")"'
    global tabs
    p[0] = '\t'*tabs + 'print ({})\n'.format(str(p[3]))
    print p[0]

def p_input(p):
    'statement : INPUT "(" NAME ")"'
    global tabs
    p[0] = '\t'*tabs + '{} = input()\n'.format(str(p[3]))
    print p[0]
    
# Loops    
def p_while_mult(p):
    'statement : WHILE "(" expression ")"'
    p[0] = '\t'*tabs + 'while ({}): \n'.format(str(p[3]))
    print p[0]

def p_infinites(p):
    'statement : INFI'
    p[0] = '\t'*tabs + 'while(true):\n'.format(str(p[2]))

def p_break(p):
    'statement : BREAK'
    p[0] = '\t'*tabs + 'break\n'

# Block
def p_blk_start(p):
    'statement : BLKST'
    global tabs
    p[0] = ''
    tabs = tabs + 1

def p_blk_end(p):
    'statement : BLKEN'
    global tabs
    p[0] = ''
    tabs = tabs - 1

# If/Else
def p_if_statement(p):
    'statement : IF "(" expression ")" statement'
    p[0] = '\t'*tabs + 'if ({}): \n\t {}\n'.format(str(p[3]), str(p[5]))

def p_if_mult(p):
    'statement : IF "(" expression ")"'
    global tabs
    p[0] = '\t'*tabs + 'if ({}): \n'.format(str(p[3]))
    print p[0]

def p_else(p):
    'statement : ELSE'
    global tabs
    p[0] = '\t'*tabs + 'else:\n'
    print p[0]

# Assignments
def p_statement_assign(p):
    'statement : NAME "=" expression \n'
    global tabs
    p[0] = '\t'*tabs + '{} {} {}\n'.format(p[1], p[2], p[3])
    names[p[1]] = p[3]
    print p[0]

def p_statement_expr(p):
    'statement : expression'
    global tabs
    p[0] = '\t'*tabs + '{}'.format(str(p[1]))
    print p[0]

# Functions
def p_func_def_witharg(p):
    'statement : DEF NAME "(" NAME ")"\n'
    global tabs
    p[0] = '\t'*tabs + 'def {}({}):\n'.format(str(p[2]), (str(p[4])))
    print p[0]

def p_func_def_withoutarg(p):
    'statement : DEF NAME "(" ")"'
    global tabs
    p[0] = '\t'*tabs + 'def {}():\n'.format(str(p[2]))
    print p[0]

def p_func_call(p):
    'expression : CALL NAME "(" NAME ")"\n'
    p[0] = '\t'*tabs + '{}({})\n'.format(str(p[2]), (str(p[4])))
    print p[0]

def p_func_call_wo_args(p):
    'expression : CALL NAME "(" ")"\n'
    p[0] = '\t'*tabs + '{}()\n'.format(str(p[2]))
    print p[0]

def p_func_ret(p):
    'statement : RET "(" NAME ")"'
    p[0] = '\t'*tabs + 'return {}\n'.format(str(p[3]))
    print p[0]

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression '%' expression
                  | expression GTE expression
                  | expression LTE expression
                  | expression NEQ expression
                  | expression EQ expression
                  | expression '>' expression
                  | expression '<' expression
                  | expression AND expression
                  | expression OR expression'''
    p[0] = '{} {} {}'.format(p[1], p[2], p[3])


def p_expression_uminus(p): 
    "expression : '-' expression %prec UMINUS"
    p[0] = '-{}'.format(p[2])


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = '{}\n'.format(str(p[2]))


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = '{}'.format(str(p[1]))


def p_expression_name(p):
    "expression : NAME"
    p[0] = '{}'.format(str(p[1]))


def p_error(p):
    if p:
        print("Syntax error at line %s: '%s'" % (p.lexer.lineno, p.value))
        quit()
    else:
        print("Syntax error at EOF")


import ply.yacc as yacc
yacc.yacc()

while 1:
    print ("Input desired filename to compile file, type gg ez to run last compiled file.")
    i = raw_input()
    #Input file name with extension .cig to "compile"
    if (i.find(".cig") != -1):
        open("ez.py", 'w').close()
        f2 = open(i, 'r')
        for line in f2:
            try:
                s = line
            except EOFError:
                break
            if not s:
                continue
            yacc.parse(s)
        f = open("ez.py", 'r+')
        f.flush()
        f2.close()
    #Input gg ez to gg CiG program
    elif (i == "gg ez"):
        execfile("ez.py")
    #Quit()
    elif (i == "quit()"):
        exit()
    #error
    else:
        print ("Error no command '%s' found" % i)
