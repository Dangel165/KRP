"""
KRP IDE (Korean Programming Language IDE)
Python IDLE 스타일의 GUI 개발 환경
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# 컴파일러 모듈 임포트 (llvmlite 없이도 작동하도록)
try:
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from compiler.interpreter import Interpreter
    INTERPRETER_AVAILABLE = True
except ImportError as e:
    INTERPRETER_AVAILABLE = False
    print(f"경고: 인터프리터 모듈 로드 실패: {e}")

try:
    from compiler.codegen import CodeGenerator
    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False
    print("경고: LLVM 모듈을 로드할 수 없습니다. LLVM 컴파일 기능이 비활성화됩니다.")
    print("인터프리터 모드는 정상 작동합니다.")
    print("LLVM 기능을 사용하려면 'install_dependencies.bat'를 실행하세요.")


class KoreanIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("KRP IDE v2.0")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.modified = False
        
        # 한국어 키워드
        self.keywords = ['변수', '함수', '만약', '아니면', '반복', '반환', '보여줘', '참', '거짓']
        
        self.create_menu()
        self.create_toolbar()
        self.create_editor()
        self.create_output()
        self.create_statusbar()
        
        # 시작 메시지
        if not INTERPRETER_AVAILABLE:
            self.output_text.insert('1.0', "오류: 컴파일러 모듈을 로드할 수 없습니다.\n", 'error')
            self.output_text.insert('end', "requirements.txt의 패키지를 설치하세요.\n", 'error')
        elif not LLVM_AVAILABLE:
            self.output_text.insert('1.0', "경고: LLVM 기능이 비활성화되었습니다.\n", 'warning')
            self.output_text.insert('end', "인터프리터 모드만 사용 가능합니다.\n", 'warning')
            self.output_text.insert('end', "LLVM 기능을 사용하려면 'install_dependencies.bat'를 실행하세요.\n\n", 'info')
        else:
            self.output_text.insert('1.0', "KRP IDE에 오신 것을 환영합니다!\n", 'success')
            self.output_text.insert('end', "F5: 빠른 실행 (인터프리터) | F6: LLVM 컴파일\n\n", 'info')
        
        # 키 바인딩
        self.editor_text.bind('<KeyRelease>', self.on_key_release)
        self.editor_text.bind('<Key>', self.on_text_change)
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<F6>', lambda e: self.compile_code())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.find_text())
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="새 파일 (Ctrl+N)", command=self.new_file)
        file_menu.add_command(label="열기 (Ctrl+O)", command=self.open_file)
        file_menu.add_command(label="저장 (Ctrl+S)", command=self.save_file)
        file_menu.add_command(label="다른 이름으로 저장", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.quit_app)
        
        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="편집", menu=edit_menu)
        edit_menu.add_command(label="실행 취소 (Ctrl+Z)", command=lambda: self.editor_text.edit_undo())
        edit_menu.add_command(label="다시 실행 (Ctrl+Y)", command=lambda: self.editor_text.edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="찾기 (Ctrl+F)", command=self.find_text)
        
        # 실행 메뉴
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="실행", menu=run_menu)
        run_menu.add_command(label="빠른 실행 (F5)", command=self.run_code)
        if LLVM_AVAILABLE:
            run_menu.add_command(label="LLVM 컴파일 (F6)", command=self.compile_code)
        
        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="보기", menu=view_menu)
        view_menu.add_command(label="글꼴 크게", command=lambda: self.change_font_size(2))
        view_menu.add_command(label="글꼴 작게", command=lambda: self.change_font_size(-2))
        view_menu.add_command(label="출력 창 지우기", command=self.clear_output)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="문법 가이드", command=self.show_syntax_guide)
        help_menu.add_command(label="예제 코드", command=self.show_examples)
        help_menu.add_command(label="정보", command=self.show_about)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="새 파일", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="열기", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="저장", command=self.save_file).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(toolbar, text="▶ 실행 (F5)", command=self.run_code).pack(side=tk.LEFT, padx=2)
        if LLVM_AVAILABLE:
            ttk.Button(toolbar, text="⚙ 컴파일 (F6)", command=self.compile_code).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(toolbar, text="찾기", command=self.find_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="출력 지우기", command=self.clear_output).pack(side=tk.LEFT, padx=2)
    
    def create_editor(self):
        # 에디터 프레임
        editor_frame = ttk.Frame(self.root)
        editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 줄 번호 표시
        self.line_numbers = tk.Text(editor_frame, width=4, padx=5, takefocus=0,
                                     border=0, background='lightgray', state='disabled',
                                     wrap='none', font=('Consolas', 11))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # 에디터
        self.editor_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE,
                                                      font=('Consolas', 11),
                                                      undo=True, maxundo=-1)
        self.editor_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 구문 강조 태그 설정
        self.editor_text.tag_config('keyword', foreground='blue', font=('Consolas', 11, 'bold'))
        self.editor_text.tag_config('string', foreground='green')
        self.editor_text.tag_config('comment', foreground='gray', font=('Consolas', 11, 'italic'))
        self.editor_text.tag_config('number', foreground='purple')
        
        # 스크롤 동기화
        self.editor_text.config(yscrollcommand=self.on_editor_scroll)
    
    def create_output(self):
        # 출력 프레임
        output_frame = ttk.LabelFrame(self.root, text="출력", padding=5)
        output_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10,
                                                      font=('Consolas', 10),
                                                      wrap=tk.WORD, state='normal')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 출력 태그 설정
        self.output_text.tag_config('success', foreground='green')
        self.output_text.tag_config('error', foreground='red')
        self.output_text.tag_config('warning', foreground='orange')
        self.output_text.tag_config('info', foreground='blue')
    
    def create_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="줄: 1, 열: 1", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_editor_scroll(self, *args):
        # 줄 번호 스크롤 동기화
        self.line_numbers.yview_moveto(args[0])
        self.editor_text.yview_moveto(args[0])
    
    def update_line_numbers(self):
        # 줄 번호 업데이트
        line_count = self.editor_text.get('1.0', 'end-1c').count('\n') + 1
        line_numbers_string = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
    
    def on_key_release(self, event=None):
        # 구문 강조는 타이머로 지연 실행 (타이핑 중 렉 방지)
        if hasattr(self, '_highlight_timer'):
            self.root.after_cancel(self._highlight_timer)
        self._highlight_timer = self.root.after(300, self.highlight_syntax)
        
        self.update_line_numbers()
        self.update_cursor_position()
    
    def on_text_change(self, event=None):
        self.modified = True
        self.update_title()
    
    def update_cursor_position(self):
        # 커서 위치 업데이트
        cursor_pos = self.editor_text.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.statusbar.config(text=f"줄: {line}, 열: {int(col)+1}")
    
    def update_title(self):
        # 제목 업데이트
        title = "KRP IDE v2.0"
        if self.current_file:
            title += f" - {self.current_file}"
        if self.modified:
            title += " *"
        self.root.title(title)
    
    def highlight_syntax(self):
        # 성능 최적화: 보이는 영역만 강조
        # 모든 태그 제거
        for tag in ['keyword', 'string', 'comment', 'number']:
            self.editor_text.tag_remove(tag, '1.0', 'end')
        
        # 현재 보이는 영역만 가져오기 (성능 향상)
        try:
            first_visible = self.editor_text.index("@0,0")
            last_visible = self.editor_text.index(f"@0,{self.editor_text.winfo_height()}")
            
            # 여유를 두고 앞뒤 10줄씩 더 포함
            first_line = max(1, int(first_visible.split('.')[0]) - 10)
            last_line = int(last_visible.split('.')[0]) + 10
            
            start_idx = f"{first_line}.0"
            end_idx = f"{last_line}.end"
            
            content = self.editor_text.get(start_idx, end_idx)
            
            # 키워드 강조 (최적화된 방식)
            for keyword in self.keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, content):
                    match_start = f"{first_line}.0+{match.start()}c"
                    match_end = f"{first_line}.0+{match.end()}c"
                    self.editor_text.tag_add('keyword', match_start, match_end)
            
            # 문자열 강조
            for match in re.finditer(r'"[^"]*"', content):
                match_start = f"{first_line}.0+{match.start()}c"
                match_end = f"{first_line}.0+{match.end()}c"
                self.editor_text.tag_add('string', match_start, match_end)
            
            # 주석 강조
            for match in re.finditer(r'#.*$', content, re.MULTILINE):
                match_start = f"{first_line}.0+{match.start()}c"
                match_end = f"{first_line}.0+{match.end()}c"
                self.editor_text.tag_add('comment', match_start, match_end)
            
            # 숫자 강조
            for match in re.finditer(r'\b\d+\.?\d*\b', content):
                match_start = f"{first_line}.0+{match.start()}c"
                match_end = f"{first_line}.0+{match.end()}c"
                self.editor_text.tag_add('number', match_start, match_end)
        except:
            # 에러 발생 시 전체 강조 (폴백)
            pass
    
    def new_file(self):
        if self.modified:
            response = messagebox.askyesnocancel("저장", "변경사항을 저장하시겠습니까?")
            if response is None:
                return
            elif response:
                self.save_file()
        
        self.editor_text.delete('1.0', 'end')
        self.current_file = None
        self.modified = False
        self.update_title()
        self.update_line_numbers()
    
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="파일 열기",
            filetypes=[("한글 파일", "*.한글"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor_text.delete('1.0', 'end')
                self.editor_text.insert('1.0', content)
                self.current_file = filename
                self.modified = False
                self.update_title()
                self.highlight_syntax()
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("오류", f"파일을 열 수 없습니다:\n{e}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.editor_text.get('1.0', 'end-1c')
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.modified = False
                self.update_title()
                self.output_text.insert('end', f"파일 저장됨: {self.current_file}\n", 'success')
            except Exception as e:
                messagebox.showerror("오류", f"파일을 저장할 수 없습니다:\n{e}")
        else:
            self.save_as()
    
    def save_as(self):
        filename = filedialog.asksaveasfilename(
            title="다른 이름으로 저장",
            defaultextension=".한글",
            filetypes=[("한글 파일", "*.한글"), ("모든 파일", "*.*")]
        )
        
        if filename:
            self.current_file = filename
            self.save_file()
    
    def run_code(self):
        if not INTERPRETER_AVAILABLE:
            messagebox.showerror("오류", "인터프리터를 사용할 수 없습니다.\nrequirements.txt의 패키지를 설치하세요.")
            return
        
        code = self.editor_text.get('1.0', 'end-1c')
        
        self.output_text.insert('end', "=" * 50 + "\n")
        self.output_text.insert('end', "실행 중...\n", 'info')
        self.output_text.insert('end', "=" * 50 + "\n")
        
        try:
            # 출력 캡처
            output_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                
                parser = Parser(tokens)
                ast = parser.parse()
                
                interpreter = Interpreter()
                interpreter.execute(ast)
            
            # 출력 표시
            output = output_buffer.getvalue()
            if output:
                self.output_text.insert('end', output)
            
            self.output_text.insert('end', "\n실행 완료!\n", 'success')
        
        except Exception as e:
            self.output_text.insert('end', f"\n오류 발생:\n{str(e)}\n", 'error')
        
        self.output_text.see('end')
    
    def compile_code(self):
        if not LLVM_AVAILABLE:
            messagebox.showwarning("경고", 
                "LLVM 컴파일 기능을 사용할 수 없습니다.\n\n"
                "'install_dependencies.bat'를 실행하여 llvmlite를 설치하세요.\n\n"
                "인터프리터 모드(F5)는 정상 작동합니다.")
            return
        
        code = self.editor_text.get('1.0', 'end-1c')
        
        self.output_text.insert('end', "=" * 50 + "\n")
        self.output_text.insert('end', "LLVM 컴파일 중...\n", 'info')
        self.output_text.insert('end', "=" * 50 + "\n")
        
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            codegen = CodeGenerator()
            llvm_ir = codegen.generate(ast)
            
            self.output_text.insert('end', "LLVM IR 생성 완료!\n\n", 'success')
            self.output_text.insert('end', "생성된 LLVM IR:\n", 'info')
            self.output_text.insert('end', llvm_ir + "\n")
        
        except Exception as e:
            self.output_text.insert('end', f"\n컴파일 오류:\n{str(e)}\n", 'error')
        
        self.output_text.see('end')
    
    def find_text(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("찾기")
        search_window.geometry("400x100")
        
        ttk.Label(search_window, text="찾을 텍스트:").pack(pady=10)
        search_entry = ttk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        def do_search():
            search_text = search_entry.get()
            if search_text:
                start_pos = self.editor_text.search(search_text, tk.INSERT, stopindex='end')
                if start_pos:
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    self.editor_text.tag_remove('sel', '1.0', 'end')
                    self.editor_text.tag_add('sel', start_pos, end_pos)
                    self.editor_text.mark_set(tk.INSERT, end_pos)
                    self.editor_text.see(start_pos)
                else:
                    messagebox.showinfo("찾기", "텍스트를 찾을 수 없습니다.")
        
        ttk.Button(search_window, text="찾기", command=do_search).pack(pady=10)
        search_entry.bind('<Return>', lambda e: do_search())
    
    def change_font_size(self, delta):
        current_font = self.editor_text.cget('font')
        if isinstance(current_font, str):
            font_family = 'Consolas'
            font_size = 11
        else:
            font_family = current_font[0]
            font_size = current_font[1]
        
        new_size = max(8, min(24, font_size + delta))
        self.editor_text.config(font=(font_family, new_size))
        self.line_numbers.config(font=(font_family, new_size))
    
    def clear_output(self):
        self.output_text.delete('1.0', 'end')
    
    def show_syntax_guide(self):
        guide = """
