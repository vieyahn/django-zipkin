from django.conf import settings

ZIPKIN_SERVICE_NAME = getattr(settings, 'ZIPKIN_SERVICE_NAME', None)

ZIPKIN_LOGGER_NAME = getattr(settings, 'ZIPKIN_LOGGER_NAME', 'zipkin')

ZIPKIN_DATA_STORE_CLASS = getattr(settings, 'ZIPKIN_DATA_STORE_CLASS', 'django_zipkin.data_store.ThreadLocalDataStore')

ZIPKIN_ID_GENERATOR_CLASS = getattr(settings, 'ZIPKIN_ID_GENERATOR_CLASS', 'django_zipkin.id_generator.SimpleIdGenerator')

