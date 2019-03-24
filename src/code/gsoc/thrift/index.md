---
layout: code
title: D/Thrift – GSoC 2011
prev_title: d4
prev_url: /code/d4
next_title: LDC
next_url: /code/ldc
---

# GSoC 2011: An Apache Thrift implementation for&nbsp;D

<p class="lead" markdown="1">I was lucky enough to be selected to participate in the [Google Summer of Code](http://www.google-melange.com/gsoc/homepage/google/gsoc2011) program this year under the umbrella of [Digital Mars](http://www.google-melange.com/gsoc/org/google/gsoc2011/dprogramminglanguage), during the course of which I worked on an implementation of the [Apache Thrift](http://thrift.apache.org/) framework for/in the [D programming language](http://d-programming-language.org/).</p>

The source code is available at [my GitHub Thrift fork](https://github.com/dnadlinger/thrift/tree/d-gsoc). The [GitHub repository wiki](https://github.com/dnadlinger/thrift/wiki) has some documentation that would go to the Thrift wiki if my work was merged upstream (including a [Getting Started](https://github.com/dnadlinger/thrift/wiki/Getting-Started-with-Thrift-and-D) page), and a [DDoc build](/code/gsoc/thrift/docs/) is available as well.

You can find the original project proposal on [Google Melange](http://www.google-melange.com/gsoc/proposal/review/google/gsoc2011/klickverbot/1), although the comments are not publicly accessible.

Current Status
--------------

The official Google Summer of Code term ended on August 22, and I was able to complete the project successfully. However, contrary to the original plans, D support has not been merged to upstream yet due to a few remaining issues, which have been resolved in the development versions of the D compiler. This is the current status of the test suite (based on Thrift [efce47fc](https://github.com/dnadlinger/thrift/commit/efce47fca54c6818be9f491cbc6bc58525bae3f1), DMD 2.058):

<figure>
<table class="firstname">
  <thead>
    <tr>
      <th></th>
      <th>Unit tests</th>
      <th>Standalone tests</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Linux x86 (DMD 2.058)</td>
      <td class="pass">pass</td>
      <td class="pass">pass</td>
    </tr>
    <tr>
      <td>Linux x86_84 (DMD 2.058)</td>
      <td class="pass">pass</td>
      <td class="pass">pass</td>
    </tr>
    <tr>
      <td>OS X x86 (DMD 2.058)</td>
      <td class="pass">pass</td>
      <td class="pass">pass</td>
    </tr>
    <tr>
      <td>OS X x86_64 (DMD 2.058)</td>
      <td class="pass">pass</td>
      <td class="pass">pass</td>
    </tr>
    <tr>
      <td>Windows x86 (DMD 2.058)</td>
      <td class="pass">pass</td>
      <td class="pass">pass</td>
    </tr>
  </tbody>
</table>
</figure>

GDC and LDC _should_ work just as well (provided that they are using a recent frontend), but have not been tested yet.

Assorted todo list (of items not really necessary to complete before kicking off the upstream merge):
 * Paint the API `@safe` (and `pure`/`nothrow` in the few places where they are applicable).
 * Some multi-threaded test cases can hang forever instead of exiting on failure.

Please free to contact me for any related questions.
