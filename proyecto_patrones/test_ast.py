import ast
code = '''def foo():
    """This is a
    docstring"""
    pass
'''
tree = ast.parse(code)
doc = tree.body[0].body[0]
print(doc.lineno, doc.col_offset, doc.end_lineno, doc.end_col_offset)
