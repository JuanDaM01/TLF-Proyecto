import ast
import tokenize
import io
import os

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # 1. Find all docstring spans
    docstrings_spans = []
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node) is not None:
                    # node.body[0] is the Expr containing the docstring
                    doc_node = node.body[0]
                    docstrings_spans.append(((doc_node.lineno, doc_node.col_offset), (doc_node.end_lineno, doc_node.end_col_offset)))
    except Exception as e:
        print(f"AST parse error in {path}: {e}")
        
    # 2. Find all comment spans
    comments_spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source_code).readline):
            if tok.type == tokenize.COMMENT:
                comments_spans.append((tok.start, tok.end))
    except Exception as e:
        print(f"Tokenize error in {path}: {e}")
        
    spans_to_remove = docstrings_spans + comments_spans
    
    # 3. Filter characters
    lines = source_code.splitlines(True)
    out_lines = []
    
    for i, line in enumerate(lines):
        lineno = i + 1
        new_line = ""
        for col, char in enumerate(line):
            inside = False
            for (s_line, s_col), (e_line, e_col) in spans_to_remove:
                after_start = (lineno > s_line) or (lineno == s_line and col >= s_col)
                before_end = (lineno < e_line) or (lineno == e_line and col < e_col)
                
                if after_start and before_end:
                    inside = True
                    break
            if not inside:
                new_line += char
        out_lines.append(new_line)
        
    clean_code = "".join(out_lines)
    
    # 4. Remove empty lines that were left behind
    final_lines = []
    for line in clean_code.splitlines():
        if not line.strip():
            # Condense consecutive empty lines to a single one
            if not final_lines or not final_lines[-1].strip():
                continue
        final_lines.append(line)
        
    # Remove leading/trailing empty lines
    while final_lines and not final_lines[0].strip():
        final_lines.pop(0)
    while final_lines and not final_lines[-1].strip():
        final_lines.pop()
        
    final_code = "\n".join(final_lines) + "\n"
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(final_code)
    print(f"Cleaned {path}")

if __name__ == '__main__':
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith('.py') and name not in ('strip_comments.py', 'test_ast.py', 'strip.py'):
                clean_file(os.path.join(root, name))
