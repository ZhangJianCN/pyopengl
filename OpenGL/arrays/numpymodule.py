"""Numpy (new version) module implementation of the OpenGL-ctypes array interfaces

XXX Need to register handlers for all of the scalar types that numpy returns,
would like to have all return values be int/float if they are of  compatible
type as well.
"""
REGISTRY_NAME = 'numpy'
import operator,logging
from OpenGL import _configflags
log = logging.getLogger( __name__ )
try:
    import numpy
except ImportError as err:
    raise ImportError( """No numpy module present: %s"""%(err))
import OpenGL
import ctypes
from OpenGL._bytes import long, integer_types
from OpenGL import constants, constant, error
from OpenGL.arrays import formathandler
c_void_p = ctypes.c_void_p
from OpenGL import acceleratesupport
NumpyHandler = None
if acceleratesupport.ACCELERATE_AVAILABLE:
    try:
        from OpenGL_accelerate.numpy_formathandler import NumpyHandler
    except ImportError as err:
        log.warn(
            "Unable to load numpy_formathandler accelerator from OpenGL_accelerate"
        )
if NumpyHandler is None:
    from OpenGL.arrays import buffers
    class NumpyHandler( buffers.BufferHandler ):
        @classmethod
        def zeros( cls, dims, typeCode ):
            """Return Numpy array of zeros in given size"""
            return numpy.zeros( dims, GL_TYPE_TO_ARRAY_MAPPING[typeCode])
        
        @classmethod
        def asArray( cls, value, typeCode=None ):
            """Convert given value to an array value of given typeCode"""
            return super(NumpyHandler,cls).asArray( cls.contiguous(value,typeCode), typeCode )
        @classmethod
        def contiguous( cls, source, typeCode=None ):
            """Get contiguous array from source

            source -- numpy Python array (or compatible object)
                for use as the data source.  If this is not a contiguous
                array of the given typeCode, a copy will be made,
                otherwise will just be returned unchanged.
            typeCode -- optional 1-character typeCode specifier for
                the numpy.array function.

            All gl*Pointer calls should use contiguous arrays, as non-
            contiguous arrays will be re-copied on every rendering pass.
            Although this doesn't raise an error, it does tend to slow
            down rendering.
            """
            typeCode = GL_TYPE_TO_ARRAY_MAPPING[ typeCode ]
            try:
                contiguous = source.flags.contiguous
            except AttributeError as err:
                if typeCode:
                    return numpy.ascontiguousarray( source, typeCode )
                else:
                    return numpy.ascontiguousarray( source )
            else:
                if contiguous and (typeCode is None or typeCode==source.dtype.char):
                    return source
                elif (contiguous and cls.ERROR_ON_COPY):
                    from OpenGL import error
                    raise error.CopyError(
                        """Array of type %r passed, required array of type %r""",
                        source.dtype.char, typeCode,
                    )
                else:
                    # We have to do astype to avoid errors about unsafe conversions
                    # XXX Confirm that this will *always* create a new contiguous array
                    # XXX Guard against wacky conversion types like uint to float, where
                    # we really don't want to have the C-level conversion occur.
                    # XXX ascontiguousarray is apparently now available in numpy!
                    if cls.ERROR_ON_COPY:
                        from OpenGL import error
                        raise error.CopyError(
                            """Non-contiguous array passed""",
                            source,
                        )
                    if typeCode is None:
                        typeCode = source.dtype.char
                    return numpy.ascontiguousarray( source, typeCode )

try:
    numpy.array( [1], 's' )
    SHORT_TYPE = 's'
except TypeError as err:
    SHORT_TYPE = 'h'
    USHORT_TYPE = 'H'

def lookupDtype( char ):
    return numpy.zeros( (1,), dtype=char ).dtype

ARRAY_TO_GL_TYPE_MAPPING = {
    lookupDtype('d'): constants.GL_DOUBLE,
    lookupDtype('f'): constants.GL_FLOAT,
    lookupDtype('i'): constants.GL_INT,
    lookupDtype(SHORT_TYPE): constants.GL_SHORT,
    lookupDtype(USHORT_TYPE): constants.GL_UNSIGNED_SHORT,
    lookupDtype('B'): constants.GL_UNSIGNED_BYTE,
    lookupDtype('c'): constants.GL_UNSIGNED_BYTE,
    lookupDtype('b'): constants.GL_BYTE,
    lookupDtype('I'): constants.GL_UNSIGNED_INT,
    #lookupDtype('P'), constants.GL_VOID_P, # normally duplicates another type (e.g. 'I')
    None: None,
}
GL_TYPE_TO_ARRAY_MAPPING = {
    constants.GL_DOUBLE: lookupDtype('d'),
    constants.GL_FLOAT:lookupDtype('f'),
    constants.GL_INT: lookupDtype('i'),
    constants.GL_BYTE: lookupDtype('b'),
    constants.GL_SHORT: lookupDtype(SHORT_TYPE),
    constants.GL_UNSIGNED_INT: lookupDtype('I'),
    constants.GL_UNSIGNED_BYTE: lookupDtype('B'),
    constants.GL_UNSIGNED_SHORT: lookupDtype(USHORT_TYPE),
    constants.GL_VOID_P: lookupDtype('P'),
    None: None,
}
