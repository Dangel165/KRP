"""
파서 테스트
"""

import sys
sys.path.insert(0, '..')

from compiler.lexer import Lexer
from compiler.parser import Parser, VarDeclaration, Number, String, BinaryOp

def test_var_declaration():
    source = "변수 x = 10\n"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], VarDeclaration)
    assert ast.statements[0].name == "x"
    assert isinstance(ast.statements[0].value, Number)
    assert ast.statements[0].value.value == 10

def test_expression():
    source = "변수 결과 = 10 + 20\n"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    var_decl = ast.statements[0]
    assert isinstance(var_decl.value, BinaryOp)
    assert var_decl.value.op == '+'

def test_string_var():
    source = '변수 이름 = "홍길동"\n'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    var_decl = ast.statements[0]
    assert isinstance(var_decl.value, String)
    assert var_decl.value.value == "홍길동"

if __name__ == '__main__':
    test_var_declaration()
    test_expression()
    test_string_var()
    print("✓ 모든 파서 테스트 통과!")