KRP 문법 가이드

1. 변수 선언
   변수 이름 = 값

2. 함수 정의
   함수 함수이름(매개변수1, 매개변수2):
       # 함수 본문
       반환 값

3. 조건문
   만약 조건:
       # 참일 때 실행
   아니면:
       # 거짓일 때 실행

4. 반복문
   반복 조건:
       # 반복 실행

5. 출력
   보여줘(값)

6. 주석
   # 이것은 주석입니다

예제:
변수 숫자 = 10
보여줘(숫자)

함수 더하기(a, b):
    반환 a + b

변수 결과 = 더하기(5, 3)
보여줘(결과)
"""
        messagebox.showinfo("문법 가이드", guide)
    
    def show_examples(self):
        examples_window = tk.Toplevel(self.root)
        examples_window.title("예제 코드")
        examples_window.geometry("600x400")
        
        examples_text = scrolledtext.ScrolledText(examples_window, wrap=tk.WORD, font=('Consolas', 10))
        examples_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        examples = """
# 예제 1: Hello World
보여줘("안녕하세요, 세계!")

# 예제 2: 변수와 연산
변수 a = 10
변수 b = 20
변수 합 = a + b
보여줘(합)

# 예제 3: 조건문
변수 나이 = 18
만약 나이 >= 18:
    보여줘("성인입니다")
