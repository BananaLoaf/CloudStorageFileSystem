from refuse.high import Operations

from CloudStorageFileSystem.utils.filesystem import FileSystem


class CustomOperations(Operations):
    def __init__(self, fs: FileSystem):
        self.fs = fs

    def init(self, *args, **kwargs):
        return self.fs.init(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        return self.fs.destroy(*args, **kwargs)

    def mknod(self, *args, **kwargs):
        return self.fs.mknod(*args, **kwargs)

    def statfs(self, *args, **kwargs):
        return self.fs.statfs(*args, **kwargs)

    def ioctl(self, *args, **kwargs):
        return self.fs.ioctl(*args, **kwargs)

    # Permissions
    def access(self, *args, **kwargs):
        return self.fs.access(*args, **kwargs)

    def chmod(self, *args, **kwargs):
        return self.fs.chmod(*args, **kwargs)

    def chown(self, *args, **kwargs):
        return self.fs.chown(*args, **kwargs)

    # Dir ops
    def getattr(self, *args, **kwargs):
        return self.fs.getattr(*args, **kwargs)

    def utimens(self, *args, **kwargs):
        return self.fs.utimens(*args, **kwargs)

    def fsyncdir(self, *args, **kwargs):
        return self.fs.fsyncdir(*args, **kwargs)

    def readdir(self, *args, **kwargs):
        return [".", ".."] + self.fs.readdir(*args, **kwargs)

    def releasedir(self, *args, **kwargs):
        return self.fs.releasedir(*args, **kwargs)

    def opendir(self, *args, **kwargs):
        return self.fs.opendir(*args, **kwargs)

    def rename(self, *args, **kwargs):
        return self.fs.rename(*args, **kwargs)

    def mkdir(self, *args, **kwargs):
        return self.fs.mkdir(*args, **kwargs)

    def rmdir(self, *args, **kwargs):
        return self.fs.rmdir(*args, **kwargs)

    def readlink(self, *args, **kwargs):
        return self.fs.readlink(*args, **kwargs)

    def unlink(self, *args, **kwargs):
        return self.fs.unlink(*args, **kwargs)

    def link(self, *args, **kwargs):
        return self.fs.link(*args, **kwargs)

    def symlink(self, *args, **kwargs):
        return self.fs.symlink(*args, **kwargs)

    # File ops
    def create(self, *args, **kwargs):
        return self.fs.create(*args, **kwargs)

    def open(self, *args, **kwargs):
        return self.fs.open(*args, **kwargs)

    def fsync(self, *args, **kwargs):
        return self.fs.fsync(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self.fs.read(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.fs.write(*args, **kwargs)

    def truncate(self, *args, **kwargs):
        return self.fs.truncate(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.fs.flush(*args, **kwargs)

    def release(self, *args, **kwargs):
        return self.fs.release(*args, **kwargs)

    # Extended attributes
    def setxattr(self, *args, **kwargs):
        return self.fs.setxattr(*args, **kwargs)

    def getxattr(self, *args, **kwargs):
        return self.fs.getxattr(*args, **kwargs)

    def removexattr(self, *args, **kwargs):
        return self.fs.removexattr(*args, **kwargs)

    def listxattr(self, *args, **kwargs):
        return self.fs.listxattr(*args, **kwargs)
