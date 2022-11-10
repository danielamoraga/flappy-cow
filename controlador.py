"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

from matplotlib.pyplot import pause
from modelo import Cow, LogCreator
import glfw
import sys
from typing import Union


class Controller(object):
    model: Union['Cow', None]  # Con esto queremos decir que el tipo de modelo es 'Bird' (nuestra clase) o None
    pipe: Union['LogCreator', None]

    def __init__(self):
        self.model = None
        self.pipe = None
        self.pause=True

    def set_model(self, m):
        self.model = m

    def set_pipe(self, p):
        self.pipe = p

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        # Controlador modifica al modelo
        elif key == glfw.KEY_UP:
            self.model.jump()

        elif key ==glfw.KEY_SPACE:
            print('Play/Pause')
            self.pause = not self.pause

        else:
            print('Unknown key')