아니면:
    보여줘("미성년자입니다")

# 예제 4: 반복문
변수 i = 1
반복 i <= 5:
    보여줘(i)
    변수 i = i + 1

# 예제 5: 함수
함수 피보나치(n):
    만약 n <= 1:
        반환 n
    아니면:
        반환 피보나치(n-1) + 피보나치(n-2)

변수 결과 = 피보나치(10)
보여줘(결과)
"""
        examples_text.insert('1.0', examples)
        examples_text.config(state='disabled')
    
    def show_about(self):
        about_text = f"""
KRP IDE v2.0

KRP (Korean Programming Language)
Python으로 작성된 한국어 기반 프로그래밍 언어

기능:
- 한국어 키워드 지원
- 구문 강조
- 인터프리터 실행 (F5)
{"- LLVM 컴파일 (F6)" if LLVM_AVAILABLE else "- LLVM 컴파일 (비활성화 - llvmlite 필요)"}
- 파일 저장/불러오기

단축키:
- Ctrl+N: 새 파일
- Ctrl+O: 파일 열기
- Ctrl+S: 파일 저장
- Ctrl+F: 찾기
- F5: 빠른 실행
{"- F6: LLVM 컴파일" if LLVM_AVAILABLE else ""}

상태:
- 인터프리터: {"사용 가능" if INTERPRETER_AVAILABLE else "사용 불가"}
- LLVM 컴파일: {"사용 가능" if LLVM_AVAILABLE else "사용 불가 (install_dependencies.bat 실행 필요)"}
"""
        messagebox.showinfo("정보", about_text)
    
    def quit_app(self):
        if self.modified:
            response = messagebox.askyesnocancel("종료", "변경사항을 저장하시겠습니까?")
            if response is None:
                return
            elif response:
                self.save_file()
        
        self.root.quit()


def main():
    root = tk.Tk()
    app = KoreanIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
