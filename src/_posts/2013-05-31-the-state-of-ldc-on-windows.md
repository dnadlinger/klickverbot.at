---
layout: post
title: "The State of LDC on Windows"
tags:
 - D
 - LDC
excerpt: "LDC is one of the three major D compilers. It uses the same frontend as DMD, the reference implementation of the language, but leverages LLVM for optimization and code generation. While it has been stable on Linux and OS&nbsp;X for quite some time"
---

<p class="lead" markdown="1">LDC is one of the three major D compilers. It uses the same frontend as DMD, the reference implementation of the language, but leverages LLVM for optimization and code generation. While it has been stable on Linux and OS&nbsp;X for quite some time, support for the Windows operating system family was virtually non-existent so far. There have been substantial advances recently, and this post gives an overview of the current situation.</p>

Before going on to discuss the present status, though, let me quickly answer the inevitable question: Why did it take so long? It is not that the importance of Windows as a target platform would not have been recognized by the D community (or the LDC contributors in particular). Instead, the reason for the lack on of a working Windows port was caused by the fact that LLVM itself did not support all the required operating system specific features.  Notably, exception handling was not implemented at all on Windows for a long time.

This applies to 32-bit variants of Windows (*Win32*) as well as to the newer 64-bit operating systems (*Win64*), but interestingly the reasons for this are completely different. In the latter case, the problem was just that nobody took the time to implement the (table-driven) Win64 exception handling scheme in the LLVM backend. This is not so surprising, as most of the big companies sponsoring LLVM development are not using LLVM on Windows, or in an application domain that does not require features such as native exception handling or thread-local storage support.

However, Kai Nacke has tackled this problem recently, among with a number of other LLVM issues blocking development of the Visual Studio-based Win64 port of LDC. A patch fixing the bulk of the bugs in the exception handling implementation is currently under review on the LLVM development mailing list, and Kai has [prepared a binary preview version of LDC](http://forum.dlang.org/post/vscpokspiejlckivqsuq@forum.dlang.org) with all the latest patches. For more information, you can also visit the [Building and hacking LDC on Windows using MSVC](http://wiki.dlang.org/Building_and_hacking_LDC_on_Windows_using_MSVC) page on the LDC wiki.

The rest of this post will discuss the situation specifically on Win32/MinGW. Here, the root problem is that Structured Exception Handling (*SEH*), the default exception handling mechanism on 32-bit Windows, is covered by a [Borland-held patent](http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&d=PALL&p=1&u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&r=1&f=G&l=50&s1=5,628,016.PN.&OS=PN/5,628,016&RS=PN/5,628,016). It will not expire until next year, and while Borland seems to dismiss any related concerns, the GCC and LLVM projects have decided to not include an implementation of SEH in their compiler backends for fear of legal trouble.

Recently, however, support for DWARF 2-style exception handling appeared in GCC/MinGW. Here, the Windows-"native" SEH is forgone for the same table-based exception handling scheme that is also used on Linux.	The downside of this approach is obviously that it doesn't integrate with SEH exceptions raised by the OS or other C libraries. But even if it is theoretically possible to catch those from D, this (DMD) feature isn't really used widely, and as such virtually all D projects should be oblivious to the exception handling mechanism used under the hood.


Status Overview
---------------

So, what can you expect from LDC on Win32/MinGW today? First, the good parts:

* _Exception handling_ works, and all the related test cases that also pass on the various Posixen also pass on Win32/MinGW. Why this qualification? Just like GDC, LDC unfortunately doesn't implement all the fine details of D's exception chaining mechanism on any platform yet.

* _Thread-local storage (TLS)_ support is solid. Seeing this item on the list might surprise you, as TLS is central to each and every D2 application. However, it regularly turns out to be a pain point when porting D to new platforms, as it is typically not so important for other native languages. Thus, the related parts of the toolchains are typically less well tested, and LLVM on MinGW unfortunately was no exception here. At this point, however, my fixes to TLS support have arrived in the upstream versions of both mingw-w64 and LLVM, so no custom patches are required any longer (this is also the reason why LDC requires a very recent version of both).

* The _DMD, druntime and Phobos_ test suites mostly pass, and some smaller applications I tested build and work just fine. This notably includes most functionality associated with 80-bit `real`s (aka `long double`), which is notoriously problematic as the Microsoft Visual C/C++ runtime (*MSVCRT*) does not support this type of floating point numbers at all.

* LDC is sufficiently ABI-compatible to DMD on 32-bit Windows that virtually all of the inline assembly code in druntime and Phobos works without changes. This only covers a surprisingly small part of the total ABI though, so even if DMD emitted COFF object files, it would still be a hopeless endeavor to try and link object files produced by the two compiles together, just as it is on the other operating systems.

Now, for the less pleasant points:

* There are still a few issues related to floating-point math, particularly with complex 80-bit numbers. Single tests in `std.complex`, `std.math`, `std.mathspecial` and `std.internal.math.gammafunction`still fail, and `core.stdc.fenv` is not implemented properly yet. It seems to be likely that most of these problems are again caused by functions lacking from MSVCRT respectively their MinGW replacements (one specific example is `fmodl`, which seems to cause interesting ABI issues).

* The `core.sys.windows.dll` tests do not build, and while this would be easy to work around, DLL creation is entirely untested at this point.

* While MinGW theoretically supports COM, the `std.windows.iunknown` tests do not link yet because of missing symbols. There is likely an easy fix, but interfacing with COM has not been tested at all.

* There are also still two rather disconcerting test failures in `core.time` and `rt.util.container` which have not been tracked down yet.

* LDC currently relies on using the MinGW `as` for emitting object files, as the LLVM integrated assembler does not correctly support writing the DWARF exception handling tables yet. This is suboptimal, as it causes several issues with non-ASCII characters in symbol names and generally has a negative effect on compiler performance. It currently also causes an issue with building the `std.algorithm` unit tests in debug mode, where the humongous symbol names (in the tens of kilo(!)bytes) overflow some `as`-internal data structures.

* And most importantly, LDC/MinGW is still virtually untested on larger real-world applications. There will certainly be a number of bugs which have not been caught by any of the test suites.


Getting Started
---------------

So, how to try out LDC on Windows? The easiest thing would be to just download the latest binary (preview) release. For this, first grab a *very recent* mingw32-w64 snapshot, [such as this one](http://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win32/Personal%20Builds/rubenvb/gcc-4.8-dw2-release/i686-w64-mingw32-gcc-dw2-4.8.0-win32_rubenvb.7z/download) (*rubenvb* personal build, *.7z*, ~27 MB) and extract it to an arbitrary location. It is important that you pick one built with Dwarf 2 exception handling enabled; when in doubt, just use the above one.

Then, download and extract the latest [LDC binary release for MinGW](http://d32gngvpvl2pi1.cloudfront.net/ldc2-0.11.0-beta3-mingw-x86.7z) (*.7z*, ~8.5 MB). It is a "DMD-style" package that should work from any location without any extra installation steps. Before invoking LDC, you need to make sure that the MinGW `bin` directory is on your path, though. This is easiest to achieve by starting a shell using `mingw32env.cmd` in the MinGW root directory, or of course using a MSYS shell altogether.

If you prefer building LDC from source yourself, a guide on [building LDC on MinGW x86](http://wiki.dlang.org/Building_LDC_on_MinGW_x86) is available on the wiki. Any help with LDC/MinGW development would be very much appreciated!
