import logging

from django_zipkin._thrift.zipkinCore.constants import SERVER_RECV, SERVER_SEND
from zipkin_data import ZipkinData, ZipkinId
from data_store import default as default_data_store
from id_generator import default as default_id_generator
from api import api as default_api
import defaults as settings


class ZipkinDjangoRequestProcessor(object):
    trace_id_hdr_name = "HTTP_X_B3_TRACEID"
    span_id_hdr_name = "HTTP_X_B3_SPANID"
    parent_span_id_hdr_name = "HTTP_X_B3_PARENTSPANID"
    sampled_hdr_name = "HTTP_X_B3_SAMPLED"
    flags_hdr_name = "HTTP_X_B3_FLAGS"

    def get_zipkin_data(self, request):
        return ZipkinData(
            trace_id=ZipkinId.from_hex(request.META.get(self.trace_id_hdr_name, None)),
            span_id=ZipkinId.from_hex(request.META.get(self.span_id_hdr_name, None)),
            parent_span_id=ZipkinId.from_hex(request.META.get(self.parent_span_id_hdr_name, None)),
            sampled=request.META.get(self.sampled_hdr_name, False),
            flags=request.META.get(self.flags_hdr_name, None)
        )


class ZipkinMiddleware(object):
    def __init__(self, store=None, request_processor=None, id_generator=None, api=None):
        self.store = store or default_data_store
        self.request_processor = request_processor or ZipkinDjangoRequestProcessor()
        self.id_generator = id_generator or default_id_generator
        self.api = api or default_api
        self.logger = logging.getLogger(settings.ZIPKIN_LOGGER_NAME)

    def process_request(self, request):
        self.store.clear()
        data = self.request_processor.get_zipkin_data(request)
        if data.span_id is None:
            data.span_id = self.id_generator.generate_span_id()
        if data.trace_id is None:
            data.trace_id = self.id_generator.generate_trace_id()
        self.store.set(data)
        self.api.record_event(SERVER_RECV)

    def process_response(self, request, response):
        self.api.record_event(SERVER_SEND)
        self.logger.info(self.api.build_log_message())
        return response

    def _build_trace(self):
        pass

    def _build_annotation(self, value):
        pass
