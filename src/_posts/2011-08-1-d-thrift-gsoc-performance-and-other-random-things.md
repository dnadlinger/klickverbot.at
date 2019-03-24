---
layout: post
title: "D/Thrift: Performance and other random things"
tags:
  - D
  - GSoC
  - Thrift
excerpt: "This week, I will try to keep the post short, while still informative – I spent way too much time being unproductive due to hard to track down bugs already to be in the mood for writing up extensive ramblings. So, on to the meat of the recent changes (besides the usual little cleanup commits here and there)"
---

This week, I will try to keep the post short, while still informative – I spent way too much time being unproductive due to hard to track down bugs already to be in the mood for writing up extensive ramblings. So, on to the meat of the recent changes (besides the usual little cleanup commits here and there):

 * _Async client design_: Yes, even though it took me quite some time to come up with the original one, I had completely missed the fact that it would be unreasonably difficult to extend the support code with resource types other than sockets – long story short, `TAsyncSocketManager` now inherits from `TAsyncManager`, instead of being a part of it. Also, I split `TFuture` into two parts, a `TFuture` interface for accessing the result, and a `TPromise` implementation for actually setting/storing it, and only the `TFuture` part is returned from the async client methods. The [thrift.async docs](/code/gsoc/thrift/docs/thrift.async.base.html) are actually useful now.

 * _Async socket timeouts_: Correctly handling the state of the connection after a `read`/`write` timeout turned out to be a surprisingly tough problem to solve (allowing other request to be executed on the same connection after a timeout could lead to strange results). In the end, I settled for just closing the connection, which is a simple yet effective solution. To correctly implement this, I also had to finally kill the `TTransport.isOpen` related contracts and replace them with exceptions in the right places, leading to modified/clarified _`isOpen` semantics_.

 * The _non-blocking server_ now handles one-way calls correctly, and modifying the task pool after it is running no longer leads to undefined results. In the process, I have also turned the static `event` struct allocations into dynamic ones, since this should have no measurable performance impact, but removes the dependence on the (unstable, per the `libevent` docs) struct layout.

 * D now also has a `TPipedTransport`, which forwards a copy of all data read/written to another transport, useful e.g. for logging requests/responses to disk.

 * The biggest chunk of time was actually spent on _performance investigations_: While I was pretty certain that the D serialization code should not perform any worse than its C++ counterpart already, the difference in speed merely being compiler-dependent, I wanted to prove this fact so that I could cross this item from the list. This involved updating [LDC](http://dsource.org/projects/ldc) to the 2.054 frontend (only to discover that Alexey Prokhin decided to start work on it at the same time I did, the related commits in the [main repository](https://bitbucket.org/lindquist/ldc) are his now), fixing some LDC-specific druntime bugs, etc<sup class="footnote" id="fnr1"><a href="#fn1">1</a></sup>. Unfortunately, I couldn't test GDC because of [issue 6411](http://d.puremagic.com/issues/show_bug.cgi?id=6411), but without further ado, here are the results:

<figure>
  <table class="firstname">
    <thead>
      <tr>
        <th>&nbsp;</th>
        <th>Writing / kHz</th>
        <th>Reading / kHz</th>
      </tr>
    </thead>
    <tbody>
      <tr class="odd">
        <td>DMD v2.054, -O -release -inline</td>
        <td>2&thinsp;051</td>
        <td>1&thinsp;030</td>
      </tr>
      <tr>
        <td>GCC 4.6.1 (C++), -O2, templates</td>
        <td>5&thinsp;667</td>
        <td>1&thinsp;050</td>
      </tr>
      <tr class="odd">
        <td>LDC, -O3 -release</td>
        <td>2&thinsp;300</td>
        <td>1&thinsp;077</td>
      </tr>
      <tr>
        <td>LDC, -output-ll / opt -O3</td>
        <td>5&thinsp;500</td>
        <td>3&thinsp;150</td>
      </tr>
      <tr class="odd">
        <td>LDC, -output-ll / opt -std-compile-opts</td>
        <td>6&thinsp;700</td>
        <td>1&thinsp;950</td>
      </tr>
    </tbody>
  </table>
</figure>

At this point, I will disregard my earlier resolution and again get into the nitty-gritty details – the rest of this post can easily be summarized as _the D version is indeed up to par with C++, when it is equally well optimized_, but if you are curious about the details, read on.

If you read the performance figures from my last post, the first thing you will probably notice is that the C++ reading performance figure is about four times lower now. This isn't a mistake; noting the comparatively slim advantage of the C++ version, I made a [change](https://github.com/dnadlinger/thrift/commit/e7ab6c3b14b31c0241a1d37e674d3fefcbb53276) to it quite some time ago, which avoids allocating a new `TMemoryBuffer` instance on every loop iteration (the D version also reuses it). Without really considering the implications, though, I also moved the construction of the `OneOfEach` struct out of the loop. This seemed like a minor detail to me, but in fact, it enabled reuse of the `std::string`-internal buffers for the string members of the struct, which is unrealistic (e.g. for a pretty similar situation in the non-blocking server, there is no buffer reuse possible as well).

In a situation where a big part of the time is spent actually allocating and copying around memory, this makes a big difference. To test this assumption about the big influence of memory allocations, I compiled a version of the D benchmark where a static buffer for the strings was used instead of reallocating them every time, and indeed, the reading performance was more than twice as high.

The `std::string` implementation of the GCC STL seems to be fairly inefficient in this case, because the best D result (which uses GC-allocated memory), is almost three times faster than it for the reading part. It is possible that there are some further optimizations which could improve performance (`-O3` didn't change things for the better, in case you are wondering), but as my goal wasn't to squeeze every last bit of performance out of this synthetic benchmark, I didn't investigate this issue any further.

But now to the D results: Simply switching to LDC 2 instead of DMD didn't give any great speedups, because `readAll()` wasn't inlined by it either, thus leaving all the memory copying unoptimized, as discussed in the last post. To see how much of a difference this would really make, I compiled the D code to LLVM IR files and manually ran the optimizer/code generator/linker on them, with the plan being to manually add the `alwaysinline` attribute to the relevant pieces of IR:

<figure><pre><code>ldc2 -c -output-ll -oq -w -release -I../src -Igen-d ….d
llvm-link *.ll -o benchmark.bc
opt {-O3, -std-compile-opts} benchmark.bc -o benchmark_opt.bc
llvm-ld -native -llphobos2 -ldl -lm -lrt benchmark_opt.bc
</code></pre></figure>

I then discovered that the method calls in question were properly inlined by the stand-alone `opt` without any manual intervention anyway. I am not really sure why this happens; the inliner cost limits could be more liberal in this case, or the optimization passes being scheduled in a different way than inside LDC could have an impact, or maybe it's connected to the fact that `TMemoryBuffer` and the caller are in different modules (to my understanding, LTO _shouldn't_ be required to optimize in this case, but it may well be that I am mistaken here).

The `LDC -output-ll` rows in the above table correspond to the benchmark compiled this way, with the `-std-compile-opts` and `-O3` flags passed to `opt`, respectively. This is a nice example of how important compiler optimizations for this, again, synthetic benchmark really are: for the reading part of the benchmark, `-O3` gives a nice speed boost because of the more aggressive inlining (`-std-compile-opts` doesn't touch `TBinaryProtocol.readFieldBegin()`, which is called 15 times per loop iteration and contains some code that can completely be optimized out), but for the writing part, its result is actually _slower_, presumably because of locality effects (the call graphs are identical).

The only change related to benchmark performance I made since the last post was an LDC-specific workaround to stop manifest constants from incorrectly being leaked from the CTFE codegen process into the writing functions. I think the above results are justification enough to stop worrying about raw serialization performance – the results when using the Compact instead of the Binary protocol are similar – and moving on to more important topics<sup class="footnote" id="fnr2"><a href="#fn2">2</a></sup>.

<p class="footnote" id="fn1"><a href="#fnr1"><sup>1</sup></a> <s>If you are curious about LDC 2, you can get the source I used from the <a href="https://bitbucket.org/lindquist/ldc">official hg repo</a>, and the LDC-specific <a href="https://github.com/dnadlinger/druntime/tree/ldc2">druntime</a> and <a href="https://github.com/dnadlinger/phobos/tree/ldc2">Phobos</a> source from my clones at GitHub</s>. LDC is <a href="https://github.com/ldc-developers/ldc">officially on GitHub</a> now.</p>

<p class="footnote" id="fn2"><a href="#fnr2"><sup>2</sup></a> Such as performance-testing the actual server implementations, but I don't expect any big surprises there, and I am not sure how to reliably benchmark the network-related code – running server and clients on the same machine is probably a bad idea?</p>
