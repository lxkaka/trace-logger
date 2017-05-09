# Python 鹰眼API

鹰眼相关说明可阅读文档[eagleeye-docs](http://gitlab.alibaba-inc.com/middleware/eagleeye-docs/wikis/eagleeye-custom-usage)

此模块实现了Python版本的鹰眼埋点API, 开发语言为Python的系统可调用本模块提供的API进行日志埋点。
实现以下功能：
* 生成鹰眼日志的trace_id
* 更新鹰眼日志的rpc_id
* 自定义入口埋点
* 自定义客户端埋点
* 自定义服务端埋点(包括自定义存储）

## 使用说明

### 日志简介
日志位置： 一般在 ~/logs/eagleeye/eagleeye.log 下面, 可自定义。
* EagleEye日志以竖线'|'分割
* EagleEye日志的前三个字段固定，含义为traceId|timestamp|rpcType|...
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
* userData：业务自定义数据，可选，[详细信息](http://gitlab.alibaba-inc.com/middleware/eagleeye-docs/wikis/eagleeye-core-userdata)

### 自定义入口
* 日志格式: traceId|timestamp|rpcType|span|rpcId|resultCode|traceName|extInfo|userData
rpc_type固定为90，不需要作为参数传入

* 调用API: `eagleeye.log_generator.EagleEyeLogger.entry_log`

* 调用示例:

```python
    _logger = logging.getLogger(EAGLEEYE_LOG)  # 注意这里的日志名字需要调用方按照自己系统的情况配置
    start_time = int(time.time() * 1000)
    url = "http://127.0.0.1:8080/test/kaka?pa=1&sign=abc"
    span = 20
    result_code = 200

    logger = EagleEyeLogger(self._logger)
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
EAGLEEYE_LOG = "eagleeye_log"
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
        EAGLEEYE_LOG: {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_ROOT, "../logs/eagleeye.log"),
            "formatter": "log_form",
            "when": "midnight",
        }
    },
    "loggers": {
        EAGLEEYE_LOG: {
            "handlers": [EAGLEEYE_LOG],
            "level": "INFO",
        }
    },
}
```

自定义入口我们一般使用url作为traceName

### 自定义服务端
* 日志格式：traceId|timestamp|rpcType|rpcId|serviceName|method|resultCode|remoteIp|span|responseSize|extInfo|userData
rpc_type固定为92，不需要作为参数传入
需要从请求头中取出透传的 **EagleEye-TraceId**, **EagleEye-RpcId**, **EagleEye-UserData**, 然后把相关参数传入调用的API
* 调用API: `eagleeye.log_generator.EagleEyeLogger.entry_log`

* 调用示例:

```python
_logger = logging.getLogger(EAGLEEYE_LOG)  # 注意这里的日志名字需要调用方按照自己系统的情况配置
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

自定义服务端我们一般使用url作为serviceName。remote_ip如果不传，会取url的host作为remote_ip, 默认为 "0.0.0.0"
关于response_size可以直接传入参数response_size，也可传入response对象，默认为0

### 自定义客户端
* 自定义客户端包括三类，
 - RPC客户端 rpc_type为 91
 - 存储客户端 rpc_type为 94
 - 缓存客户端 rpc_type为 95
* 日志格式：traceId|timestamp|rpcType|rpcId|serviceName|method|remoteIp|span|resultCode|requestSize|responseSize|extInfo|userData
如调用其他服务，rpc_type为 91。在整个调用链中，每次RPC调用需要透传EagleEye的TraceID、RpcID和用户数据等上下文信息
* 通过 http header 透传**EagleEye-TraceId**, **EagleEye-RpcId**, **EagleEye-UserData**

    调用API `eagleeye.log_generator.EagleEyeLogger.transfer_eagleeye_params`

    示例:

    ```python
    header = EagleEyeLogger.transfer_eagleeye_params(header)
    ```

* 调用API埋点：`eagleeye.log_generator.EagleEyeLogger.client_log`

调用示例:

```python
_logger = logging.getLogger(EAGLEEYE_LOG)  # 注意这里的日志名字需要调用方按照自己系统的情况配置
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

自定义客户端我们一般使用url作为serviceName。remote_ip如果不传，会取url的host作为remote_ip，默认为 "0.0.0.0"
关于response_size可以直接传入参数response_size，也可传入response对象，默认为0