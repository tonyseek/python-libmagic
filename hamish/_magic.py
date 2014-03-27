import cffi

__version__ = "0.0.1"

# Flag constants for open and setflags
MAGIC_NONE = NONE = 0
MAGIC_DEBUG = DEBUG = 1
MAGIC_SYMLINK = SYMLINK = 2
MAGIC_COMPRESS = COMPRESS = 4
MAGIC_DEVICES = DEVICES = 8
MAGIC_MIME_TYPE = MIME_TYPE = 16
MAGIC_CONTINUE = CONTINUE = 32
MAGIC_CHECK = CHECK = 64
MAGIC_PRESERVE_ATIME = PRESERVE_ATIME = 128
MAGIC_RAW = RAW = 256
MAGIC_ERROR = ERROR = 512
MAGIC_MIME_ENCODING = MIME_ENCODING = 1024
MAGIC_MIME = MIME = 1040
MAGIC_APPLE = APPLE = 2048

MAGIC_NO_CHECK_COMPRESS = NO_CHECK_COMPRESS = 4096
MAGIC_NO_CHECK_TAR = NO_CHECK_TAR = 8192
MAGIC_NO_CHECK_SOFT = NO_CHECK_SOFT = 16384
MAGIC_NO_CHECK_APPTYPE = NO_CHECK_APPTYPE = 32768
MAGIC_NO_CHECK_ELF = NO_CHECK_ELF = 65536
MAGIC_NO_CHECK_TEXT = NO_CHECK_TEXT = 131072
MAGIC_NO_CHECK_CDF = NO_CHECK_CDF = 262144
MAGIC_NO_CHECK_TOKENS = NO_CHECK_TOKENS = 1048576
MAGIC_NO_CHECK_ENCODING = NO_CHECK_ENCODING = 2097152

MAGIC_NO_CHECK_BUILTIN = NO_CHECK_BUILTIN = 4173824

MAGIC_VERSION = 517


ffi = cffi.FFI()
ffi.cdef("""
    struct magic_set;

    struct magic_set *magic_open(int);
    void magic_close(struct magic_set *);

    const char *magic_getpath(const char *, int);
    const char *magic_file(struct magic_set *, const char *);
    const char *magic_descriptor(struct magic_set *, int);
    const char *magic_buffer(struct magic_set *, const void *, size_t);

    const char *magic_error(struct magic_set *);
    int magic_setflags(struct magic_set *, int);

    int magic_version();
    int magic_load(struct magic_set *, const char *);
    int magic_compile(struct magic_set *, const char *);
    int magic_check(struct magic_set *, const char *);
    int magic_list(struct magic_set *, const char *);
    int magic_errno(struct magic_set *);
""")
cmagic = ffi.verify(
    '#include "magic.h"',
    include_dirs=['vendor/include'],
    library_dirs=['vendor/lib'],
    libraries=["magic_embed", "z_embed"]
)


class Magic(object):
    def __init__(self, magic_flag=None, magic_file=None):
        self._c_magic_t = ffi.NULL
        self.magic_flag = MAGIC_NONE if magic_flag is None else magic_flag
        self.magic_file = ffi.NULL if magic_file is None else magic_file

    def __enter__(self):
        self.open(self.magic_flag)
        self.load(self.magic_file)
        return self

    def __exit__(self, error_type, error_value, error_tb):
        self.close()

    def open(self, flags):
        self._c_magic_t = cmagic.magic_open(flags)

    def close(self):
        cmagic.magic_close(self._c_magic_t)

    def load(self, path):
        cmagic.magic_load(self._c_magic_t, path)

    def from_file(self, filename):
        r = cmagic.magic_file(self._c_magic_t, filename)
        if r:
            return ffi.string(r)

    def from_buffer(self, buf):
        """
        Returns a textual description of the contents of the argument passed
        as a buffer or None if an error occurred and the MAGIC_ERROR flag
        is set. A call to errno() will return the numeric error code.
        """
        c_buf = ffi.new('char []', buf)
        c_buf_len = ffi.cast('size_t', len(c_buf) - 1)
        r = cmagic.magic_buffer(self._c_magic_t, c_buf, c_buf_len)
        if r:
            return ffi.string(r)
