import os
import tokenize
import io

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    tokens = []
    tok_gen = tokenize.generate_tokens(io.StringIO(code).readline)
    
    try:
        prev_tok = None
        
        for tok in tok_gen:
            if tok.type == tokenize.COMMENT:
                continue
            
            # Keep the token
            tokens.append(tok)

        # Now let's remove docstrings. A docstring is a STRING token
        # that is not part of an assignment or expression. Usually it's alone on a line.
        # So it's preceded by INDENT or NEWLINE (or DEDENT) and followed by NEWLINE.
        filtered_tokens = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.type == tokenize.STRING and (tok.string.startswith('"""') or tok.string.startswith("'''")):
                # Check neighbors
                prev_type = tokens[i-1].type if i > 0 else tokenize.NEWLINE
                next_type = tokens[i+1].type if i < len(tokens)-1 else tokenize.NEWLINE
                
                # If it's a docstring, it's typically surrounded by NEWLINE, INDENT, or DEDENT
                if prev_type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.NL) and \
                   next_type in (tokenize.NEWLINE, tokenize.NL, tokenize.ENDMARKER):
                    i += 1
                    continue
            filtered_tokens.append(tok)
            i += 1
        
        out = tokenize.untokenize(filtered_tokens)
        
        # Clean up excessive empty lines
        clean_lines = []
        for line in out.splitlines():
            if not line.strip():
                if not clean_lines or not clean_lines[-1].strip():
                    continue
            clean_lines.append(line)
        
        final_code = "\n".join(clean_lines).strip() + "\n"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(final_code)
        print(f"Cleaned {path}")
    except Exception as e:
        print(f"Error cleaning {path}: {e}")

if __name__ == '__main__':
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith('.py') and name != 'strip.py':
                clean_file(os.path.join(root, name))
