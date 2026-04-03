#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KRP 인터프리터 실행 스크립트
"""

import sys
import io

# Windows 콘솔 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter

def main():
    if len(sys.argv) < 2:
        print("사용법: python run_interpreter.py <파일.한글>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.execute(ast)
    
    except FileNotFoundError:
        print(f"오류: 파일 '{filename}'을(를) 찾을 수 없습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
