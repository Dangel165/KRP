#!/usr/bin/env python3
"""
KRP (Korean Programming Language) - 메인 실행 파일
"""

import sys
import argparse
from pathlib import Path
from compiler import Lexer, Parser, CodeGenerator

def compile_file(input_file: str, output_file: str = None, show_ir: bool = False):
    """한국어 소스 파일을 컴파일"""
    
    # 소스 코드 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        # 렉싱
        print(f"[1/4] 렉싱 중...")
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if show_ir:
            print("\n=== 토큰 ===")
            for token in tokens:
                print(f"  {token}")
        
        # 파싱
        print(f"[2/4] 파싱 중...")
        parser = Parser(tokens)
        ast = parser.parse()
        
        if show_ir:
            print("\n=== AST ===")
            print(f"  {ast}")
        
        # 코드 생성
        print(f"[3/4] LLVM IR 생성 중...")
        codegen = CodeGenerator()
        llvm_ir = codegen.generate(ast)
        
        if show_ir:
            print("\n=== LLVM IR ===")
            print(llvm_ir)
        
        # 최적화
        print(f"[4/4] 최적화 중...")
        optimized_ir = codegen.optimize()
        
        # 출력 파일 결정
        if output_file is None:
            output_file = Path(input_file).stem + '.o'
        
        # 오브젝트 파일 생성
        codegen.compile_to_object(output_file)
        
        print(f"\n✓ 컴파일 완료: {output_file}")
        print(f"  링크하려면: gcc {output_file} -o {Path(input_file).stem}")
        
    except Exception as e:
        print(f"\n✗ 컴파일 오류: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_repl():
    """대화형 모드 (REPL)"""
    print("KRP (Korean Programming Language) v2.0")
    print("종료하려면 '종료' 또는 Ctrl+C를 입력하세요.\n")
    
    codegen = CodeGenerator()
    
    while True:
        try:
            line = input(">>> ")
            
            if line.strip() in ['종료', 'exit', 'quit']:
                break
            
            if not line.strip():
                continue
            
            # 렉싱
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            
            # 파싱
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 실행 (간단한 인터프리터 모드)
            for stmt in ast.statements:
                codegen.generate_statement(stmt)
            
        except KeyboardInterrupt:
            print("\n종료합니다.")
            break
        except Exception as e:
            print(f"오류: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='KRP (Korean Programming Language) 컴파일러',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s program.한글              # 컴파일
  %(prog)s program.한글 -o output.o  # 출력 파일 지정
  %(prog)s program.한글 --show-ir    # LLVM IR 출력
  %(prog)s --repl                    # 대화형 모드
        """
    )
    
    parser.add_argument('input', nargs='?', help='입력 소스 파일')
    parser.add_argument('-o', '--output', help='출력 파일 이름')
    parser.add_argument('--show-ir', action='store_true', help='LLVM IR 출력')
    parser.add_argument('--repl', action='store_true', help='대화형 모드 시작')
    
    args = parser.parse_args()
    
    if args.repl:
        run_repl()
    elif args.input:
        compile_file(args.input, args.output, args.show_ir)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
