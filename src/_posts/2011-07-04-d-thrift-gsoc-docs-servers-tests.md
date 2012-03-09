---
layout: post
title: "D/Thrift: Docs, Servers, Tests"
tags:
  - D
  - GSoC
  - Thrift
excerpt: "Dear Reader, Let me apologize for not being terribly motivated to write a blog post right now, but I was lucky enough to catch the flu last week with temperatures between 25&thinsp;°C and 35&thinsp;°C outside, and while the fever has gone by now, I am still depleting my"
---

Dear Reader,

Let me apologize for not being terribly motivated to write a blog post right now, but I was lucky enough to catch the flu last week with temperatures between 25&thinsp;°C and 35&thinsp;°C outside, and while the fever has gone by now, I am still depleting my tissue stock at an insanely high rate…

Anyway, back to topic, the usual summary of the recent changes to my Thrift GSoC project:

 * The most important item on the list from an user point of view are probably the _documentation_ improvements: The project now has a [Getting Started page](https://github.com/klickverbot/thrift/wiki/Getting-Started-with-Thrift-and-D), and I have made a complete pass through all the DDoc docs, a build of which is [available here](http://klickverbot.at/code/gsoc/thrift/docs/) (I still have to whip up a nice design, but it should do for the moment).

 * More interesting from a coding perspective are the additions of two _new `thrift.server` implementations_, `TThreadedServer` and `TTaskPoolServer`. The former is a naive implementation of a threaded server which just spawns a new worker thread per client connection, while the latter uses a `std.parallelism` thread pool to process the queued client connections (the maximum number of active connections is configurable). I also added a D version of the `StressTest` server for sanity checking.

 * Another server-related change is the addition of server and processor _event handlers_, which can be used to hook custom code into various points during the server/request lifecycle, e.g. for collecting diagnostic data. Data can be persisted between the calls by saving them as connection/call »context«, which is a `Variant` the server code passes around for you (I went with variants over e.g. templating the server code on the context object type simply to avoid adding another layer of complexity for a non-essential feature).

 * I added a standalone test case exercising the different transport types (socket, file, memory buffer) combined with the various wrapper transports (buffered, framed), modeled after the C++ `TransportTest`. This has uncovered a number of (sometimes not-so-) subtle defects in the transport implementations which have been fixed (TSocket not handling `EINTR`, framed/memory buffer `borrow()` would also return smaller than requested, `TFileReaderTransport` not tailing files correctly, …).

 * Build system improvements: The stand-alone test cases are now organized in a much less cumbersome scheme, and DDoc documentation is generated for the library by default. `lib/d/README` now has instructions on how to generate a self-signed certificate for SSL socket testing.

If you are on OS X, you might want to manually apply [Phobos pull request 131](https://github.com/D-Programming-Language/phobos/pull/131) until it is merged into Git master to avoid your servers crashing due to an unhandled `SIGPIPE` (you can also just set `signal(SIGPIPE, …)` to `SIG_IGN` in your startup code).

I have also added a list of not yet scheduled ideas to the [project page](/code/gsoc/thrift/). Implementing a ZLib compression transport is currently the top item on my list, after which I will start to work on a non-blocking server implementation as planned. An asynchronous version of `TClient` is something I certainly want to implement, but I am planning to defer work on it until I have tackled the non-blocking server, as I could end up using the same approach (e.g. `libevent`) for it.
