---
layout: post
title: "D/Thrift GSoC: First results"
tags:
  - D
  - GSoC
  - Thrift
excerpt: "The first week of my Thrift project as part of the D programming language Google Summer of Code is over, and I am happy to be able to share some first results. If you are not sure what I am talking about yet"
---

The first week of my [_D/Thrift_ project](/code/gsoc/thrift/) as part of the [D programming language](http://d-programming-language.org) [Google Summer of Code 2011](http://www.google-melange.com/gsoc/org/google/gsoc2011/dprogramminglanguage) is over, and I am happy to be able to share some first results. If you are not sure what I am talking about yet: [Apache Thrift](http://thrift.apache.org), originally developed for internal use at [Facebook](http://facebook.com), is both a data serialization/RPC protocol and its reference implementation. In short, it works by defining data types and services interface in a language-agnostic interface definition file. Then, a compiler is used for generating code from that `.thrift` file (currently written in C++), using target language support libraries which contain the actual serialization protocol/RPC implementation. Currently, Thrift supports a large number of languages including C++, Java, PHP and Python.

It was clear from the beginning that I would stick with this approach for my implementation, not only because the informal project goal is to establish D as an equal target language besides the existing ones, but simply because one of the main strengths of Thrift is that you can use the same interface definition for all target languages, with the compiler doing all the heavy lifting for you. I did, however, want to leverage the powerful metaprogramming capabilities of D (compile-time reflection, CTFE, string mixins) to lift as much work off the »ahead-of-time« C++ code generator as possible, having the option to use the Thrift libraries beyond the traditional scope of the project for ad-hoc extension of existing D data types and interfaces with serialization/RPC functionality at the back of my mind.

My primary goal during the first week was to evaluate the feasibility of this approach by quickly implementing the basic parts of each Thrift component. In more detail, the sub-goals I tackled during the last week were:

 * Create a preliminary implementation the central parts of the support library (`TBinaryProtocol`, `TBufferedTransport`, `TSocket`, …) using the C++ and Java implementations as reference to be able to directly test the progressing D implementation against other languages.

 * Implement the general and client-specific parts of compile-time code generation (struct reading/writing, method arguments/result struct generation `TClient`, …), using a hand-crafted Thrift tutorial interface to test it against the Java server.

 * Implement `TSimpleServer` and related basic server functionality (e.g. `TServerSocket`) to be able to test server code generation.

 * Complete missing server-side code generation bits (`TProcessor`, server-side arguments/result structs, …), again using a hand-crafted interface to test it against the Java Thrift calculator tutorial client.

 * Add D code generation to the Thrift compiler, and run the compiler against all the test interface files coming with Thrift (`test/*.thrift`) to catch any obvious issues.

 * Implement a `ThriftTest` server and client in D to exercise the more advanced serialization code paths and fix any bugs, testing it against the C++ implementation.

So far, no major problems popped up, and I was able to complete the above list as planned. I did, however, hit a few bugs in DMD, which is, on the other hand, doesn't come as a total surprise because I am heavily using the metaprogramming facilities. I have been able to find workarounds for all of the issues, but it nevertheless took me quite some time to track them down initially: issues [6069](http://d.puremagic.com/issues/show_bug.cgi?id=6069), [6077](http://d.puremagic.com/issues/show_bug.cgi?id=6077), [6078](http://d.puremagic.com/issues/show_bug.cgi?id=6078), [DMD pull request 77](https://github.com/D-Programming-Language/dmd/pull/77) and – this one is merely an enhancement – [Phobos pull request 65](https://github.com/D-Programming-Language/phobos/pull/65).

If you want to have a look at the code, feel free to head to [my GitHub Thrift fork](https://github.com/dnadlinger/thrift/tree/d-gsoc), where I regularly push my work to. And just to give you a short glimpse of the very basic features (a lot more is already implemented), this is how you could implement a simple calculator server/client which adds two numbers using the Thrift library, without using any generated code.

{% codeblock lang:d Shared module containing the interface the server offers and the client consumes. %}
// This could also be generated from a .thrift file and contain
// structs, exceptions, etc.
module calculator;

interface Calculator {
  int add(int lhs, int rhs);
}
{% endcodeblock %}

{% codeblock lang:d Server implementation, accepting connections on port 9090 using the binary protocol. %}
module server;

import calculator;
import thrift.codegen.processor;
import thrift.protocol.binary;
import thrift.protocol.processor;
import thrift.server.simple;
import thrift.transport.buffered;
import thrift.transport.serversocket;

class CalculatorHandler : Calculator {
  override int add(int lhs, int rhs) {
    return n1 + n2;
  }
}

void main() {
  // Expose a CalculatorHandler instance at port 9090.
  auto protocolFactory = new TBinaryProtocolFactory();
  auto processor = new TServiceProcessor!Calculator(
    new CalculatorHandler());
  auto serverTransport = new TServerSocket(9090);
  auto transportFactory = new TBufferedTransportFactory();

  auto server = new TSimpleServer(
    processor, serverTransport, transportFactory, protocolFactory);
  server.serve();
}
{% endcodeblock %}

{% codeblock lang:d Client implementation. Note how the interface defined above in the <code>calculator</code> module is passed to TClient as a template parameter, which then generates the necessary RPC code. %}
module client;

import calculator;
import std.stdio;
import thrift.codegen.client;
import thrift.protocol.binary;
import thrift.transport.buffered;
import thrift.transport.socket;

void main() {
  // Set up a client for the Calculator interface and try to
  // connect to localhost:9090.
  auto socket = new TSocket("localhost", 9090);
  auto transport = new TBufferedTransport(socket);
  auto protocol = new TBinaryProtocol(transport);
  auto client = new TClient!Calculator(protocol);
  transport.open();

  // Call the server's add() method and print the result.
  auto lhs = 2;
  auto rhs = 3;
  auto sum = client.add(lhs, rhs);
  writefln("%s + %s = %s", lhs, rhs, sum);
}
{% endcodeblock %}

*[CTFE]: Compile Time Function Execution
