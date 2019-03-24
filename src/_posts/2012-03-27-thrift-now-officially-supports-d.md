---
layout: post
title: Thrift now officially supports D!
tags:
  - D
  - GSoC
  - Thrift
excerpt: "Thrift is a cross-language serialization and RPC framework, originally developed for internal use at Facebook, and now an Apache Software Foundation project. I started implementing support for the D programming language during Google Summer of Code 2011"
---

<p class="lead" markdown="1">[Thrift](http://thrift.apache.org) is a cross-language serialization and RPC framework, originally developed for internal use at Facebook, and now an [Apache Software Foundation](http://apache.org) project. I started working on support for the [D programming language](http://dlang.org) during [Google Summer of Code 2011](http://www.klickverbot.at/code/gsoc/thrift/), and at the end of last week, the implementation was finally incorporated into the main project.</p>

First, let me thank Jake Farrell and everybody else on the Thrift team who was involved in [THRIFT-1500](https://issues.apache.org/jira/browse/THRIFT-1500); reviewing a ~719&thinsp;kB patch certainly isn't an easy thing to do. But now that the work is in, what can you (as a Thrift user) expect from the implementation?

Feature-wise, the library should roughly be up to par with the other major implementations (i.e. C++ and Java):

<ul>
  <li><p><em>Protocols:</em> Binary, Compact and JSON. The Dense protocol has not been implemented yet – it is only supported by the C++ implementation and I am not sure about its relevance nowadays (but if you are at a certain well-known company and it turns out that you still need the feature for new projects, let me know; adding support for it should not be hard).</p></li>
  <li><p><em>Transports:</em> Socket, SSL, HTTP and log file reader/writer implementations (plus your familiar helpers, i.e. buffered/framed/memory-buffer/piped/zlib...)</p></li>
  <li><p><em>Servers:</em> several single- and multithreaded variants (including a libevent-based non-blocking implementation)</p></li>
  <li><p><em>Clients:</em> Both a synchronous and an asynchronous (future-based interface with one or more libevent-backed worker threads) implementation are provided. Additionally, several pooling implementations for redundancy as well as aggregation use cases are available.</p></li>
</ul>

The implementation makes heavy use of D's metaprogramming capatibilties and is also able to work without code generated off-line from `.thrift` files, if so desired. There are also a few experimental gimmicks, such as the capatibility to generate Thrift IDL files from existing D types at compile time. Soon to come:

<ul markdown="1">
  <li><p><em>Unix domain sockets:&nbsp;</em> Currently, the D implementation only supports IPv4 and IPv6 TCP sockets, because that is what the D standard library does, but starting with the next release, it will also support Unix domain sockets (if really needed, the lack of support in `std.socket` could be worked around without much effort, though).</p></li>
  <li><p><code>@safe</code><em>-ty annotations:&nbsp;</em> The D language features built-in memory safety annotations. The majority of the methods in the D Thrift library should be memory safe (except for e.g. `TTransport.borrow`), so marking it as such allowed Thrift to be used in D programs where safety is enforced without requiring the user to mark the Thrift calls as `@trusted`.</p></li>
</ul>

So, how to get started? As said above, the source code has been mergerd from my [personal GitHub repo](https://github.com/dnadlinger/thrift) to the `trunk` of the [main ASF repo](http://thrift.apache.org/developers/), and as soon as the currently ongoing rework of the official Thrift site is completed, the [Getting Started with Thrift and D](https://github.com/dnadlinger/thrift/wiki/Getting-Started-with-Thrift-and-D) and [Building Thrift/D on Windows](https://github.com/dnadlinger/thrift/wiki/Building-Thrift-D-on-Windows) pages will follow along. A recent build of the [API docs](http://www.klickverbot.at/code/gsoc/thrift/docs/) is currently available here on my website. If you find any bugs, be sure to file them at the [Thrift JIRA](https://issues.apache.org/jira/browse/THRIFT).
