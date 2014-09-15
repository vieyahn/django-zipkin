from constants import DEFAULT_ZIPKIN_SERVICE_NAME, DEFAULT_ZIPKIN_DATA_STORE_CLASS,\
    DEFAULT_ZIPKIN_LOGGER_NAME, DEFAULT_ZIPKIN_ID_GENERATOR_CLASS
try:
    from configglue.schema import Section, StringOption
    has_configglue = True
except ImportError:
    has_configglue = False

if has_configglue:
    class DjangoZipkinSection(Section):
        zipkin_service_name = StringOption(default=DEFAULT_ZIPKIN_SERVICE_NAME)
        zipkin_data_store_class = StringOption(default=DEFAULT_ZIPKIN_DATA_STORE_CLASS)
        zipkin_logger_name = StringOption(default=DEFAULT_ZIPKIN_LOGGER_NAME)
        zipkin_id_generator_class = StringOption(default=DEFAULT_ZIPKIN_ID_GENERATOR_CLASS)
