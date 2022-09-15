import logging
import logstash

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
# test_logger.addHandler(logstash.LogstashHandler('servicex.atlas-ml.org', 5959, version=1))
test_logger.addHandler(logstash.TCPLogstashHandler('servicex.atlas-ml.org', 5959, version=1))

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')
