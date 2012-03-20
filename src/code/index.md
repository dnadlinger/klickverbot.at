---
layout: code
title: Code
next_title: d4
next_url: /code/d4
---

Code
====

<p class="lead">Ever since I started toying around with QBasic back when a single decimal digit was enough to express my age in years, I find computer programming, its nature at the intersection of raw computing power and creativity, to be deeply fascinating. This page features a woefully incomplete compilation of some of my projects.</p>

Originally, my motivation was mostly graphics programming and game development, but that has changed over the years – right now, my main interests are the dirty low-level magic of e.g. compiler writing on one hand and design of and algorithms for parallel and distributed computing on the other hand.

I believe that going open source is a viable and beneficial approach both for personal/not-for-profit projects as well as for many corporate products. But perhaps just as important as that, having reams of real-world code to peruse at their disposal is also a fantastic resource for people new to programming – at least, it has been for me, and I have been contributing to free software whenever time allowed ever since.

* _Apache Thrift:_ Having been offered the chance to participate in the [Google Summer of Code 2011](http://www.google-melange.com/gsoc/program/home/google/gsoc2011) program under the umbrella of [Digital Mars](http://digitalmars.com), I implemented [D support](/code/gsoc/thrift) for [Apache Thrift](http://thrift.apache.org), which is an open source serialization/RPC framework originally developed by Facebook. Feature-wise, the library can be considered to be on par with the established C++ and Java implementations, and it is currently [pending upstream inclusion](https://issues.apache.org/jira/browse/THRIFT-1500).

* _Assimp:_ The [Open Asset Import Library](http://assimp.sourceforge.net/) is a C/C++ library to load various 3D file formats, including Collada, 3DS, X, Obj, STL and others. Written by several members of the (German) [ZFX](http://zfx.info/) 3D graphics/game development community, I contributed D bindings and help with maintenance and the CMake build system.

* _D:_ The statically typed, C-style syntax [D programming language](http://dlang.org) pragmatically combines efficiency, control, and modeling power, with safety and programmer productivity. I discovered it when I started [d4](/code/d4), and have been involved with core language development for quite a while now – you will find my commits in the [reference compiler](http://github.com/D-Programming-Language/dmd), [low-level runtime](http://github.com/D-Programming-Language/druntime) and [standard libraries](http://github.com/D-Programming-Language/phobos). I also contributed two C library bindings to the [Deimos project](http://github.com/D-Programming-Deimos) and a few fixes to the [website](http://dlang.org). An important meta-goal of mine is to help building a healthy and vibrant community.

* _d4:_ Along with a [more or less scholarly paper](/science/3d-mathematics/) on the mathematical basics of realtime 3D rendering I wrote as part of my Matura exam (comparable to the British A levels), I designed and implemented [a simple software rasterizer](/code/d4) in the D programming language. It is mainly for demonstration purposes, but I still find the metaprogramming-based vertex and pixel shader design quite interesting.

* _KDE:_ I originally joined the ranks of [KDE](http://kde.org) committers to work on the stability of the then-new compositing support in KWin, KDE's window manager (at that time, [Compiz](http://en.wikipedia.org/wiki/Compiz) was all the craze, but didn't integrate particularly well with KDE). After experiencing for the first time the amount of hair-pulling shipping a beta to several thousand people can entail, I contributed several small fixes to other projects.

* _SWIG:_ The [Simple Wrapper Interface Generator](http://swig.org/) connects programs written in C and C++ with a variety of high-level programming languages. I implemented comprehensive support for the D programming language (both versions 1 and 2), which first shipped with SWIG 2.0.2.

Generally, I am a fan of [Git](http://git-scm.org), and you can find some more completed as well as some in-progress personal projects at my [GitHub account](http://github.com/klickverbot). From time to time, I also submit patches to other project to address a specific issue that is bugging me, ranging e.g. from [LLVM](http://llvm.org) over [Homebrew](http://mxcl.github.com/homebrew/) and [Mercurial](http://mercurial.selenic.com/) to [Wine](http://winehq.org).
