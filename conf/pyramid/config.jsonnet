/*
Assembles the sections from sections.libsonnet into complete Pyramid/PasteDeploy INI
files. Each INI file is self-contained, i.e. there are no references to sections
in other config files (e.g. via `use = config:uri`).
*/

local sections = import 'sections.libsonnet';

{
  // Output INI files
  'demo.ini': std.manifestIni(rc_and_demo_ini),
  'demo_frontend.ini': std.manifestIni(rc_and_demo_frontend_ini),
  'rc.ini': std.manifestIni(rc_and_demo_ini),
  'rc_frontend.ini': std.manifestIni(rc_and_demo_frontend_ini),
  'smalldb.ini': std.manifestIni({
    sections:
      sections.App(development=false, use_small_db=true) +
      sections.Indexer() +
      shared_non_development_ini_sections,
  }),
  'test.ini': std.manifestIni(
    {
      sections:
        test_app_section +
        sections.Indexer(queue_type='REDIS_LIST') +
        shared_non_development_ini_sections,
    }
  ),
  'test_frontend.ini': std.manifestIni(
    {
      sections:
        test_app_section +
        sections.Indexer(queue_type='REDIS_LIST', queue_worker_processes=8) +
        shared_non_development_ini_sections,
    }
  ),
  'candidate.ini': std.manifestIni(
    {
      sections:
        candidate_app_section +
        sections.Indexer(queue_type='BASE_QUEUE_TYPE') +
        shared_non_development_ini_sections,
    }
  ),
  'candidate_frontend.ini': std.manifestIni(
    {
      sections:
        candidate_app_section +
        sections.Indexer(queue_type='BASE_QUEUE_TYPE', queue_worker_processes=8) +
        shared_non_development_ini_sections,
    }
  ),
  'development.ini': std.manifestIni(
    {
      sections:
        sections.App(
          pg_uri='postgresql://postgres@:5432/postgres?host=/tmp/snovault/pgdata',
        ) +
        sections.PipelineDebug(pipeline='egg:PasteDeploy#prefix egg:repoze.debug#pdbpm app') +
        sections.CompositeMain() +
        sections.Indexer(
          indexer_initial_log=false,
          queue_worker_processes=2,
          queue_worker_chunk_size=1024,
          queue_worker_batch_size=2000,
          queue_worker_get_size=2000,
        ) +
        sections.VisIndexer() +
        sections.RegionIndexer() +
        sections.ServerMain() +
        sections.Loggers(additional_loggers=['wsgi'],) +
        sections.Handlers() +
        sections.Formatters() +
        sections.GenericLogger(section_name='logger_root', level='INFO', handlers='console') +
        sections.GenericLogger(section_name='logger_wsgi', level='DEBUG', qualname='wsgi') +
        sections.GenericLogger(section_name='logger_encoded', level='DEBUG', qualname='encoded') +
        sections.GenericLogger(
          section_name='logger_snovault.batchupgrade',
          level='INFO',
          handlers='console',
          qualname='snovault.batchupgrade',
          propagate=false
        ) +
        sections.GenericHandler(section_name='handler_console') +
        sections.GenericFormatter(
          section_name='formatter_generic',
          format='%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s'
        ),
    },
  ),
  // Shared variables
  local test_app_section = sections.App(
    development=false, external_aws_s3_transfer_allow=true,
  ),
  local candidate_app_section = sections.App(
    accession_factory='encoded.server_defaults.enc_accession',
    blob_bucket='encoded-blobs',
    development=false,
    external_aws_s3_transfer_allow=true,
    file_upload_bucket='encode-files',
    pds_private_bucket='encode-private',
    pds_public_bucket='encode-public',
  ),
  local rc_and_demo_ini = {
    sections:
      sections.App(development=false) +
      sections.Indexer() +
      shared_non_development_ini_sections,
  },
  local rc_and_demo_frontend_ini = {
    sections:
      sections.App(development=false) +
      sections.Indexer(queue_worker_processes=8) +
      shared_non_development_ini_sections,
  },
  local shared_non_development_ini_sections =
    sections.VisIndexer() +
    sections.RegionIndexer() +
    sections.MemLimit() +
    sections.PipelineDebug() +
    sections.PipelineMain() +
    sections.ServerMain() +
    sections.Loggers(additional_loggers=['encoded_listener', 'file_encoded_listener'],) +
    sections.Handlers(additional_handlers=['fl_batchupgrade'],) +
    sections.Formatters() +
    sections.GenericLogger(section_name='logger_root', level='WARN', handlers='console') +
    sections.GenericLogger(
      section_name='logger_encoded',
      level='WARN',
      handlers='console',
      qualname='encoded',
      propagate=false
    ) +
    sections.GenericLogger(
      section_name='logger_encoded_listener',
      level='INFO',
      handlers='console',
      qualname='snovault.elasticsearch.es_index_listener',
      propagate=false
    ) +
    sections.GenericLogger(
      section_name='logger_file_encoded_listener',
      level='INFO',
      handlers='console',
      qualname='encoded.commands.es_file_index_listener',
      propagate=false
    ) +
    sections.GenericLogger(
      section_name='logger_snovault.batchupgrade',
      level='INFO',
      handlers='fl_batchupgrade, console',
      qualname='snovault.batchupgrade',
      propagate=false
    ) +
    sections.GenericHandler(section_name='handler_console') +
    sections.GenericHandler(
      section_name='handler_fl_batchupgrade',
      class='FileHandler',
      args="('batchupgrade.log','a')"
    ) +
    sections.GenericFormatter(
      section_name='formatter_generic',
      format='%(levelname)s [%(name)s][%(threadName)s] %(message)s'
    ),
}
