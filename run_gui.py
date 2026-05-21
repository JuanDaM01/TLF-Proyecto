import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proyecto_patrones'))
from main import run_gui

if __name__ == '__main__':
    run_gui()
