# Python 链路日志API

此模块实现了Python版本的链路日志埋点API, 开发语言为Python的系统可调用本模块提供的API进行日志埋点。
实现以下功能：
* 生成链路日志的trace_id
* 更新链路日志的rpc_id
* 自定义入口埋点
* 自定义客户端埋点
* 自定义服务端埋点(包括自定义存储）

## 使用说明

### 日志简介
* 日志以竖线'|'分割
* 日志的前三个字段固定，含义为traceId|timestamp|rpcType|...
* 不同rpcType对应日志的余下字段个数、含义及顺序会略有不同
日志示例：1e1cb47b14942139800801000dda2d|1494213980080|91|0.1|http://127.0.0.1:8080/test/kaka?pa=1&sign=abc||127.0.0.1|[0,20]|00|123|321|||

### 字段含义
* traceId：全局唯一的Id，用作整个链路的唯一标识与组装
* timestamp：调用的开始时间
* rpcType：Rpc调用类型标示
* rpcId：用来标示 RPC 调用层次关系
* serviceName：调用的服务名（可能已编码）
* method：调用的方法名（可能已编码）
* remoteIp：対端地址(默认为0.0.0.0)
* span：记录的是调用的时间偏移量，毫秒为单位，有两种格式：[a,b](客户端类型)或者是一个数字c(服务端类型)，a=调用开始到客户端发送请求的时间差，b=调用开始到收到响应的时间差，c=处理时间
* resultCode：标示rpc调用成功或者失败，一般00表示成功，01表示失败，[详细信息]
* requestSize：客户端请求的大小(默认为0)
* responseSize：服务端响应的大小(默认为0)
* extInfo：用户附加的扩展数据，可选
* userData：业务自定义数据，可选

### 自定义入口
* 日志格式: traceId|timestamp|rpcType|span|rpcId|resultCode|traceName|extInfo|userData
rpc_type固定为90，不需要作为参数传入

* 调用API: `trace_logger.log_generator.TraceLogger.entry_log`

* 调用示例:

```python
    _logger = logging.getLogger(TRACE_LOG)  # 注意这里的日志名字需要调用方按照自己系统的情况配置
    start_time = int(time.time() * 1000)
    url = "http://127.0.0.1:8080/test/kaka?pa=1&sign=abc"
    span = 20
    result_code = 200

    logger = TraceLogger(self._logger)
    logger.entry_log(                     # 其他参数根据需要进行传递
        start_time=start_time,
        url=url,
        span=span,
        result_code=result_code,
        ext_info=ext_info,
        user_data=user_data,
    )
```

* 日志配置示例:

```python
import os
LOG_ROOT = os.path.abspath(os.path.dirname(__file__))
TRACE_LOG = "trace_log"
log_conf = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "log_form": {
            "format": "%(message)s"
        }
    },
    "filters": {},
    "handlers": {
        Trace_LOG: {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_ROOT, "../logs/tracelogger.log"),
            "formatter": "log_form",
            "when": "midnight",
        }
    },
    "loggers": {
        TRACE_LOG: {
            "handlers": [TRACE_LOG],
            "level": "INFO",
        }
    },
}
```

自定义入口我们一般使用url作为traceName

### 自定义服务端
* 日志格式：traceId|timestamp|rpcType|rpcId|serviceName|method|resultCode|remoteIp|span|responseSize|extInfo|userData
rpc_type固定为92，不需要作为参数传入
需要从请求头中取出透传的 **TraceLogger-TraceId**, **TraceLogger-RpcId**, **TraceLogger-UserData**, 然后把相关参数传入调用的API
* 调用API: `trace_logger.log_generator.TraceLogger.entry_log`

* 调用示例:

```python
_logger = logging.getLogger(TRACE_LOG)  # 注意这里的日志名字需要调用方按照自己系统的情况配置
    start_time = int(time.time() * 1000)
    url = "http://127.0.0.1:8080/test/kaka?pa=1&sign=abc"
    span = 20
    result_code = 200

logger.entry_log(                          # 其他参数根据需要进行传递
            trace_id=trace_id,
            rpc_id=rpc_id,
            start_time=start_time,
            url=url,
            method="post",
            span=span,
            result_code=result_code,
            remote_ip=remote_ip,
            response_size="216",
            ext_info=ext_info,
            user_data=user_data,
        )
```

自定义服务端我们一般使用url作为serviceName。remote_ip如果不传，会取url的host作为remote_ip, 默认为 "0.0.0.0"。
关于response_size可以直接传入参数response_size，也可传入response对象，默认为0

### 自定义客户端
* 自定义客户端包括三类，
 - RPC客户端 rpc_type为 91
 - 存储客户端 rpc_type为 94
 - 缓存客户端 rpc_type为 95
* 日志格式：traceId|timestamp|rpcType|rpcId|serviceName|method|remoteIp|span|resultCode|requestSize|responseSize|extInfo|userData
如调用其他服务，rpc_type为 91。在整个调用链中，每次RPC调用需要透传TraceID、RpcID和用户数据等上下文信息
* 通过 http header 透传**TraceLogger-TraceId**, **TraceLogger-RpcId**, **TraceLogger-UserData**

    调用API `trace_logger.log_generator.TRACELogger.transfer_tracelogger_params`

    示例:

    ```python
    header = TraceLogger.transfer_tracelogger_params(header)
    ```

* 调用API埋点：`trace_logger.log_generator.TraceLogger.client_log`

调用示例:

```python
_logger = logging.getLogger(Trace_LOG)  # 注意这里的日志名字需要调用方按照自己系统的情况配置
    start_time = int(time.time() * 1000)
    url = "http://127.0.0.1:8080/test/kaka?pa=1&sign=abc"
    span = 20
    result_code = 200

logger.entry_log(                          # 其他参数根据需要进行传递
            rpc_type = "91",
            start_time=start_time,
            url=url,
            method="get",
            gap=10,                         #  调用开始到客户端发送请求的时间差
            span=span,                     #  调用开始到收到响应的时间差
            result_code=result_code,
            remote_ip=remote_ip,
            request_size="123",
            response_size="321",
            ext_info=ext_info,
            user_data=user_data,
        )
```

自定义客户端我们一般使用url作为serviceName。remote_ip如果不传，会取url的host作为remote_ip，默认为 "0.0.0.0"。
关于response_size可以直接传入参数response_size，也可传入response对象，默认为0

## 完整使用示例

```python
# -*- coding: utf-8 -*-
import time
import logging
from trace_logger import TraceLogger


# 生成链路日志埋点实例，参数为logging库配置的logger对象。(配置可参考logger_configuration)
# 也可以实现info方法，用任意的文件对象记录日志
_logger = logging.getLogger('trace_log')
start_time = int(time.time() * 1000)
url = 'http://127.0.0.1:8080/test/kaka?pa=1&sign=abc'
span = 20  # 调用开始到收到响应的时间差
result_code = 200
logger = TraceLogger(_logger)
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
# 首先更新rpc_id, 更新请求头。通过 http header 透传TraceLogger-TraceId, TraceLogger-RpcId, TraceLogger-UserData
header = None  # http请求头
header = TraceLogger.transfer_tracelogger_params(header)
rpc_type = '91'
gap = '5'  # 调用开始到客户端发送请求的时间差
logger.client_log(rpc_type=rpc_type, start_time=start_time, span=span, url=url, method=method, gap=gap,
                  result_code=result_code, response=response, ext_info=ext_info, user_data=user_data)

```