'''OpenGL extension NV.vertex_program

This module customises the behaviour of the 
OpenGL.raw.GL.NV.vertex_program to provide a more 
Python-friendly API
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.NV.vertex_program import *
### END AUTOGENERATED SECTION