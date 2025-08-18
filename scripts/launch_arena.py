import os
import sys
import subprocess
import time

# Helper to launch a script in a new terminal window

def launch_in_new_terminal(script, venv_python, title):
    if sys.platform.startswith('win'):
        # Windows: use start to open a new cmd window
        cmd = [
            'start', f'"{title}"',
            'cmd', '/k', f'{venv_python} {script}'
        ]
        # Use shell=True for 'start' to work
        subprocess.Popen(' '.join(cmd), shell=True)
    elif sys.platform.startswith('darwin'):
        # macOS: use osascript to open Terminal
        apple_script = f'''osascript -e 'tell application "Terminal" to do script "{venv_python} {script}"' '''
        subprocess.Popen(apple_script, shell=True)
    else:
        # Linux: try gnome-terminal, xterm, or fallback
        for term in ['gnome-terminal', 'x-terminal-emulator', 'xterm']:
            if subprocess.call(f'which {term}', shell=True, stdout=subprocess.DEVNULL) == 0:
                subprocess.Popen([term, '-e', f'{venv_python} {script}'])
                break
        else:
            print(f"[WARN] Could not find a terminal emulator. Run: {venv_python} {script}")

if __name__ == '__main__':
    venv_python = os.path.abspath(os.path.join('.venv', 'Scripts', 'python.exe')) if sys.platform.startswith('win') else os.path.abspath(os.path.join('.venv', 'bin', 'python'))
    main_py = os.path.abspath('main.py')
    dash_py = os.path.abspath('dashboard_api.py')

    print("[INFO] Launching main.py in a new terminal window...")
    launch_in_new_terminal(main_py, venv_python, 'ChaosArena-Main')
    time.sleep(2)
    print("[INFO] Launching dashboard_api.py in a new terminal window...")
    launch_in_new_terminal(dash_py, venv_python, 'ChaosArena-Dashboard')
    print("[INFO] Both processes launched. If you don't see new terminals, run them manually:")
    print(f"  {venv_python} {main_py}")
    print(f"  {venv_python} {dash_py}")
