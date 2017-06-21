# -*- coding: utf-8 -*-
import threading


class InitialParams(threading.local):
    """
    初始化链路日志线程变量
    """
    tracelogger_trace_id = None
    tracelogger_rpc_id = None
    tracelogger_user_data = None
    call_counter = 0

INITIAL_PARAMS = InitialParams()


class RpcIdUpdater(object):

    @staticmethod
    def update_rpc_id(rpc_id=None):
        try:
            if rpc_id:
                temp = INITIAL_PARAMS.call_counter
                temp += 1
                rpc_id = ".".join([rpc_id, str(temp)])
                INITIAL_PARAMS.call_counter = temp
            else:
                rpc_id = "0"
        except:
            rpc_id = "0"
        return rpc_id