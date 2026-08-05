import sys
import os
import io
import importlib

# force utf-8 encoding for stdout and stderr on windows (not sure if this actually does anything but worth a try)
try:
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

def main():
    if len(sys.argv) < 2:
        return
    cmd_name = sys.argv[1].lower()
    cmd_args = sys.argv[2:]

    cmds_dir = os.path.dirname(os.path.abspath(__file__))
    if cmds_dir not in sys.path:
        sys.path.insert(0, cmds_dir)

    try:
        mod = importlib.import_module(cmd_name)
    except Exception as e:
        print(f"Error loading command '{cmd_name}': {e}")
        return

    class Term:
        cwd = os.getcwd()
        username = os.environ.get("USERNAME", "user")

        @staticmethod
        def write(text, delay=False):
            try:
                print(str(text))
            except Exception:
                # fallback print for unencodable characters
                print(str(text).encode('utf-8', errors='replace').decode('utf-8'))

    try:
        mod.run(Term(), cmd_args)
    except Exception as e:
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
