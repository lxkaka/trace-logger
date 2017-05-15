# -* coding: utf-8 -*-

import unittest
import logging
from logging.config import dictConfig
import time
from eagleeye.trace_builder import TraceIdGenerator
from eagleeye.rpc_updater import RpcIdUpdater, INITIAL_PARAMS
from eagleeye.log_maker import EagleEyeLogger
from eagleeye.logger_configuration import EAGLEEYE_LOG, log_conf


class EagleeyeTest(unittest.TestCase):
    dictConfig(log_conf)
    _logger = logging.getLogger(EAGLEEYE_LOG)
    start_time = int(time.time() * 1000)
    url = "http://127.0.0.1:8080/test/kaka?pa=1&sign=abc"
    span = 20
    result_code = 200

    def test_trace_builder(self):
        trace_id = TraceIdGenerator.get_trace_id()
        self.assertEqual(trace_id[-5], TraceIdGenerator.PID_FLAG)

    def test_rpc_updater(self):
        INITIAL_PARAMS.eagleeye_trace_id = TraceIdGenerator.get_trace_id()
        INITIAL_PARAMS.eagleeye_rpc_id = RpcIdUpdater.update_rpc_id()
        INITIAL_PARAMS.eagleeye_user_data = ''
        rpc_id = RpcIdUpdater.update_rpc_id(INITIAL_PARAMS.eagleeye_rpc_id)
        self.assertEqual(rpc_id, "0.1")
        self.assertEqual(INITIAL_PARAMS.call_counter, 1)

    def test_entry(self):
        logger = EagleEyeLogger(self._logger)
        logger.entry_log(
            start_time=self.start_time,
            url=self.url,
            span=self.span,
            result_code=self.result_code
        )

        # 自定义服务端日志
        logger.entry_log(
            trace_id=TraceIdGenerator.get_trace_id(),
            rpc_id="0.1",
            start_time=self.start_time,
            url=self.url,
            span=self.span,
            result_code=self.result_code
        )

    def test_client(self):
        logger = EagleEyeLogger(self._logger)
        INITIAL_PARAMS.eagleeye_trace_id = TraceIdGenerator.get_trace_id()
        INITIAL_PARAMS.eagleeye_rpc_id = "0.1."

        logger.client_log(
            rpc_type="91",
            start_time=self.start_time,
            url=self.url,
            span=self.span,
            result_code=self.result_code,
            request_size="123",
            response_size="321"
        )