from unittest2.case import TestCase
from mock import Mock, sentinel
from django.test import RequestFactory

from helpers import DjangoZipkinTestHelpers
from django_zipkin.zipkin_data import ZipkinData, ZipkinId
from django_zipkin.data_store import BaseDataStore
from django_zipkin.id_generator import BaseIdGenerator
from django_zipkin.middleware import ZipkinMiddleware, ZipkinDjangoRequestParser


__all__ = ['ZipkinMiddlewareTestCase', 'ZipkinDjangoRequestProcessorTestCase']


class ZipkinMiddlewareTestCase(TestCase):
    def setUp(self):
        self.store = Mock(spec=BaseDataStore)
        self.request_processor = Mock(spec=ZipkinDjangoRequestParser)
        self.generator = Mock(spec=BaseIdGenerator)
        self.middleware = ZipkinMiddleware(self.store, self.request_processor, self.generator)

    def test_intercepts_incoming_trace_id(self):
        self.middleware.process_request(Mock())
        self.store.set.assert_called_once_with(self.request_processor.get_zipkin_data.return_value)

    def test_generates_ids_if_no_incoming(self):
        self.request_processor.get_zipkin_data.return_value = ZipkinData()
        self.middleware.process_request(Mock())
        self.generator.generate_trace_id.assert_called_once_with()
        self.generator.generate_span_id.assert_called_once_with()
        data = self.store.set.call_args[0][0]
        self.assertEqual(data.span_id, self.generator.generate_span_id.return_value)
        self.assertEqual(data.trace_id, self.generator.generate_trace_id.return_value)

    def test_with_defaults(self):
        self.request_factory = RequestFactory()
        self.middleware = ZipkinMiddleware()
        self.middleware.process_request(self.request_factory.get('/', HTTP_X_B3_TRACEID='000000000000002a'))
        self.assertEqual(self.middleware.store.get().trace_id.get_binary(), 42)
        self.assertIsInstance(self.middleware.store.get().span_id, ZipkinId)

    def test_incoming_span_id_to_parent_span_id(self):
        self.middleware.request_parser = ZipkinDjangoRequestParser()
        request_factory = RequestFactory()
        self.middleware.process_request(request_factory.get('/', HTTP_X_B3_SPANID='000000000000002a'))
        self.assertEqual(self.store.set.call_args[0][0].parent_span_id.get_binary(), 42)


class ZipkinDjangoRequestProcessorTestCase(DjangoZipkinTestHelpers, TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.processor = ZipkinDjangoRequestParser()

    def test_header_keys(self):
        transform = lambda s: 'HTTP_' + s.upper().replace('-', '_')
        self.assertEqual(ZipkinDjangoRequestParser.trace_id_hdr_name, transform("X-B3-TraceId"))
        self.assertEqual(ZipkinDjangoRequestParser.span_id_hdr_name, transform("X-B3-SpanId"))
        self.assertEqual(ZipkinDjangoRequestParser.parent_span_id_hdr_name, transform("X-B3-ParentSpanId"))
        self.assertEqual(ZipkinDjangoRequestParser.sampled_hdr_name, transform("X-B3-Sampled"))
        self.assertEqual(ZipkinDjangoRequestParser.flags_hdr_name, transform("X-B3-Flags"))

    def test_all_fields_filled(self):
        trace_id = ZipkinId.from_binary(42)
        span_id = ZipkinId.from_binary(-42)
        parent_span_id = ZipkinId.from_binary(53)
        request = self.request_factory.get('/', **{
            ZipkinDjangoRequestParser.trace_id_hdr_name: trace_id.get_hex(),
            ZipkinDjangoRequestParser.span_id_hdr_name:  span_id.get_hex(),
            ZipkinDjangoRequestParser.parent_span_id_hdr_name:  parent_span_id.get_hex(),
            ZipkinDjangoRequestParser.sampled_hdr_name: sentinel.sampled,
            ZipkinDjangoRequestParser.flags_hdr_name: sentinel.flags
        })
        self.assertZipkinDataEquals(
            self.processor.get_zipkin_data(request),
            ZipkinData(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                sampled=sentinel.sampled,
                flags=sentinel.flags
            )
        )

    def test_no_fields_filled(self):
        self.assertZipkinDataEquals(
            self.processor.get_zipkin_data(self.request_factory.get('/')),
            ZipkinData()
        )
