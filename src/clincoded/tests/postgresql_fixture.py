from urllib.parse import quote
import os.path
import sys
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


def initdb(datadir, prefix='', echo=False):
    init_args = [
        os.path.join(prefix, 'initdb'),
        '-D', datadir,
        '-U', 'postgres',
        '--auth=trust',
    ]
    output = subprocess.check_output(
        init_args,
        close_fds=True,
        stderr=subprocess.STDOUT,
    )
    if echo:
        print(output.decode('utf-8'))


def server_process(datadir, prefix='', echo=False):
    args = [
        os.path.join(prefix, 'postgres'),
        '-D', datadir,
        '-F',  # no fsync
        '-h', '',
        '-k', datadir,
        '-p', '5432'
    ]
    process = subprocess.Popen(
        args,
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    SUCCESS_LINE = b'database system is ready to accept connections\n'

    lines = []
    for line in iter(process.stdout.readline, b''):
        if echo:
            sys.stdout.write(line.decode('utf-8'))
        lines.append(line)
        if line.endswith(SUCCESS_LINE):
            break
    else:
        code = process.wait()
        msg = ('Process return code: %d\n' % code) + b''.join(lines).decode('utf-8')
        raise Exception(msg)

    if not echo:
        process.stdout.close()

    if echo:
        print('Created: postgresql://postgres@:5432/postgres?host=%s' % quote(datadir))

    return process


def main():
    import atexit
    import shutil
    import tempfile
    datadir = tempfile.mkdtemp()

    print('Starting in dir: %s' % datadir)
    try:
        process = server_process(datadir, echo=True)
    except:
        shutil.rmtree(datadir)
        print('Cleaned dir: %s' % datadir)
        raise

    @atexit.register
    def cleanup_process():
        try:
            if process.poll() is None:
                process.terminate()
                for line in process.stdout:
                    sys.stdout.write(line.decode('utf-8'))
                process.wait()
        finally:
            shutil.rmtree(datadir)
            print('Cleaned dir: %s' % datadir)

    print('Started. ^C to exit.')

    try:
        for line in iter(process.stdout.readline, b''):
            sys.stdout.write(line.decode('utf-8'))
    except KeyboardInterrupt:
        raise SystemExit(0)


if __name__ == '__main__':
    main()
