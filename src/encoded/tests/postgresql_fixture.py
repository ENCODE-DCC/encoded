import os.path

def server_process(datadir, prefix='', echo=False):
    from urllib import quote
    import subprocess
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
        print output

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

    SUCCESS_LINE = 'database system is ready to accept connections\n'

    lines = []
    for line in iter(process.stdout.readline, ''):
        if echo:
            print line,
        lines.append(line)
        if line.endswith(SUCCESS_LINE):
            break
    else:
        code = process.wait()
        msg = ('Process return code: %d\n' % code) + ''.join(lines)
        raise Exception(msg)

    if not echo:
        process.stdout.close()

    if echo:
        print 'Created: postgresql://postgres@:5432/postgres?host=%s' % quote(datadir)

    return process


def main():
    import atexit
    import shutil
    import tempfile
    datadir = tempfile.mkdtemp()

    print 'Starting in dir: %s' % datadir
    try:
        process = server_process(datadir, echo=True)
    except:
        shutil.rmtree(datadir)
        print 'Cleaned dir: %s' % datadir
        raise

    @atexit.register
    def cleanup_process():
        try:
            if process.poll() is None:
                process.terminate()
                for line in process.stdout:
                    print line,
                process.wait()
        finally:
            shutil.rmtree(datadir)
            print 'Cleaned dir: %s' % datadir

    print 'Started. ^C to exit.'

    try:
        for line in iter(process.stdout.readline, ''):
            print line,
    except KeyboardInterrupt:
        raise SystemExit(0)


if __name__ == '__main__':
    main()
