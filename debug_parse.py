from compiler.lexer import Lexer
from compiler.parser import Parser

code = """
함수 합계(목록):
    보여줘(목록)
    반환 목록

변수 숫자들 = [1, 2, 3]
변수 결과 = 합계(숫자들)
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

print("AST:")
for stmt in ast.statements:
    print(f"  {stmt}")
    if hasattr(stmt, 'parameters'):
        print(f"    Parameters: {stmt.parameters}")
    if hasattr(stmt, 'body'):
        print(f"    Body: {stmt.body}")
