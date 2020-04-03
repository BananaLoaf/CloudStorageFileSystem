import errno
import stat
from typing import Union, List, Tuple

from refuse.high import FuseOSError
from pathlib import Path


class Stat:
    def __init__(self, is_dir: bool,
                 size: int,
                 atime: Any[int, float],
                 mtime: Any[int, float],
                 ctime: Any[int, float]):
        self.st_mode = stat.S_IFDIR | 0o755 if is_dir else stat.S_IFREG | 0o644
        self.st_ino = 2 if is_dir else 1
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


class FileSystem:
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
    # Dir ops
    def getattr(self, path: str, fh) -> Stat:
        """
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incompatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        """
        raise FuseOSError(errno.ENOENT)

    def utimens(self, path: str, times) -> int:
        """Times is a (atime, mtime) tuple. If None use current time."""
        return 0

    def fsyncdir(self, path: str, datasync, fh) -> int:
        return 0

    def readdir(self, path: str, fh) -> Union[List[str], List[Tuple[str, Stat, int]]]:
        """
        Can return either a list of names, or a list of (name, attrs, offset)
        tuples. attrs is a dict as in getattr.
        """
        return []

    def releasedir(self, path: str, fh) -> int:
        return 0

    def opendir(self, path: str) -> int:
        """Returns a numerical file handle."""
        return 0

    def rename(self, old: str, new: str):
        raise FuseOSError(errno.EROFS)

    def mkdir(self, path: str, mode):
        raise FuseOSError(errno.EROFS)

    def rmdir(self, path: str):
        raise FuseOSError(errno.EROFS)

    def readlink(self, path: str):
        raise FuseOSError(errno.ENOENT)

    def unlink(self, path: str):
        raise FuseOSError(errno.EROFS)

    def link(self, target: str, source: str):
        """Creates a hard link `target -> source` (e.g. ln source target)"""
        raise FuseOSError(errno.EROFS)

    def symlink(self, target: str, source: str):
        """Creates a symlink `target -> source` (e.g. ln -s source target)"""
        raise FuseOSError(errno.EROFS)

    # File ops
    def create(self, path: str, mode, fi) -> int:
        """Create should return a numerical file handle."""
        raise FuseOSError(errno.EROFS)
        return 0

    def open(self, path: str, flags) -> int:
        """
        When raw_fi is False (default case), open should return a numerical
        file handle.

        When raw_fi is True the signature of open becomes:
            open(self, path, fi)

        and the file handle should be set directly.
        """
        return 0

    def fsync(self, path: str, datasync, fh) -> int:
        return 0

    def read(self, path: str, size: int, offset: int, fh) -> bytes:
        """Returns a byte string containing the data requested."""
        raise FuseOSError(errno.EIO)

    def write(self, path: str, data: bytes, offset: int, fh):
        raise FuseOSError(errno.EROFS)

    def truncate(self, path: str, length: int, fh):
        raise FuseOSError(errno.EROFS)

    def flush(self, path: str, fh) -> int:
        return 0

    def release(self, path: str, fh) -> int:
        return 0

    ################################################################
    # Extended attributes
    def setxattr(self, path: str, name, value, options, position: int):
        raise FuseOSError(errno.ENOTSUP)

    def getxattr(self, path: str, name, position: int):
        raise FuseOSError(errno.ENOTSUP)

    def removexattr(self, path: str, name):
        raise FuseOSError(errno.ENOTSUP)

    def listxattr(self, path: str) -> list:
        return []
