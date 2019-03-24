---
layout: post
title: "D/Thrift GSoC: Growing the library"
tags:
  - D
  - GSoC
  - Thrift
excerpt: "First, let me apologize for not posting an update last week – I had a busy time, but regardless I will try to let you know about the state of affairs regularly in the future. Now, what were I working on? I updated"
---

First, let me apologize for not posting an update last week – I had a busy time, but regardless I will try to let you know about the state of affairs regularly in the future. Now, what were I working on? I updated my [project page](/code/gsoc/thrift/) based on the timeline previously discussed at my project mailing list, and – besides me being a day late, more below – it is still valid. These were the main points I worked on:

 * _Build system integration_: The D library is now integrated with the Thrift Autoconf/Automake build system. If a working D2 compiler is detected, the `libthriftd` static library containing all the modules is now built on issuing `make` along with the rest of Thrift. `make check` runs the unit tests for each D module and builds the standalone test executables (i.e. `ThriftTest` for now).

 * _Socket transport enhancements_: Implemented `interrupt()` for the server socket which can be used to notify a server waiting on a blocking socket for connections about shutdown, added socket timeouts, properly handle exceptions thrown by `std.socket`, …

 * Added a D implementation of _`TMemoryBuffer`_, which is widely internally used and a nice tool for writing unit tests as well. Implemented the _Framed_ transport in D.

 * Implemented _`TFileReaderTransport`_ and _`TFileWriterTransport`_, the D equivalent to the C++ `TFileTransport`. I separated the two components because I could not really think of a situation in which you would use both at once, and conflating the two would complicate the state space (I am not even sure if the C++ implementation does what it is supposed to if read/write calls are interleaved) and make the implementation unnecessarily complex. The `TFileWriterTransport` implementation performs the actual file I/O in a separate worker thread, which communicates with the main thread using a message passing approach (leveraging D's `std.concurrency` module).

 * A simple _HTTP client/server transport_, closely modeled after the C++ implementation.

 * An _SSL client/server socket_ implementation using the OpenSSL library, which is linked in dynamically (primarily for easy Windows compatibility). The actual implementation is pretty much a direct port of the C++ `TSSLSocket`, but I had to quickly write the D2 bindings for OpenSSL first. For now, the bindings live in `thrift.util.openssl`, as I only included the subset of functions I needed for Thrift, but I might move them out in the future.

As always, you can find the changes [on my GitHub fork](https://github.com/dnadlinger/thrift). I also spent a sizable chunk of my time on contributing some improvements and fixed to the D compiler and standard library projects. As for the issues I mentioned two weeks ago, kudos to Don Clugston for promptly fixing CTFE issues [6077](http://d.puremagic.com/issues/show_bug.cgi?id=6077) and  [6078](http://d.puremagic.com/issues/show_bug.cgi?id=6078), and my [DMD pull request 77](https://github.com/D-Programming-Language/dmd/pull/77) and [Phobos pull request 65](https://github.com/D-Programming-Language/phobos/pull/65) were also merged in the meantime.

During the last two weeks, I worked on Phobos pull requests [73](https://github.com/D-Programming-Language/phobos/pull/73) (adds `std.socket.socketpair`), [87](https://github.com/D-Programming-Language/phobos/pull/87) (better `std.file` error messages), [90](https://github.com/D-Programming-Language/phobos/pull/90) (fixes a mailbox handling bug in `std.concurrency` – took me quite some time to track down as it caused sporadic deadlocks in my unit tests), [99](https://github.com/D-Programming-Language/phobos/pull/99) (adds timeout handling and hostname lookup to `std.socket` – I still don't know why WinSock adds 500 ms to the `recv()` timeout), [druntime pull request 28](https://github.com/D-Programming-Language/druntime/pull/28) (adds a Posix `netdb.h` module) and [DMD pull request 118](https://github.com/D-Programming-Language/dmd/pull/118) (finally removes the `_DH` flag).

Furthermore, I collaborated with Daniel Murphy on fixing the long-standing issue that function pointers are not properly typechecked, resulting in [DMD pull request 96](https://github.com/D-Programming-Language/dmd/pull/96) and [druntime pull request 26] (https://github.com/D-Programming-Language/druntime/pull/26). I have also started to work the dreaded DMD [bug 314](http://d.puremagic.com/issues/show_bug.cgi?id=314). While the basic fix is in place – that's how I found the bug in [Phobos pull request 102](https://github.com/D-Programming-Language/phobos/pull/102) – (I adapted the D1/LDC changes by Christian Kamm to D2/DMD), I still need to add some more tests and solve a few more complex cases. Unfortunately, I also hit two new issues which I have not been able to fix yet: [6108](http://d.puremagic.com/issues/show_bug.cgi?id=6108), a DMD contract inheritance bug, and [6135](http://d.puremagic.com/issues/show_bug.cgi?id=6135), a druntime OSX threading/GC crash.
