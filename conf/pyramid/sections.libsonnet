/*
Generic function to use for generating Pyramid/PasteDeploy INI config files. Each
function returns an object taking the form `{section_name: section_data}` where
`section_name` will be the name of the section in the serialized INI file and
`section_data` is an object containing key-value pairs to list under the section. So a
section like `{foo: {bar: baz}}` could be serialized into the following INI file:
```
[foo]
bar = baz
```

Each function's arguments can change the resulting section returned. The default values
are not particularly special, they usually represent the most common configuration
values to make assembling the sections into complete INI files less verbose by reducing
the need to supply overriding keyword arguments.

Jsonnet requires quoting any dotted keys or keys with spaces. If you need to use
PasteDeploy `set` keyword then enclose it in quotes, as in the example below:
```
'set timeout': 60,
```
*/
{
  App(
    accession_factory='encoded.server_defaults.test_accession',
    blob_bucket='encoded-blobs-dev',
    blob_store_profile_name='encoded-files-upload',
    development=true,
    elasticsearch_server='localhost:9201',
    external_aws_s3_transfer_allow=false,
    file_upload_bucket='encoded-files-dev',
    pds_private_bucket='encode-pds-private-dev',
    pds_public_bucket='encode-pds-public-dev',
    pg_uri='postgresql:///encoded',
    repo_root_directory='/srv/encoded',
    use_small_db=false,
  ): {
    'app:app': section_data,
    local shared_config = {
      use: 'egg:encoded',
      accel_redirect_header: 'X-Accel-Redirect',
      'auth0.siteName': 'ENCODE DCC Submission',
      download_proxy: 'https://download.encodeproject.org/',
      'elasticsearch.server': elasticsearch_server,
      rna_expression_elasticsearch_server: 'vpc-rna-expression-dro56qntagtgmls6suff2m7nza.us-west-2.es.amazonaws.com:80',
      'embed_cache.capacity': if development then 5000 else 25000,
      // Direct file transfer from external AWS S3 to internal S3 bucket
      external_aws_s3_transfer_allow: external_aws_s3_transfer_allow,
      external_aws_s3_transfer_buckets: '/srv/encoded/.aws/direct-external-s3-list',
      file_upload_bucket: 'encoded-files-dev',
      file_upload_profile_name: 'encoded-files-upload',
      genomic_data_service: if development then 'http://localhost:5000' else 'http://data-service.demo.regulomedb.org',
      // Only run ec2metadata on ec2 instances
      hostname_command: 'command -v ec2metadata > /dev/null && ec2metadata --public-hostname || hostname',
      // Local Storage: Settings must exist in...
      // encoded/tests/conftest.py
      local_storage_host: 'localhost',
      local_storage_port: if development then 6378 else 6379,
      local_storage_redis_index: 1,
      local_storage_timeout: 5,
      local_tz: 'US/Pacific',
      'multiauth.groupfinder': 'encoded.authorization.groupfinder',
      'multiauth.policies': 'auth0 session remoteuser accesskey',
      'multiauth.policy.accesskey.base': 'encoded.authentication.BasicAuthAuthenticationPolicy',
      'multiauth.policy.accesskey.check': 'encoded.authentication.basic_auth_check',
      'multiauth.policy.accesskey.namespace': 'accesskey',
      'multiauth.policy.accesskey.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
      'multiauth.policy.auth0.base': 'encoded.auth0.Auth0AuthenticationPolicy',
      'multiauth.policy.auth0.namespace': 'auth0',
      'multiauth.policy.auth0.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
      'multiauth.policy.remoteuser.base': 'pyramid.authentication.RemoteUserAuthenticationPolicy',
      'multiauth.policy.remoteuser.namespace': 'remoteuser',
      'multiauth.policy.remoteuser.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
      'multiauth.policy.session.base': 'pyramid.authentication.SessionAuthenticationPolicy',
      'multiauth.policy.session.namespace': 'mailto',
      'multiauth.policy.session.use': 'encoded.authentication.NamespacedAuthenticationPolicy',
      //  Public bucket
      pds_private_bucket: 'encode-pds-private-dev',
      pds_public_bucket: 'encode-pds-public-dev',
      'postgresql.statement_timeout': if development then 20 else 120,
      'pyramid.default_locale_name': 'en',
      'retry.attempts': 3,
      'snp_search.server': elasticsearch_server,
      'sqlalchemy.url': pg_uri,
    },
    local development_only_config = {
      create_tables: true,
      load_test_only: true,
      'pyramid.debug_authorization': false,
      'pyramid.debug_notfound': true,
      'pyramid.debug_routematch': false,
      'pyramid.reload_templates': true,
      'snovault.load_test_data': 'encoded.loadxl:load_test_data',
      testing: true,
    },
    local non_development_only_config = {
      accession_factory: accession_factory,
      blob_bucket: blob_bucket,
      blob_store_profile_name: 'encoded-files-upload',
      file_upload_bucket: file_upload_bucket,
      'indexer.chunk_size': 1024,
      'indexer.processes': 16,
      pds_private_bucket: pds_private_bucket,
      pds_public_bucket: pds_public_bucket,
      'session.secret': '%s/session-secret.b64' % repo_root_directory,
      // Small DB
      small_db_path: '%s/src/encoded/tests/data/inserts/sorted_uuids.tsv' % repo_root_directory,
      use_small_db: use_small_db,
    },
    local section_data = shared_config + (if development then development_only_config else non_development_only_config),
  },
  Indexer(
    remote_indexing=false,
    queue_type='Simple',
    indexer_initial_log=true,
    queue_worker_processes=24,
    queue_worker_chunk_size=1024,
    queue_worker_batch_size=5000,
    queue_worker_get_size=2500000,
  ): {
    'composite:indexer': section_data,
    local section_data = {
      use: 'egg:encoded#indexer',
      app: 'app',
      path: '/index',
      timeout: 60,
      'set embed_cache.capacity': 25000,
      'set indexer': true,
      // Log indexing data to file
      'set indexer_initial_log': indexer_initial_log,
      'set indexer_initial_log_path': '/srv/encoded/initial-indexing-times.txt',
      // Used to limit the indexed uuids.  Either leave blank or set to a number like
      // 10 or 1000
      'set indexer_short_uuids': 0,
      'set queue_host': 'localhost',
      'set queue_port': 6379,
      'set queue_server': true,
      'set queue_type': queue_type,
      'set queue_worker': true,
      'set queue_worker_batch_size': queue_worker_batch_size,
      'set queue_worker_chunk_size': queue_worker_chunk_size,
      'set queue_worker_get_size': queue_worker_get_size,
      'set queue_worker_processes': queue_worker_processes,
      'set remote_indexing': remote_indexing,
      'set remote_indexing_threshold': 10001,
      'set stage_for_followup': 'vis_indexer',
      'set timeout': 60,
    },
  },
  VisIndexer(
    remote_indexing=false
  ): {
    'composite:visindexer': section_data,
    local section_data = {
      use: 'egg:encoded#indexer',
      app: 'app',
      path: '/index_vis',
      timeout: 60,
      'set timeout': 60,
      'set embed_cache.capacity': 5000,
      'set visindexer': true,
      'set remote_indexing': remote_indexing,
    },
  },
  MemLimit(): {
    'filter:memlimit': section_data,
    local section_data = {
      use: 'egg:encoded#memlimit',
      rss_limit: '500MB',
    },
  },
  PipelineMain(): {
    'pipeline:main': section_data,
    local section_data = {
      pipeline: 'memlimit egg:PasteDeploy#prefix app',
    },
  },
  PipelineDebug(pipeline='egg:repoze.debug#pdbpm app'): {
    'pipeline:debug': section_data,
    local section_data = {
      pipeline: pipeline,
      'set pyramid.includes': 'pyramid_translogger',
    },
  },
  CompositeMain(): {
    'composite:main': section_data,
    local section_data = {
      use: 'egg:rutter#urlmap',
      '/': 'debug',
      '/_indexer': 'indexer',
      '/_visindexer': 'visindexer',
    },
  },
  ServerMain(): {
    'server:main': section_data,
    local section_data = {
      use: 'egg:waitress#main',
      host: '0.0.0.0',
      port: 6543,
      threads: 1,
    },
  },
  // logging configuration
  // http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/logging.html
  Loggers(additional_loggers=[],): {
    loggers: section_data,
    local shared_loggers = ['root', 'encoded', 'snovault.batchupgrade'],
    local section_data = {
      keys: std.join(', ', shared_loggers + additional_loggers),
    },
  },
  Handlers(additional_handlers=[],): {
    handlers: section_data,
    local shared_handlers = ['console'],
    local section_data = {
      keys: std.join(', ', shared_handlers + additional_handlers),
    },
  },
  Formatters(): {
    formatters: section_data,
    local section_data = {
      keys: 'generic',
    },
  },
  GenericLogger(section_name, level, handlers='', qualname='', propagate=true): {
    [section_name]: section_data,
    local section_data = {
      level: level,
      handlers: handlers,
      [if std.length(qualname) > 0 then 'qualname']: qualname,
      [if !propagate then 'propagate']: 0,
    },
  },
  GenericHandler(
    section_name,
    class='StreamHandler',
    args='(sys.stderr,)',
    level='NOTSET',
    formatter='generic'
  ): {
    [section_name]: section_data,
    local section_data = {
      class: class,
      args: args,
      level: level,
      formatter: formatter,
    },
  },
  GenericFormatter(section_name, format): {
    [section_name]: section_data,
    local section_data = {
      format: format,
    },
  },
}
