# -*- coding: utf-8 -*-
import os
import threading

from . import _magic

__version__ = '0.0.1'


def open(mime=False, magic_file=None,
         mime_encoding=False,
         keep_going=False):
    flags = _magic.MAGIC_NONE
    if mime:
        flags |= _magic.MAGIC_MIME_TYPE
    elif mime_encoding:
        flags |= _magic.MAGIC_MIME_ENCODING
    if keep_going:
        flags |= _magic.MAGIC_CONTINUE

    if not magic_file:
        path = os.path.realpath(__file__).rsplit('/', 2)[0]
        magic_file = os.path.join(path, 'misc', 'magic.mgc')

    return _magic.Magic(flags, magic_file=magic_file)


instances = threading.local()


def _get_magic_type(mime):
    i = vars(instances).get(mime)
    if i is None:
        i = vars(instances)[mime] = open(mime=mime)
    return i


def from_file(filename, mime=False):
    """"
    Accepts a filename and returns the detected filetype.  Return
    value is the mimetype if mime=True, otherwise a human readable
    name.

    >>> from_file("testdata/test.pdf", mime=True)
    'application/pdf'
    """
    with _get_magic_type(mime) as m:
        return m.from_file(filename)


def from_buffer(buffer, mime=False):
    """
    Accepts a binary string and returns the detected filetype.  Return
    value is the mimetype if mime=True, otherwise a human readable
    name.

    >>> from_buffer(open("testdata/test.pdf").read(1024))
    'PDF document, version 1.2'
    """
    with _get_magic_type(mime) as m:
        return m.from_buffer(buffer)
