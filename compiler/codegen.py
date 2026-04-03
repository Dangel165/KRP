"""
한국어 프로그래밍 언어 - 코드 생성기 (LLVM IR)
LLVM IR 생성 및 최적화
"""

from llvmlite import ir, binding
from compiler.parser import *

class CodeGenerator:
    def __init__(self):
        # LLVM 초기화
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        
        # 모듈 생성
        self.module = ir.Module(name="korean_lang_module")
        self.module.triple = binding.get_default_triple()
        
        # 빌더
        self.builder = None
        
        # 심볼 테이블
        self.variables = {}
        self.functions = {}
        
        # 타입 정의
        self.int_type = ir.IntType(64)
        self.float_type = ir.DoubleType()
        self.bool_type = ir.IntType(1)
        self.void_type = ir.VoidType()
        
        # 문자열 포인터 타입
        self.str_type = ir.IntType(8).as_pointer()
        
        # 내장 함수 선언
        self._declare_builtins()
    
    def _declare_builtins(self):
        # printf 선언
        printf_ty = ir.FunctionType(self.int_type, [self.str_type], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")
        
        # scanf 선언
        scanf_ty = ir.FunctionType(self.int_type, [self.str_type], var_arg=True)
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")
    
    def generate(self, ast: Program) -> str:
        # main 함수 생성
        main_ty = ir.FunctionType(self.int_type, [])
        main_func = ir.Function(self.module, main_ty, name="main")
        block = main_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        # 프로그램 본문 생성
        for statement in ast.statements:
            self.generate_statement(statement)
        
        # main 함수 종료
        self.builder.ret(ir.Constant(self.int_type, 0))
        
        return str(self.module)
    
    def generate_statement(self, node: ASTNode):
        if isinstance(node, VarDeclaration):
            return self.generate_var_declaration(node)
        elif isinstance(node, Assignment):
            return self.generate_assignment(node)
        elif isinstance(node, PrintStatement):
            return self.generate_print(node)
        elif isinstance(node, IfStatement):
            return self.generate_if(node)
        elif isinstance(node, WhileStatement):
            return self.generate_while(node)
        elif isinstance(node, FunctionDeclaration):
            return self.generate_function(node)
        elif isinstance(node, FunctionCall):
            return self.generate_function_call(node)
        elif isinstance(node, ReturnStatement):
            return self.generate_return(node)
    
    def generate_var_declaration(self, node: VarDeclaration):
        # 변수 할당 공간 생성
        value = self.generate_expression(node.value)
        var_ptr = self.builder.alloca(value.type, name=node.name)
        self.builder.store(value, var_ptr)
        self.variables[node.name] = var_ptr
        return var_ptr
    
    def generate_assignment(self, node: Assignment):
        value = self.generate_expression(node.value)
        if node.name in self.variables:
            var_ptr = self.variables[node.name]
            self.builder.store(value, var_ptr)
        else:
            raise NameError(f"Variable '{node.name}' not defined")
        return value
    
    def generate_print(self, node: PrintStatement):
        value = self.generate_expression(node.expression)
        
        # 타입에 따라 포맷 문자열 선택
        if value.type == self.int_type:
            fmt = "%lld\n\0"
        elif value.type == self.float_type:
            fmt = "%f\n\0"
        elif value.type == self.bool_type:
            # bool을 int로 변환
            value = self.builder.zext(value, self.int_type)
            fmt = "%lld\n\0"
        else:
            fmt = "%s\n\0"
        
        # 포맷 문자열을 전역 상수로 생성
        fmt_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), 
                              bytearray(fmt.encode("utf8")))
        global_fmt = ir.GlobalVariable(self.module, fmt_str.type, 
                                       name=f"fmt_{id(node)}")
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = fmt_str
        
        # printf 호출
        fmt_ptr = self.builder.bitcast(global_fmt, self.str_type)
        self.builder.call(self.printf, [fmt_ptr, value])
    
    def generate_if(self, node: IfStatement):
        condition = self.generate_expression(node.condition)
        
        # 블록 생성
        then_block = self.builder.function.append_basic_block("then")
        else_block = self.builder.function.append_basic_block("else") if node.else_block else None
        merge_block = self.builder.function.append_basic_block("merge")
        
        # 조건 분기
        if else_block:
            self.builder.cbranch(condition, then_block, else_block)
        else:
            self.builder.cbranch(condition, then_block, merge_block)
        
        # then 블록
        self.builder.position_at_end(then_block)
        for stmt in node.then_block:
            self.generate_statement(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
        
        # else 블록
        if else_block:
            self.builder.position_at_end(else_block)
            for stmt in node.else_block:
                self.generate_statement(stmt)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)
        
        # merge 블록
        self.builder.position_at_end(merge_block)
    
    def generate_while(self, node: WhileStatement):
        # 블록 생성
        cond_block = self.builder.function.append_basic_block("while_cond")
        body_block = self.builder.function.append_basic_block("while_body")
        end_block = self.builder.function.append_basic_block("while_end")
        
        # 조건 블록으로 점프
        self.builder.branch(cond_block)
        
        # 조건 블록
        self.builder.position_at_end(cond_block)
        condition = self.generate_expression(node.condition)
        self.builder.cbranch(condition, body_block, end_block)
        
        # 본문 블록
        self.builder.position_at_end(body_block)
        for stmt in node.body:
            self.generate_statement(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)
        
        # 종료 블록
        self.builder.position_at_end(end_block)
    
    def generate_function(self, node: FunctionDeclaration):
        # 함수 타입 생성 (일단 모든 파라미터를 int64로 가정)
        param_types = [self.int_type] * len(node.parameters)
        func_ty = ir.FunctionType(self.int_type, param_types)
        
        # 함수 생성
        func = ir.Function(self.module, func_ty, name=node.name)
        self.functions[node.name] = func
        
        # 함수 본문 블록
        block = func.append_basic_block(name="entry")
        old_builder = self.builder
        self.builder = ir.IRBuilder(block)
        
        # 파라미터 저장
        old_vars = self.variables.copy()
        for i, param_name in enumerate(node.parameters):
            param_ptr = self.builder.alloca(self.int_type, name=param_name)
            self.builder.store(func.args[i], param_ptr)
            self.variables[param_name] = param_ptr
        
        # 함수 본문 생성
        for stmt in node.body:
            self.generate_statement(stmt)
        
        # 명시적 return이 없으면 0 반환
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(self.int_type, 0))
        
        # 복원
        self.builder = old_builder
        self.variables = old_vars
        
        return func
    
    def generate_function_call(self, node: FunctionCall):
        if node.name not in self.functions:
            raise NameError(f"Function '{node.name}' not defined")
        
        func = self.functions[node.name]
        args = [self.generate_expression(arg) for arg in node.arguments]
        return self.builder.call(func, args)
    
    def generate_return(self, node: ReturnStatement):
        value = self.generate_expression(node.value)
        self.builder.ret(value)
    
    def generate_expression(self, node: ASTNode):
        if isinstance(node, Number):
            if isinstance(node.value, int):
                return ir.Constant(self.int_type, node.value)
            else:
                return ir.Constant(self.float_type, node.value)
        
        elif isinstance(node, Boolean):
            return ir.Constant(self.bool_type, 1 if node.value else 0)
        
        elif isinstance(node, String):
            # 문자열 상수 생성
            str_val = node.value + '\0'
            str_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(str_val)),
                                   bytearray(str_val.encode("utf8")))
            global_str = ir.GlobalVariable(self.module, str_const.type,
                                          name=f"str_{id(node)}")
            global_str.linkage = 'internal'
            global_str.global_constant = True
            global_str.initializer = str_const
            return self.builder.bitcast(global_str, self.str_type)
        
        elif isinstance(node, Identifier):
            if node.name in self.variables:
                var_ptr = self.variables[node.name]
                return self.builder.load(var_ptr, name=node.name)
            else:
                raise NameError(f"Variable '{node.name}' not defined")
        
        elif isinstance(node, BinaryOp):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            
            # 산술 연산
            if node.op == '+':
                if left.type == self.float_type or right.type == self.float_type:
                    return self.builder.fadd(left, right)
                return self.builder.add(left, right)
            elif node.op == '-':
                if left.type == self.float_type or right.type == self.float_type:
                    return self.builder.fsub(left, right)
                return self.builder.sub(left, right)
            elif node.op == '*':
                if left.type == self.float_type or right.type == self.float_type:
                    return self.builder.fmul(left, right)
                return self.builder.mul(left, right)
            elif node.op == '/':
                if left.type == self.float_type or right.type == self.float_type:
                    return self.builder.fdiv(left, right)
                return self.builder.sdiv(left, right)
            
            # 비교 연산
            elif node.op == '==':
                return self.builder.icmp_signed('==', left, right)
            elif node.op == '!=':
                return self.builder.icmp_signed('!=', left, right)
            elif node.op == '>':
                return self.builder.icmp_signed('>', left, right)
            elif node.op == '<':
                return self.builder.icmp_signed('<', left, right)
            elif node.op == '>=':
                return self.builder.icmp_signed('>=', left, right)
            elif node.op == '<=':
                return self.builder.icmp_signed('<=', left, right)
        
        elif isinstance(node, FunctionCall):
            return self.generate_function_call(node)
        
        raise ValueError(f"Unknown expression type: {type(node)}")
    
    def optimize(self):
        """LLVM 최적화 패스 실행"""
        pmb = binding.create_pass_manager_builder()
        pmb.opt_level = 2
        pm = binding.create_module_pass_manager()
        pmb.populate(pm)
        
        llvm_module = binding.parse_assembly(str(self.module))
        pm.run(llvm_module)
        
        return str(llvm_module)
    
    def compile_to_object(self, output_file: str):
        """오브젝트 파일로 컴파일"""
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        llvm_module = binding.parse_assembly(str(self.module))
        llvm_module.verify()
        
        with open(output_file, 'wb') as f:
            f.write(target_machine.emit_object(llvm_module))
