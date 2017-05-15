# -*- coding: utf-8 -*-
import urlparse
from re import match, compile
from .trace_builder import TraceIdGenerator
from .rpc_updater import INITIAL_PARAMS, RpcIdUpdater


class HandleArgs(object):
    REGEX = "\\b((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\.((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\." \
            "((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\.((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\b"
    PATTERN = compile(REGEX)

    @staticmethod
    def pretty_string(content):
        try:
            if not isinstance(content, basestring):
                content = str(content)
            if not isinstance(content, unicode):
                content = content.decode("utf-8")
            content = content.replace("\n", "").replace("\r", "")
        except:
            content = "fail_to_pretty_string"
        return content

    @classmethod
    def get_remote_ip(cls, url):
        if url:
            parsed = urlparse.urlsplit(url)
            host = parsed.hostname
            if cls.validate(host):
                return host
        return None

    @classmethod
    def validate(cls, ip):
        try:
            if match(cls.PATTERN, ip):
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def get_size(response):
        try:
            if hasattr(response, 'request'):
                request_size = response.request.headers.get('content-length', '0')
                response_size = response.headers.get('content-length', '0')
            else:
                response_size = response.handler.headers.get('content-length', '0')
                request_size = '0'
        except:
            response_size = request_size = '0'
        return request_size, response_size


class EagleEyeLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def entry_log(self, **kwargs):
        """
        此方法可记录两类日志，包括
        自定义入口 rpc_type为 90
        自定义服务端 rpc_type为 92
        """
        trace_id = kwargs.pop("trace_id", None)
        rpc_id = kwargs.pop("rpc_id", None)
        time_stamp = kwargs.pop("start_time", "")
        span = kwargs.pop("span", "")
        result_code = "00" if kwargs.pop("result_code") == 200 else "01"
        url = kwargs.pop("url", "")
        ext_info = kwargs.pop("ext_info", "")
        INITIAL_PARAMS.eagleeye_user_data = kwargs.pop("user_data", "")

        if trace_id and rpc_id:
            rpc_type = "92"  # 自定义服务端
            response_size = kwargs.pop("response_size", "")
            if not response_size:
                request_size, response_size = HandleArgs.get_size(kwargs.pop('response', None))
            remote_ip = kwargs.pop("remote_ip", None)
            if not remote_ip:
                remote_ip = HandleArgs.get_remote_ip(url) or "0.0.0.0"
            INITIAL_PARAMS.eagleeye_trace_id = trace_id
            INITIAL_PARAMS.eagleeye_rpc_id = rpc_id

            # 日志格式，自定义服务端 traceId|timestamp|rpcType|rpcId|serviceName|method|resultCode|remoteIp|span|
            # responseSize|extInfo|userData
            _message = "{trace_id}|{ts}|{rpc_type}|{rpc_id}|{service}|{method}|{code}|{remote_ip}|{span}|{res_size}|" \
                       "{ext_info}|{user_data}".format(
                        trace_id=INITIAL_PARAMS.eagleeye_trace_id,
                        ts=HandleArgs.pretty_string(time_stamp),
                        rpc_type=rpc_type,
                        rpc_id=INITIAL_PARAMS.eagleeye_rpc_id,
                        service=url,
                        method=kwargs.pop("method", ""),
                        code=result_code,
                        remote_ip=remote_ip,
                        span=HandleArgs.pretty_string(span),
                        res_size=response_size,
                        ext_info=ext_info,
                        user_data=INITIAL_PARAMS.eagleeye_user_data
                        )

        else:
            INITIAL_PARAMS.eagleeye_trace_id = TraceIdGenerator.get_trace_id()
            INITIAL_PARAMS.eagleeye_rpc_id = RpcIdUpdater.update_rpc_id()
            rpc_type = "90"  # 自定义入口

            # 日志格式，自定义入口 traceId|timestamp|rpcType|span|rpcId|resultCode|traceName|extInfo|userData
            _message = "{trace_id}|{ts}|{type}|{span}|{rpc_id}|{code}|{trace_name}|{ext_info}|{user_data}".format(
                trace_id=INITIAL_PARAMS.eagleeye_trace_id,
                ts=HandleArgs.pretty_string(time_stamp),
                type=rpc_type,
                span=HandleArgs.pretty_string(span),
                rpc_id=INITIAL_PARAMS.eagleeye_rpc_id,
                code=HandleArgs.pretty_string(result_code),
                trace_name=HandleArgs.pretty_string(url),
                ext_info=ext_info,
                user_data=INITIAL_PARAMS.eagleeye_user_data

            )
        self.logger.info(_message)

    def client_log(self, **kwargs):
        """
        自定义客户端包括三类，
        RPC客户端 rpc_type为 91，
        存储客户端 rpc_type为 94，
        缓存客户端 rpc_type为 95
        """
        trace_id = INITIAL_PARAMS.eagleeye_trace_id
        rpc_type = kwargs.pop("rpc_type", "")
        if rpc_type == "91":
            rpc_id = INITIAL_PARAMS.eagleeye_rpc_id
        elif rpc_type in ["94", "95"]:
            rpc_id = RpcIdUpdater.update_rpc_id(INITIAL_PARAMS.eagleeye_rpc_id)
        user_data = INITIAL_PARAMS.eagleeye_user_data or ""
        time_stamp = kwargs.pop("start_time", "")
        url = kwargs.pop("url", "")
        service_name = kwargs.pop("service_name", None)
        if not service_name:
            service_name = url
        remote_ip = kwargs.pop("remote_ip", None)
        if not remote_ip:
            remote_ip = HandleArgs.get_remote_ip(url) or "0.0.0.0"
        gap = kwargs.pop("gap", "0")
        span = kwargs.pop("span", "")
        result_code = "00" if kwargs.pop("result_code", "") == 200 else "01"
        request_size = kwargs.pop("request_size", "")
        response_size = kwargs.pop("response_size", "")
        if not request_size or not response_size:
            request_size, response_size = HandleArgs.get_size(kwargs.pop('response', None))
        ext_info = kwargs.pop("ext_info", "")

        # 日志格式，自定义客户端 traceId|timestamp|rpcType|rpcId|serviceName|method|remoteIp|span|resultCode|
        # requestSize|responseSize|extInfo|userData
        _message = "{trace_id}|{ts}|{rpc_type}|{rpc_id}|{service}|{method}|{remote_ip}|[{gap},{span}]|{code}|" \
                   "{req_size}|{res_size}|{ext_info}|{user_data}".format(
                    trace_id=trace_id,
                    ts=HandleArgs.pretty_string(time_stamp),
                    rpc_type=rpc_type,
                    rpc_id=rpc_id,
                    service=service_name,
                    method=kwargs.pop("method", ""),
                    remote_ip=remote_ip,
                    gap=HandleArgs.pretty_string(gap),
                    span=HandleArgs.pretty_string(span),
                    code=result_code,
                    req_size=request_size,
                    res_size=response_size,
                    ext_info=ext_info,
                    user_data=user_data
                    )
        self.logger.info(_message)

    @staticmethod
    def transfer_eagleeye_params(header):
        INITIAL_PARAMS.eagleeye_rpc_id = RpcIdUpdater.update_rpc_id(INITIAL_PARAMS.eagleeye_rpc_id)
        eagleeye_header = {
            "EagleEye-TraceId": INITIAL_PARAMS.eagleeye_trace_id,
            "EagleEye-RpcId": INITIAL_PARAMS.eagleeye_rpc_id,
            "EagleEye-UserData": INITIAL_PARAMS.eagleeye_user_data
        }

        return header.update(eagleeye_header)
