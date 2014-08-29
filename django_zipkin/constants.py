DEFAULT_ZIPKIN_SERVICE_NAME = None
DEFAULT_ZIPKIN_LOGGER_NAME = 'zipkin'
DEFAULT_ZIPKIN_DATA_STORE_CLASS = 'django_zipkin.data_store.ThreadLocalDataStore'
DEFAULT_ZIPKIN_ID_GENERATOR_CLASS = 'django_zipkin.id_generator.SimpleIdGenerator'

TRACE_ID_HDR_NAME = "X-B3-TraceId"
SPAN_ID_HDR_NAME = "X-B3-SpanId"
PARENT_SPAN_ID_HDR_NAME = "X-B3-ParentSpanId"
SAMPLED_HDR_NAME = "X-B3-Sampled"
FLAGS_HDR_NAME = "X-B3-Flags"
