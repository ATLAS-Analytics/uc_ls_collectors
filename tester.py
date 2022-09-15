import logging
import sys
import logstash

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
# test_logger.addHandler(logstash.LogstashHandler('servicex.atlas-ml.org', 5959, version=1))
test_logger.addHandler(logstash.TCPLogstashHandler('servicex.atlas-ml.org', 5959, version=1))

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning mdessage.')

metric = {
    'metric_string': 'python version: ' + repr(sys.version_info),
    'metric_boolean': True,
    'metric_dict': {'a': 1, 'b': 'c'},
    'metric_float': 1.23,
    'metric_integer': 123,
    'metric_list': [1, 2, '3'],
}

test_logger.info('python-logstash: test extra fields', extra=metric)
