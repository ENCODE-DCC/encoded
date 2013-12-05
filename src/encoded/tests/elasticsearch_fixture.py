import os.path

def server_process(datadir, host='127.0.0.1', port=9200, prefix='', echo=False):
    import subprocess
    args = [
        os.path.join(prefix, 'elasticsearch'),
        '-f',  # foreground
        '-Des.path.data="%s"' % os.path.join(datadir, 'data'),
        '-Des.path.logs="%s"' % os.path.join(datadir, 'logs'),
        '-Des.node.local=true',
        '-Des.discovery.zen.ping.multicast.enabled=false',
        '-Des.network.host=%s' % host,
        '-Des.http.port=%d' % port,
        '-Des.index.number_of_shards=1',
        '-Des.index.number_of_replicas=0',
        '-Des.index.store.type=memory',
        '-Des.index.store.fs.memory.enabled=true',
        '-Des.index.gateway.type=none',
        '-Des.gateway.type=none',
    ]
    # elasticsearch.deb setup
    if os.path.exists('/etc/elasticsearch'):
        args.append('-Des.path.conf=/etc/elasticsearch')
    process = subprocess.Popen(
        args,
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    SUCCESS_LINE = 'started\n'

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

    print 'Started. ^C to exit.'

    try:
        for line in iter(process.stdout.readline, ''):
            print line,
    except KeyboardInterrupt:
        raise SystemExit(0)


if __name__ == '__main__':
    main()
