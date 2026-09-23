"""One-shot build: parse the Turkish source content, then render dist/index.html."""
import runpy, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
runpy.run_path(os.path.join(HERE, "parse_content.py"), run_name="__main__")
runpy.run_path(os.path.join(HERE, "render.py"), run_name="__main__")
