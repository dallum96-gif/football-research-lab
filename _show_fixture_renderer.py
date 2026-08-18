from pathlib import Path
import ast

path = Path(".\gui\app_redesign.py")
text = path.read_text(encoding="utf-8-sig")
tree = ast.parse(text)

fn = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "render_fixture_detail"
)

lines = text.splitlines()
for line in lines[fn.lineno - 1:fn.end_lineno]:
    print(line)
