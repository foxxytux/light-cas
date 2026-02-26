import math

# --- TOKENIZER: Breaks string into math chunks ---
def tokenize(s):
    # Standardize inputs: handle powers, e, and the derivative shortcut (')
    s = s.replace(" ", "").replace("**", "^").replace("e^", "exp(").replace("'", ",x")
    s = s.replace("pi", "P").replace("PI", "P")
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isdigit(): # Handle numbers (integers and floats)
            v = ""
            while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                v += s[i]; i += 1
            tokens.append(('num', float(v) if '.' in v else int(v)))
        elif s[i].isalpha(): # Handle variables and functions
            v = ""
            while i < len(s) and s[i].isalpha():
                v += s[i]; i += 1
            if v == "P": tokens.append(('num', 3.1415926535)) # Constant Pi
            elif v == "e": tokens.append(('num', 2.7182818284)) # Constant e
            else: tokens.append(('var' if len(v) == 1 else 'fn', v))
        elif s[i] in "+-*/^(),": # Handle operators
            tokens.append(('op', s[i])); i += 1
        else: i += 1
    return tokens

# --- PARSER: Builds the math tree (Order of Operations) ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0
    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def eat(self, t=None):
        tok = self.peek(); self.pos += 1; return tok
    
    def parse_expr(self): # Handles + and -
        node = self.parse_term()
        while self.peek() and self.peek()[1] in "+-":
            op = self.eat()[1]; node = (op, node, self.parse_term())
        return node
        
    def parse_term(self): # Handles * and /
        node = self.parse_pow()
        while self.peek() and self.peek()[1] in "*/":
            op = self.eat()[1]; node = (op, node, self.parse_pow())
        return node
        
    def parse_pow(self): # Handles exponents ^
        node = self.parse_atom()
        if self.peek() and self.peek()[1] == "^":
            self.eat(); node = ("^", node, self.parse_pow())
        return node
        
    def parse_atom(self): # Handles numbers, vars, and functions
        tok = self.eat()
        if not tok: return ('num', 0)
        if tok[0] == 'fn': # Function call: fn(arg)
            self.eat(); arg = self.parse_expr()
            if self.peek() and self.peek()[1] == ')': self.eat()
            return (tok[1], arg, None)
        if tok[1] == '(': # Parentheses
            node = self.parse_expr()
            if self.peek() and self.peek()[1] == ')': self.eat()
            return node
        if tok[0] == 'num' or tok[0] == 'var':
            if tok[0] == 'num' and self.peek() and self.peek()[0] == 'var':
                return ('*', tok, self.eat()) # Implicit mult: 5x -> 5*x
            return tok
        return ('num', 0)

# --- DIFFERENTIATION: Symbolic math rules ---
def diff(e, v):
    if e[0] == 'num': return ('num', 0)
    if e[0] == 'var': return ('num', 1 if e[1] == v else 0)
    op, l, r = e
    if op == '+': return ('+', diff(l, v), diff(r, v))
    if op == '-': return ('-', diff(l, v), diff(r, v))
    if op == '*': return ('+', ('*', l, diff(r, v)), ('*', diff(l, v), r))
    if op == '/': return ('/', ('-', ('*', diff(l, v), r), ('*', l, diff(r, v))), ('^', r, ('num', 2)))
    if op == '^': # Power Rule & basic a^x
        if r[0] == 'num': return ('*', r, ('*', ('^', l, ('num', r[1]-1)), diff(l, v)))
        return ('*', e, ('ln', l, None))
    # Trig and Transcendental
    if op == 'ln': return ('*', ('/', ('num', 1), l), diff(l, v))
    if op == 'exp': return ('*', e, diff(l, v))
    if op == 'sqrt': return ('/', diff(l, v), ('*', ('num', 2), ('sqrt', l, None)))
    if op == 'sin': return ('*', ('cos', l, None), diff(l, v))
    if op == 'cos': return ('*', ('*', ('num', -1), ('sin', l, None)), diff(l, v))
    if op == 'tan': return ('/', diff(l, v), ('^', ('cos', l, None), ('num', 2)))
    if op == 'cot': return ('/', ('*', ('num', -1), diff(l, v)), ('^', ('sin', l, None), ('num', 2)))
    if op == 'atan': return ('/', diff(l, v), ('+', ('num', 1), ('^', l, ('num', 2))))
    return ('num', 0)

# --- SIMPLIFIER: Cleans up 1*x, x+0, etc. ---
def S(e):
    if e is None or e[0] in ('num', 'var'): return e
    op, l, r = e[0], S(e[1]), S(e[2]) if e[2] is not None else None
    
    if l[0] == 'num' and r and r[0] == 'num': # Constant Folding
        try:
            if op == '+': return ('num', l[1] + r[1])
            if op == '*': return ('num', l[1] * r[1])
        except: pass
    if op == '+':
        if l == ('num', 0): return r
        if r == ('num', 0): return l
    if op == '*':
        if l == ('num', 0) or r == ('num', 0): return ('num', 0)
        if l == ('num', 1): return r
        if r == ('num', 1): return l
    return (op, l, r)

# --- STRINGIFY: Converts math tree back to text ---
def to_s(e):
    if e is None: return ""
    if e[0] == 'num': 
        v = e[1]
        if v == 3.1415926535: return "pi"
        if v == 2.7182818284: return "e"
        return str(int(v) if v == int(v) else round(v, 4))
    if e[0] == 'var': return e[1]
    op, l, r = e
    if r is None: return op + "(" + to_s(l) + ")"
    ls, rs = to_s(l), to_s(r)
    if op in "+-": return "(" + ls + op + rs + ")"
    if op == '*': return ls + "*" + rs
    if op == '/': return ls + "/" + rs
    return ls + "^" + rs

# --- HISTORY & INTERFACE ---
history = []
def run_cas(text):
    try:
        raw = text.lower().strip()
        is_expand = raw.startswith("expand(")
        var = "x"
        if "," in raw:
            p = raw.split(",")
            expr = p[0].replace("diff(", "").strip()
            v_tmp = p[1].strip().replace(")", "")
            if v_tmp: var = v_tmp
        else: expr = raw[7:].rstrip(")") if is_expand else raw.replace("'", "")
        
        tree = Parser(tokenize(expr)).parse_expr()
        res = tree if is_expand else diff(tree, var)
        for _ in range(4): res = S(res)
        out = to_s(res)
        return out[1:-1] if out.startswith("(") and out.endswith(")") else out
    except: return "Syntax Error"

print("Light CAS Pro")
print("History: '..'=last, 'h'=list | Exit: 'q'")

while True:
    inp = input(">> ")
    if inp.lower() in ("q", "exit"): break
    if inp == "h": # Show history
        for i, h in enumerate(history): print(str(i)+": "+h)
        continue
    if inp == ".." and history: # Recall last
        inp = history[-1]; print(">> " + inp)
    
    if inp.strip():
        if not history or inp != history[-1]: history.append(inp)
        if len(history) > 10: history.pop(0)
        print("ans:", run_cas(inp))
