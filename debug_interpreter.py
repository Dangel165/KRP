from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter

code = """
함수 합계(목록):
    보여줘(목록)
    반환 목록

변수 숫자들 = [1, 2, 3]
변수 결과 = 합계(숫자들)
보여줘(결과)
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()

# Add debug to call_function
original_call = interpreter.call_function

def debug_call(call):
    print(f"\n=== Calling function: {call.name} ===")
    print(f"Arguments: {call.arguments}")
    print(f"Variables before: {list(interpreter.variables.keys())}")
    result = original_call(call)
    print(f"Variables after: {list(interpreter.variables.keys())}")
    print(f"Result: {result}")
    return result

interpreter.call_function = debug_call

try:
    interpreter.execute(ast)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
