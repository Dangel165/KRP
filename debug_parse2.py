from compiler.lexer import Lexer
from compiler.parser import Parser

code = open('test_function_params.한글', 'r', encoding='utf-8').read()
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

print(f'Total statements: {len(ast.statements)}')
for i, stmt in enumerate(ast.statements):
    name = stmt.name if hasattr(stmt, 'name') else ''
    print(f'{i}: {type(stmt).__name__} - {name}')
    if hasattr(stmt, 'body'):
        print(f'   Body: {len(stmt.body)} statements')
        for j, body_stmt in enumerate(stmt.body):
            print(f'     {j}: {type(body_stmt).__name__}')
