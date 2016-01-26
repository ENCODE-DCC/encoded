import gzip  
import logging  
_logger = logging.getLogger(__name__)

# monkey patch for 2.7
import sys  
if sys.version_info[:2] == (2, 7):  
    # ripped from py 3.4 gzip module
    # modified for py 2.7 _read()
    def read1(self, size=-1):
        self._check_closed()
        if self.mode != gzip.READ:
            import errno
            raise OSError(errno.EBADF, "read1() on write-only GzipFile object")

        if self.extrasize <= 0 and self.fileobj is None:
            return b''

        # For certain input data, a single call to _read() may not return
        # any data. In this case, retry until we get some data or reach EOF.
        try:
            while self.extrasize <= 0 and self._read():
                pass
        except EOFError:
            pass

        if size < 0 or size > self.extrasize:
            size = self.extrasize

        offset = self.offset - self.extrastart
        chunk = self.extrabuf[offset: offset + size]
        self.extrasize -= size
        self.offset += size
        return chunk

    gzip.GzipFile.read1 = read1

class AltGzipFile(gzip.GzipFile):

    def read(self, size=-1):
        chunks = []
        try:
            if size < 0:
                while True:
                    chunk = self.read1()
                    if not chunk:
                        break
                    chunks.append(chunk)
            else:
                while size > 0:
                    chunk = self.read1(size)
                    if not chunk:
                        break
                    size -= len(chunk)
                    chunks.append(chunk)
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            if not chunks or not str(e).startswith('Not a gzipped file'):
                raise
            _logger.warn('decompression OK, trailing garbage ignored')       

        return b''.join(chunks)
        