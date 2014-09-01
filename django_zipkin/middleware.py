import logging

from django_zipkin._thrift.zipkinCore.constants import SERVER_RECV, SERVER_SEND
from zipkin_data import ZipkinData, ZipkinId
from data_store import default as default_data_store
from id_generator import default as default_id_generator
from api import api as default_api
import constants
import defaults as settings


def _hdr_to_meta_key(h):
    return 'HTTP_' + h.upper().replace('-', '_')


def _str_to_bool(s):
    return s.lower() in ['true', 't', '1', 'yes']


class ZipkinDjangoRequestParser(object):
    trace_id_hdr_name = _hdr_to_meta_key(constants.TRACE_ID_HDR_NAME)
    span_id_hdr_name = _hdr_to_meta_key(constants.SPAN_ID_HDR_NAME)
    parent_span_id_hdr_name = _hdr_to_meta_key(constants.PARENT_SPAN_ID_HDR_NAME)
    sampled_hdr_name = _hdr_to_meta_key(constants.SAMPLED_HDR_NAME)
    flags_hdr_name = _hdr_to_meta_key(constants.FLAGS_HDR_NAME)

    def get_zipkin_data(self, request):
        return ZipkinData(
            trace_id=ZipkinId.from_hex(request.META.get(self.trace_id_hdr_name, None)),
            span_id=ZipkinId.from_hex(request.META.get(self.span_id_hdr_name, None)),
            parent_span_id=ZipkinId.from_hex(request.META.get(self.parent_span_id_hdr_name, None)),
            sampled=_str_to_bool(request.META.get(self.sampled_hdr_name, 'false')),
            flags=request.META.get(self.flags_hdr_name, None)
        )


class ZipkinMiddleware(object):
    def __init__(self, store=None, request_parser=None, id_generator=None, api=None):
        self.store = store or default_data_store
        self.request_parser = request_parser or ZipkinDjangoRequestParser()
        self.id_generator = id_generator or default_id_generator
        self.api = api or default_api
        self.logger = logging.getLogger(settings.ZIPKIN_LOGGER_NAME)

    def process_request(self, request):
        self.store.clear()
        data = self.request_parser.get_zipkin_data(request)
        if data.trace_id is None:
            data.trace_id = self.id_generator.generate_trace_id()
        data.parent_span_id = data.span_id
        data.span_id = self.id_generator.generate_span_id()
        self.store.set(data)
        self.api.set_rpc_name(request.method)
        self.api.record_event(SERVER_RECV)
        self.api.record_key_value(constants.ANNOTATION_HTTP_URI, request.get_full_path())

    def process_response(self, request, response):
        self.api.record_event(SERVER_SEND)
        self.api.record_key_value(constants.ANNOTATION_HTTP_STATUSCODE, response.status_code)
        if self.store.get().sampled:
            self.logger.info(self.api.build_log_message())
        return response

    def _build_trace(self):
        pass

    def _build_annotation(self, value):
        pass
