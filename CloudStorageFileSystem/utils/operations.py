import errno
from typing import Optional, Union, Tuple
import stat
import os

from refuse.high import Operations, FuseOSError


def flag2mode(flags: int) -> str:
    modes = {os.O_RDONLY: "rb", os.O_WRONLY: "wb", os.O_RDWR: "wb+"}
    mode = modes[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        mode = mode.replace("w", "a", 1)

    return mode


class Stat:
    def __init__(self, is_dir: bool,
                 size: int,
                 atime: Union[int, float],
                 mtime: Union[int, float],
                 ctime: Union[int, float]):
        self.st_mode = stat.S_IFDIR | 0o755 if is_dir else stat.S_IFREG | 0o644
        # self.st_ino = 2 if is_dir else 1
        self.st_nlink = 1

        self.st_size = size
        self.st_blocks = int((size + 511) / 512)

        # self.st_uid = os.getuid()
        # self.st_gid = os.getgid()

        self.st_atime = float(atime)
        self.st_mtime = float(mtime)
        self.st_ctime = float(ctime)

    @property
    def is_dir(self):
        return self.st_mode == stat.S_IFDIR | 0o755

    @property
    def is_file(self):
        return self.st_mode == stat.S_IFREG | 0o644

    def items(self):
        st_vars = vars(self)
        for key in st_vars:
            yield key, st_vars[key]


class CustomOperations(Operations):
    # FS ops
    def init(self, path: str):
        """Called on filesystem initialization. Path is always /"""
        pass

    def destroy(self, path: str):
        """Called on filesystem destruction. Path is always /"""
        pass

    def mknod(self, path: str, mode, dev):
        raise FuseOSError(errno.EROFS)

    def statfs(self, path: str) -> dict:
        """
        Returns a dictionary with keys identical to the statvfs C structure of
        statvfs(3).

        On Mac OS X f_bsize and f_frsize must be a power of 2
        (minimum 512).
        """
        return {}

    def ioctl(self, path, cmd, arg, fip, flags, data):
        raise FuseOSError(errno.ENOTTY)

    ################################################################
    # Permissions
    def access(self, path: str, amode) -> int:
        return 0

    def chmod(self, path: str, mode):
        raise FuseOSError(errno.EROFS)

    def chown(self, path: str, uid, gid):
        raise FuseOSError(errno.EROFS)

    ################################################################
    # Main ops
    def getattr(self, path: str, fh: Optional[int] = None) -> Stat:
        """
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incompatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        """
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path: str, fh) -> Union[str, Tuple[str, Stat, int]]:
        """
        Can return either a list of names, or a list of (name, attrs, offset)
        tuples. attrs is a dict as in getattr.
        """
        yield "."
        yield ".."

    def rename(self, old: str, new: str):
        raise FuseOSError(errno.EROFS)

    def mkdir(self, path: str, mode):
        raise FuseOSError(errno.EROFS)

    def rmdir(self, path: str):
        raise FuseOSError(errno.EROFS)

    def unlink(self, path: str):
        raise FuseOSError(errno.EROFS)

    ################################################################
    # Other ops
    def utimens(self, path: str, times: Optional[Tuple] = None) -> int:
        """Times is a (atime, mtime) tuple. If None use current time."""
        return 0

    def link(self, target: str, source: str):
        """Creates a hard link `target -> source` (e.g. ln source target)"""
        raise FuseOSError(errno.EROFS)

    def symlink(self, target: str, source: str):
        """Creates a symlink `target -> source` (e.g. ln -s source target)"""
        raise FuseOSError(errno.EROFS)

    def readlink(self, path: str):
        raise FuseOSError(errno.ENOENT)

    def opendir(self, path: str) -> int:
        """Returns a numerical file handle."""
        return 0

    def releasedir(self, path: str, fh) -> int:
        return 0

    def fsyncdir(self, path: str, datasync, fh) -> int:
        return 0

    ################################################################
    # File ops
    def create(self, path: str, mode, fi: Optional[int] = None) -> int:
        """Create should return a numerical file handle."""
        raise FuseOSError(errno.EROFS)
        return 0

    def open(self, path: str, flags) -> int:
        """Open should return a numerical file handle."""
        return 0

    def read(self, path: str, size: int, offset: int, fh) -> bytes:
        """Returns a byte string containing the data requested."""
        raise FuseOSError(errno.EIO)

    def write(self, path: str, data: bytes, offset: int, fh):
        raise FuseOSError(errno.EROFS)

    def truncate(self, path: str, length: int, fh: Optional[int] = None):
        raise FuseOSError(errno.EROFS)

    def release(self, path: str, fh) -> int:
        return 0

    def flush(self, path: str, fh) -> int:
        return 0

    def fsync(self, path: str, datasync, fh) -> int:
        return 0

    ################################################################
    # Extended attributes
    def setxattr(self, path: str, name, value, options, position: int = 0):
        raise FuseOSError(errno.ENOTSUP)

    def getxattr(self, path: str, name, position: int = 0):
        raise FuseOSError(errno.ENOTSUP)

    def removexattr(self, path: str, name):
        raise FuseOSError(errno.ENOTSUP)

    def listxattr(self, path: str) -> list:
        return []
