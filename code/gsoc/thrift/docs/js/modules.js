var g_moduleList = [
  "thrift.base", "thrift.async.base", "thrift.async.libevent",
  "thrift.async.socket", "thrift.async.ssl", "thrift.codegen.async_client",
  "thrift.codegen.async_client_pool", "thrift.codegen.base",
  "thrift.codegen.client", "thrift.codegen.client_pool",
  "thrift.codegen.idlgen", "thrift.codegen.processor", "thrift.protocol.base",
  "thrift.protocol.binary", "thrift.protocol.compact", "thrift.protocol.json",
  "thrift.protocol.processor", "thrift.server.base", "thrift.server.simple",
  "thrift.server.nonblocking", "thrift.server.taskpool",
  "thrift.server.threaded", "thrift.server.transport.base",
  "thrift.server.transport.socket", "thrift.server.transport.ssl",
  "thrift.transport.base", "thrift.transport.buffered",
  "thrift.transport.file", "thrift.transport.framed", "thrift.transport.http",
  "thrift.transport.memory", "thrift.transport.piped",
  "thrift.transport.range", "thrift.transport.socket", "thrift.transport.ssl",
  "thrift.transport.zlib", "thrift.util.awaitable", "thrift.util.cancellation",
  "thrift.util.future", "thrift.util.hashset",
];

var g_packageTree = new PackageTree(P('', [
  P('thrift',[
    P('thrift.async',[
      M('thrift.async.base'),
      M('thrift.async.libevent'),
      M('thrift.async.socket'),
      M('thrift.async.ssl'),
    ]),
    P('thrift.codegen',[
      M('thrift.codegen.async_client'),
      M('thrift.codegen.async_client_pool'),
      M('thrift.codegen.base'),
      M('thrift.codegen.client'),
      M('thrift.codegen.client_pool'),
      M('thrift.codegen.idlgen'),
      M('thrift.codegen.processor'),
    ]),
    P('thrift.protocol',[
      M('thrift.protocol.base'),
      M('thrift.protocol.binary'),
      M('thrift.protocol.compact'),
      M('thrift.protocol.json'),
      M('thrift.protocol.processor'),
    ]),
    P('thrift.server',[
      P('thrift.server.transport',[
        M('thrift.server.transport.base'),
        M('thrift.server.transport.socket'),
        M('thrift.server.transport.ssl'),
      ]),
      M('thrift.server.base'),
      M('thrift.server.nonblocking'),
      M('thrift.server.simple'),
      M('thrift.server.taskpool'),
      M('thrift.server.threaded'),
    ]),
    P('thrift.transport',[
      M('thrift.transport.base'),
      M('thrift.transport.buffered'),
      M('thrift.transport.file'),
      M('thrift.transport.framed'),
      M('thrift.transport.http'),
      M('thrift.transport.memory'),
      M('thrift.transport.piped'),
      M('thrift.transport.range'),
      M('thrift.transport.socket'),
      M('thrift.transport.ssl'),
      M('thrift.transport.zlib'),
    ]),
    P('thrift.util',[
      M('thrift.util.awaitable'),
      M('thrift.util.cancellation'),
      M('thrift.util.future'),
      M('thrift.util.hashset'),
    ]),
    M('thrift.base'),
  ]),
])
);

var g_creationTime = 1328741250;
