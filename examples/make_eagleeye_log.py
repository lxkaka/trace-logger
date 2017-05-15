# -*- coding: utf-8 -*-
import time
import logging
from eagleeye import EagleEyeLogger


# 生成鹰眼埋点实例，参数为logging库配置的logger对象。(配置可参考logger_configuration)
# 也可以实现info方法，用任意的文件对象记录日志
_logger = logging.getLogger('eagleeye_log')
start_time = int(time.time() * 1000)
url = 'http://127.0.0.1:8080/test/kaka?pa=1&sign=abc'
span = 20  # 调用开始到收到响应的时间差
result_code = 200
logger = EagleEyeLogger(_logger)
response = None
remote_ip = '192.168.1.1'
method = 'post'

# 请求入口埋点
logger.entry_log(start_time=start_time, span=span, url=url, result_code=result_code)

# 自定义服务端埋点
# 我们一般使用url作为serviceName。remote_ip如果不传，会取url的host作为remote_ip, 默认为 "0.0.0.0"
# 关于response_size可以直接传入参数response_size，也可传入response对象，默认为0
trace_id = '1e1cb3e014948226556311001d568a'
rpc_id = '0.1'
ext_info = 'ext_info_example'
user_data = '@@rpcName0x14RPC0x12i0x147325abff0x12'
response_size = '122'
logger.entry_log(trace_id=trace_id, rpc_id=rpc_id, start_time=start_time, span=span, url=url, method=method,
                 result_code=result_code, response=response, ext_info=ext_info, user_data=user_data)

# 自定义客户端埋点
# 我们一般使用url作为serviceName。remote_ip如果不传，会取url的host作为remote_ip，默认为 "0.0.0.0"
# 关于request_size, response_size可以直接传入参数，也可传入response对象，默认为0
# 首先更新rpc_id, 更新请求头。通过 http header 透传EagleEye-TraceId, EagleEye-RpcId, EagleEye-UserData
header = None  # http请求头
header = EagleEyeLogger.transfer_eagleeye_params(header)
rpc_type = '91'
gap = '5'  # 调用开始到客户端发送请求的时间差
logger.client_log(rpc_type=rpc_type, start_time=start_time, span=span, url=url, method=method, gap=gap,
                  result_code=result_code, response=response, ext_info=ext_info, user_data=user_data)
