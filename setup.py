import os
import sys
import tarfile
from subprocess import Popen, PIPE
from setuptools import setup, find_packages
from setuptools.dist import Distribution
from importlib import import_module


class CFFIExtension(object):
    def __init__(self, qualname):
        self._qualname = qualname
        self._ffi_cached = None
        # install the cffi
        Distribution({"setup_requires": ["cffi"]})

    @property
    def _ffi(self):
        if not self._ffi_cached:
            modname, ffiname = self._qualname.rsplit(":", 1)
            mod = import_module(modname)
            ffi = getattr(mod, ffiname)
            self._ffi_cached = ffi.verifier.get_extension()
        return self._ffi_cached

    def __getattribute__(self, name):
        if name in ("_ffi", "_ffi_cached", "_qualname"):
            return object.__getattribute__(self, name)
        return getattr(self._ffi, name)

    def __setattr__(self, name, value):
        if name in ("_ffi", "_ffi_cached", "_qualname"):
            return object.__setattr__(self, name, value)
        return setattr(self._ffi, name, value)


# setuptools DWIM monkey-patch madness
# http://mail.python.org/pipermail/distutils-sig/2007-September/thread.html#8204 # noqa
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__

PYTHON3K = sys.version_info[0] > 2

cwd = os.path.dirname(os.path.realpath(__file__))
vendor_path = os.path.join(cwd, 'vendor')


def execute(command_list, shell=False, wait=False):
    popen = Popen(command_list, stdout=PIPE, stderr=PIPE, shell=shell)
    if wait:
        popen.wait()
    stdoutdata, stderrdata = popen.communicate()
    if popen.returncode != 0:
        print(stderrdata)
        sys.exit()


def extract(file):
    t = tarfile.open(file, mode='r:gz')
    t.extractall()

os.chdir(vendor_path)

# extract file
extract('file-5.17.tar.gz')

# extract zlib
extract('zlib-1.2.8.tar.gz')

libmagic_path = os.path.join(vendor_path, 'file-5.17')
os.chdir(libmagic_path)

# build libmagic
execute(['patch -p0 < ../file-locale-5.17.patch'], shell=True, wait=True)

execute(['./configure', '--prefix=%s' % vendor_path, '--disable-shared',
        '--enable-static', '--with-pic'])

execute(['make', '-C', 'src', 'install'])

execute(['make', '-C', 'magic', 'install'])

# build libz
libz_path = os.path.join(vendor_path, 'zlib-1.2.8')
os.chdir(libz_path)
execute(['./configure', '--prefix=%s' % vendor_path, '--static'])

execute(['make', 'install'])

# prepare embed lib
os.rename(os.path.join(vendor_path, 'lib', 'libmagic.a'),
          os.path.join(vendor_path, 'lib', 'libmagic_embed.a'))
os.rename(os.path.join(vendor_path, 'lib', 'libz.a'),
          os.path.join(vendor_path, 'lib', 'libz_embed.a'))

os.chdir(cwd)

setup(
    name="python-libmagic",
    version="0.0.1",
    license="revised BSD",
    description="A wrapper for libmagic with static build.",
    author="XTao",
    author_email='xutao881001@gmail.com',
    install_requires=['cffi'],
    ext_modules=[CFFIExtension("hamish._magic:ffi")],
    py_modules=['hamish'],
    packages=find_packages(),
    package_data={'': ['misc/magic.mgc']},
    include_package_data=True,
    zip_safe=False,
    tests_require=['mock'] + [] if PYTHON3K else ['unittest2'],
    test_suite="tests" if PYTHON3K else "unittest2.collector",
    data_files=[('misc', ['vendor/share/misc/magic.mgc'])],
)
