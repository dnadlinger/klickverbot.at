---
layout: post
title: "Purity in D"
tags:
  - D
excerpt: "Programming language design is a controversial topic, but in light of current challenges regarding both hardware trends and maintainability, several concepts originating in the functional programming world are being rediscovered as universally helpful"
no_footer: true
---

<p class="lead" markdown="1">Programming language design is a controversial topic, but in light of current challenges regarding both hardware trends and maintainability, several concepts originating in the [functional programming](http://en.wikipedia.org/wiki/Functional_programming) world are being rediscovered as universally helpful. To that end, the [D programming language](http://dlang.org) includes its own pragmatic take on the idea of _functional purity_. This article is an introduction to D's `pure` keyword and its interaction with other language features.</p>

Purity is a powerful tool for programmer and compiler alike to help reasoning about source code. But before we delve into the implications and use cases of the feature, first a short definition of the actual semantics of `pure` in D. If you are already familiar with the concept as implemented in other languages, please pretend you never heard of it for the moment. There will likely be a subtle difference in D's interpretation, the quite profound consequences of which will be covered later.

`pure` is a function attribute, and represents a contract between functions and their callers: The implementation of a pure function _does not access global mutable state_, where »global« refers to anything besides the function parameters (which must not reference data `shared` between threads), and »access« covers all reading or writing operations. A function not marked `pure` is called _impure_.

In a slightly less precise way, this means that pure functions always have the same effect and/or return the same result for a given set of arguments. As a consequence, a pure function for example cannot call other impure functions, or perform any kind of I/O (in the classical sense).

However, in order to make implementing non-trivial pure functions feasible, a few things are allowed in pure code that might be illegal under a very strict definition of what comprises state (feel free to skip this if you are only interested in the »big picture«):

 * _Aborting the program_: In a systems-level language like D, there will always be ways to terminate the program. As there is really no way around this, it is explicitly allowed in the specification.

 * _Floating point calculations_: On x86 processors, the behavior of floating point calculation is influenced by a number of global flags (this probably applies to other ISAs which I am less familiar with as well). Thus, if a function contains even a single, perfectly innocent x87/SSE floating point expression like `x + y` or `cast(int)x`, its result, including exceptions being thrown, can vary greatly based on global state (i.e. the processor flags).<sup class="footnote" id="fnr1"><a href="#fn1">1</a></sup> Thus, under a strict definition of purity, all floating point calculations would be disallowed. As this would be an impractical restriction, in D pure functions are allowed to read and write floating point flags (note, however, that in general D functions which change the flags are required to reset them after control flow leaves the function).

<aside markdown="1">In D, non-recoverable exceptions are derived from the `Error` class. While it is still possible to catch them in non-`@safe`<sup class="footnote" id="fnr2"><a href="#fn2">2</a></sup> code, any invariants normally provided by the type system are not guaranteed to hold any longer at this point.</aside>

<ul><li><p markdown="1">_Allocating garbage-collected memory_: If maybe not on the first look, on the second thought it should be evident that the result of an operation allocating memory (think `malloc`) fundamentally depends on global state, namely the amount of free memory available to the system. An equally valid observation, though, is that being unable to use heap-allocated memory at all is a severe restriction for many operations. But it turns out that in D, if allocating GC memory using the `new` keyword fails, it does so with a non-recoverable `Error` anyway. Thus, pure functions can use `new` without violating the guarantees the type system provides. (<em>Note:&nbsp;</em>Strictly speaking, even using memory from the stack would be impure, because depending on the environment, the function might end up triggering a stack overflow.)</p></li></ul>


What About Referential Transparency?
---

One thing is ubiquitous in the functional programming world, but conspicuously absent from the above definition: The immutability of the function parameters. This is neither an oversight, nor has it been implied – pure functions in D can alter their arguments. For example, the following snippet is perfectly valid D code:

{% codeblock lang:d %}
int readAndIncrement(ref int x) pure {
  return x++;
}
{% endcodeblock %}

This might be surprising to some, as purity in programming language theory typically implies referential transparency, which means that a function invocation can be replaced with its result without changing the program semantics (implying absence of side effects). However, this is not automatically the case in D. For example, this piece of code

{% codeblock lang:d %}
int val = 1;
auto result = readAndIncrement(val) * readAndIncrement(val);
// assert(val == 3 && result == 2);
{% endcodeblock %}
clearly does not give the same result if `readAndIncrement` is only evaluated once instead:
{% codeblock lang:d %}
int val = 1;
auto tmp = readAndIncrement(val);
auto result = tmp * tmp;
// assert(val == 2 && result == 1);
{% endcodeblock %}

As covered in the next section, this behavior is actually very desirable in an imperative language, but what to do if you actually want the stronger guarantees of the classical definition of purity, and all the nice properties it entails? Here, another aspect of the D type systems comes to the rescue: the option to transitively mark a view on data as `const` or the data to be completely `immutable`<sup class="footnote" id="fnr3"><a href="#fn3">3</a></sup>. For a closer look at this, consider the following three function declarations:

{% codeblock lang:d %}
int a(int[] val) pure;
int b(const int[] val) pure;
int c(immutable int[] val) pure;
{% endcodeblock %}

Regarding `a` with its mutable parameter, the same observation as for `readAndIncrement` applies (`int[]` is a dynamic array, i.e. a pointer/length pair referring to a slice of memory). In case of `b` and `c`, though, something nice happens: Because the functions are pure, we know that they cannot read/change any global state, and the parameters are not mutable either, so `b` and `c` are side-effect free in the usual sense of the word – calls to them are referentially transparent.

That being said, is there a difference between `b` and `c` at all? From a purity point of view, there is none – `const` and `immutable` impose exactly the same restrictions on what the function can do with its parameters (the latter additionally provides the guarantee that the data will indeed never change, but as no references to it can be escaped besides the return value due to `pure`, this is unlikely to matter in most cases).

However, there is a subtle but important difference affecting the _calling_ code, depending on whether the actual _arguments_ to a function call are merely `const`, which both mutable and immutable values are implicitly convertible to, or `immutable` (i.e. the following applies to both `c` and `b` if called with an `immutable` array).

For example, consider implementing a memoization or common subexpression elimination mechanism. When coming across a `pure` function with `immutable` parameters, only the identity of the arguments has to be checked in order to be able to optimize several calls down to one, e.g. by comparing the memory addresses in the case of a runtime implementation, or by a few very simply checks in an optimizing compiler. On the other hand, if an argument type contains indirections and is only `const`, somebody else could modify the data between two calls, requiring »deep« comparisons that might not be feasible for large data structures in the runtime case, or extensive data flow analysis in a compiler.

The same consideration applies to parallelization: If the arguments of a pure function have no or only `immutable` indirections, it is guaranteed that it is safe to parallelize, because it can cause no side effects which could lead to non-deterministic behavior, and there can be no data races in the parameters as well. However, for `const` arguments, this cannot as easily be inferred, because another piece of code with a mutable view on the arguments could end up modifying them at the same time.

<!-- Comment about explicit annotations, std.traits.ParameterTypeTuple. -->

Indirections in the Return Type?
---

In the previous examples, the functions `a`, `b` and `c` differed in whether there were mutable indirections present in their arguments, but in all three cases, the return type was `int`, the archetypical example for a value type. Is there more to consider if a pure function returns a type containing references?

The first essential point are addresses, respectively the definition of equality applied when considering referential transparency. In functional languages, the actual memory address that some value resides at is usually of little to no importance. D being a system programming language, however, exposes this concept. Now, consider a function `ulong[] primes(uint count) pure`, which allocates an array and fills it with the first `count` prime numbers. Invoking `primes` multiple times with the same `count` will always return the same numbers, but the arrays containing the result will be allocated at different addresses. Thus, it is clear that when considering referential transparency of functions with indirections in the return value, logical equality (`==`) instead of bit-by-bit equality (`is`) is what matters.

The second thing important for referential transparency are mutable indirections in the return type. For example, consider the following snippet of code using the hypothetical `primes` function:

{% codeblock lang:d %}
auto p = primes(42);
auto q = primes(42);
p[] *= 2;
{% endcodeblock %}

Obviously, rewriting the second invocation of `primes` to `auto q = p` is not valid, because then, `q` would refer to the same slice of memory, and thus also contain twice the primes after the multiplication is executed. Generally speaking, the invocation of a pure function with mutable indirections in its return type cannot immediately be considered referentially transparent, but a number of calls might still be optimized/… as if it was depending on how the calling code uses the return values.


›Weak‹ Purity Allows for Stronger Guarantees
---

At this point, it should be mentioned that the initial design of the `pure` keyword in D featured a much stricter set of rules, and while the language specification only ever had a single notion of purity (as defined in the introduction), during discussion of the current more permissive design two terms were coined: _weakly pure_, referring to functions like `readAndIncrement` and `a` from the above examples which have mutable parameters, and _strongly pure_ for side-effect free functions like `b` and `c`. Note, however, that there is no exact definition for these terms and their use frequently is the source of confusion in online discussions – to the point where Don Clugston, who introduced the names in his proposal for the improved design, has already asked for them not to be used any longer.

Still, the terms remain in use today, and the fact that this arbitrary distinction refuse to go away corroborates the observation that the amount of guarantees `pure` provides varies greatly depending on the parameter/return types. And if maybe only for the reason that it is unfamiliar – the actual rules are very simple –, the implications of the current design are sometimes poorly understood. So, what is the motivation behind allowing pure functions to modify their arguments in the first place?

The real power behind the D purity design is that relaxing the rules actually allows _more functions to be »strongly« pure_. To illustrate this, allow me to quote a recent [#AltDevBlogADay](http://altdevblogaday.com) article by John Carmack (of _id Software_ fame) titled »Functional Programming in C++«, a refreshingly pragmatic look at the benefits of applying some functional principles to C++ code:

> Programming with pure functions will involve more copying of data, and in some cases this clearly makes it the incorrect implementation strategy due to performance considerations.  As an extreme example, you can write a pure `DrawTriangle()` function that takes a framebuffer as a parameter and returns a completely new framebuffer with the triangle drawn into it as a result. Don’t do that. &nbsp;—&nbsp; [altdevblogaday.com/…/functional-programming-in-c](http://www.altdevblogaday.com/2012/04/26/functional-programming-in-c/)

There is nothing wrong with this statement, copying the frame buffer every time you draw a triangle is certainly not a good idea. But it turns out that in D, you can actually implement a `pure` triangle drawing function without committing performance suicide! Its signature might look something like this:<sup class="footnote" id="fnr4"><a href="#fn4">4</a></sup>

{% codeblock lang:d %}
alias ubyte[4] Color;
struct Vertex { float[3] position; /* … */ }
alias Vertex[3] Triangle;
void drawTriangle(Color[] framebuffer, const ref Triangle tri) pure;
{% endcodeblock %}

This is nice in and for itself: as remarked in the above quote, `drawTriangle` cannot realistically be referentially transparent since it needs to write to the frame buffer, but `pure` still guarantees that it does not mess around with any hidden/global state. However, there is more: Being pure, the function can now be called from other pure functions. Continuing the toy example, if allocating a new buffer every frame was an option, this could be a function to render a whole scene consisting of triangles:

{% codeblock lang:d %}
Color[] renderScene(
   const Triangle[] triangles,
   ushort width = 640,
   ushort height = 480
) pure {
   auto image = new Color[width * height];
   foreach (ref triangle; triangles) {
      drawTriangle(image, triangle);
   }
   return image;
}
{% endcodeblock %}

Note how the arguments of `renderScene` lack any mutable indirections – while it internally calls the argument-mutating `drawTriangle`, `renderScene` as a whole is referentially transparent!

Now, granted, this example might be a bit contrived, but with D unwilling to give up the bare-metal performance of imperative code, similar situations quite frequently occur in real-life code (e.g. when using any kind of mutable container in the implementation of a pure function). This is also backed by experience with the aforementioned first iteration of the purity design – relaxing the purity rules had the at first sight slightly paradoxical effect of enabling the _same strong guarantees_ as before to be provided for a greatly _increased amount of code_.

A related observation is that most modern style guides discourage use of global state anyway, and thus, it should be possible to mark most D functions not dealing with I/O as pure. This is indeed true – so why not make `pure` the default and require functions to be explicitly marked as, say, `impure` instead? Regarding D version 2, the reason why this has not been done is simply that purity in its current form was only added at a relatively late point in the evolution of the language, where the impact of such a breaking change was simply considered to be too high. Nevertheless, this is certainly a promising direction to explore for future languages and a (hypothetical) next major release of D.


Templates and Purity
---

Up to this point, the focus was on the design of `pure` more or less in isolation. In the following sections, the main topic will be its interaction with other language features, with the first one being templates, or more specifically functions templates.

Once instantiated with its type parameters, functions template are just normal functions, so purity should just work as previously described for them as well. This is indeed the case, but there is additional complexity added because whether a function template can be pure or not might actually depend on the types it is instantiated with.

For an example of this, suppose you want to write a function `array` which accepts a range<sup class="footnote" id="fnr5"><a href="#fn5">5</a></sup> and returns an array containing all of its elements (this function already exists in `std.array` with a much better implementation). A first take on the problem could look somewhat like this:

{% codeblock lang:d A simple, inefficient reimplementation of <code>std.array.array</code>, which converts a range of elements into a built-in array. Could <code>pure</code> be added to this function? %}
auto array(R)(R r) if (isInputRange!R) {
   ElementType!R[] result;
   while (!r.empty) {
      result ~= r.front;
      r.popFront();
   }
   return result;
}
{% endcodeblock %}

It is not hard to guess what this is doing – one by one, the front element of the range is popped off and appended to the result array until there are no more elements left. But the question is now: Can this function be made `pure`? If `R` is something like the result of a `map` or `filter` operation on an array, there is no reason why the should not be callable from pure code. However, if `R` for example encapsulates a line being read from standard input, there is no way `r.empty`, `r.front` and `r.popFront()` can all be `pure`. Thus if `array` was marked `pure`, it could not operate on such ranges anymore, even if it would otherwise be perfectly able to. So, what to do?

One way of approaching this problem would be to introduce syntax sugar for only conditionally applying attributes to a declaration based on some predicate (which would here depend on `R`). However, this was shunned at due to the complexity and repetition it would introduce to code that really should be easy to write. The solution which was finally implemented is quite simple: Since D takes a »white-box« approach to templates anyway, meaning that in order to instantiate a template its source must be available, purity is automatically inferred by the compiler for them (along with a few similar attributes like `nothrow`).

For the above example, this means that a call to `array` will be callable from pure functions if the concrete range type allows it, and just be impure otherwise. Also note that explicitly specifying `pure` for template functions is still possible, and can be beneficial for documentation purposes if purity does not depend on the template arguments.


Pure Member Functions
---

Unsurprisingly, struct and class member functions can be `pure` as well, and exactly the same rules as for free functions apply to them – with a single addition, or rather clarification: The implicit `this` parameter is also considered a function parameter for purity semantics, which is a fancy way of saying that pure functions may access and modify member variables.

{% codeblock lang:d Pure functions are allowed to access member variables (note: typically properties would be used in place of getters/setters in D). %}
class Foo {
  int getBar() const pure {
    return bar;
  }

  void setBar(int bar) pure {
    this.bar = bar;
  }

  private int bar;
}
{% endcodeblock %}

Also note that marking a member function `const` or `immutable` is semantically equivalent to applying the attribute to its implicit `this` parameter; i.e. the above considerations regarding mutability also apply unchanged.

As far as class inheritance is concerned, purity behaves just as one would expect: Generally, a member function in a subclass may require less assumptions while possibly providing more guarantees than its base class equivalent (see e.g. return type covariance). Thus, a pure function might override an impure function, but not the other way round. Actually, for convenience a function overriding a pure base class method is implicitly marked `pure` (similar to `virtual` in C++); Walter Bright recently wrote [a blog post](http://www.drdobbs.com/blogs/cpp/232601305) about this.


`pure` and `immutable` – again?
---

The effects of `const` and `immutable` on referential transparency have already been discussed at length. However, the guarantees of `pure` in some cases also allow to draw additional conclusions. A prominent case of this, because it is integrated with the type system, is that the return value of pure functions can in some cases be safely cast to `immutable`. For example, consider the function `ulong[] primes(uint n) pure` from above. At first, it is not obvious why the following code should compile:

{% codeblock lang:d %}
immutable ulong[] p = primes(5);
{% endcodeblock %}

After all, `immutable` is a guarantee that there are no mutable references to the data in question at all, but `primes` clearly returns an array of mutable values. Still, the above code compiles fine, so what is going on here? The reason why it is indeed safe to assume that no other mutable references exist to the return value of `primes` is of course the fact that it is pure: It does not take any arguments with mutable indirections, nor can it read any global mutable state, so even though the slice returned refers to mutable data, the caller can be sure that nobody else could potentially modify the data.

This seems to be a fairly minor detail, but it turns out to be surprisingly useful in practice, as it allows functions to be seamlessly used in a »functional-style« immutable data context, while at the same time not requiring unnecessary copies in more »traditional« pieces of code, where data might need to be mutated in-place for performance reasons.


Fine, but where is the Escape Hatch?
---

It lies in the very nature of purity that it is viral, in the sense that when writing a pure function, all code its implementation depends on must be pure as well. D's purity rules make this compositional aspect of purity very natural, but still, sometimes the need arises to call a function that is nominally impure from `pure` code.

One example for this is dealing with legacy code, for example when calling a function from an external C library which meets all the criteria to be pure, but has not been marked so in the header files. The way such situations are handled is the same as in all other cases where the type system cannot prove a statement about code: Use a `cast`. More specifically, get a pointer to the function, add the `pure` attribute by casting, and then call it as usual (as any other operation which potentially subverts the type system, this is forbidden in `@safe` code). If a piece of code has to deal with lots of such »dirty« calls, introducing a short `assumePure` template which nicely encapsulates the casts might be worthwhile.

And then there is this other thing where purity might momentarily be a hindrance: inserting (impure) debug code into functions, for example to log some values or to take simple call statistics by bumping a global variable every time a function is invoked. Inserting such an impure statement into the innermost of a chain of pure functions would be a major annoyance, and while this style of debugging might be scoffed at by language purists, it is sometimes quite useful in practice.

Initially, D did not include any special provision for this use case, but a way to »temporarily disable purity« for debugging purposes was much requested. As a result, a special case was eventually added to the rules, allowing impure code in pure functions if it is inside a `debug` conditional. This solution is easy to use, and if not perfectly clean, since such code has to be explicitly enabled via a command line switch (it is _not_ included in normal non`-release` builds), it is still acceptable from an aesthetical point of view.


Conclusion
---

To reiterate the statement from the beginning, the importance of the concept of purity lies within the fact that it allows the type system to assert that a particular function call will not depend on or modify hidden state. We have seen that the `pure` keyword in D imposes less restrictions than in many other languages, but while the same amount of guarantees can still be given due to the interesting properties of transitive const-ness and immutability, this enables very natural interactions with other language features, and perhaps most importantly, imperative-style code.

Where to go for further information? The actual specification for `pure` is not very long, see the [Functions](http://dlang.org/function.html) chapter of the language reference at [dlang.org](http://dlang.org). For background information about the evolution of the current design, the [discussion started by Don Clugston](http://forum.dlang.org/thread/i7bp8o$6po$1@digitalmars.com) which led to the last big change is certainly an interesting read – the [D programming language forums](http://forum.dlang.org/group/digitalmars.D) might also be a good place to ask specific questions about design and implementation of the concepts described here.


<footer>
  <p>Like what you read? <a href="http://twitter.com/?status=@klickverbot:">Let me know</a> what you think, <a href="http://twitter.com/?status=Just%20read%20»Purity%20in%20D«%20by%20@klickverbot:%20http://klickverbot.at/blog/2012/05/purity-in-d">share the article</a> on Twitter or join the discussions on <a href="http://news.ycombinator.com/item?id=4032248">Hacker News</a> and <a href="http://www.reddit.com/r/programming/comments/u84fc/purity_in_d/">Reddit</a>. Also, there is more on <a href="/blog/tags/D/" title="View all posts tagged with »D«" rel="tag">D</a>.</p>
</footer>

<p class="footnote" id="fn1" style="margin-top: 2.88em"><a href="#fnr1"><sup>1</sup></a>The consequences of this can be a lot more serious and confusing than one might think: Historically, several printer drivers on Windows modified the FPU flags when issuing a print job without changing them back afterwards. This caused quite a few programs to crash after a document was printed – the perfect case of a hard-to-debug crash occurring only on customer machines…</p>

<p class="footnote" id="fn2" markdown="1"><a href="#fnr2"><sup>2</sup></a>D code can be restricted to a memory safe language subset sometimes referred to as _SafeD_. The feature can be activated on a per-function basis by applying one of three attributes: Code marked as `@safe` is guaranteed to be memory safe, and thus e.g. cannot do pointer arithmetic or use C-style memory management. `@system` code is the opposite – here the full language, including inline assembly and unsafe pointer casts is allowed. Finally, `@trusted` acts a bridge between both worlds, it contains hand-vetted interfaces to unsafe code. A typical example for the latter would be a type-safe D wrapper around a C `void*`-style API.</p>

<p class="footnote" id="fn3" markdown="1"><a href="#fnr3"><sup>3</sup></a>In D, as notably opposed to C++, `const` and `immutable` are _transitive_. In case of `const`, this means that everything reachable through a  `const` reference automatically becomes `const` as well. For example, given `struct Foo { int bar; int* baz; }; void fun(const Foo* foo);`, in C++ `fun` is not allowed to modify `foo` itself, e.g. to set `foo->bar` to a different value, but can legally modify the value `foo->baz` points to – this is also called _shallow const_. In contrast, D features _deep const_, which means that in `fun`, `foo.baz` automatically becomes a `const` pointer to a `const` `int`, disallowing modifications to `*foo.baz` as well. The same rules apply to `immutable`, except that it additionally guarantees that no mutable view on the data exists at all, i.e. that not only `fun` does not modify its parameter, but nobody else ever does so (you could imagine `immutable` values to be stored in some kind of ROM). `immutable` implies `const`.</p>

<p class="footnote" id="fn4" markdown="1"><a href="#fnr4"><sup>4</sup></a>This example was picked for its illustrative qualities, but admittedly would probably only work like this for a simple software rasterizer. Besides the question of whether purity is much of a benefit here, if an actual graphics API was used to implement it, extra thought would have to be put into how to handle the GPU state in a pure manner.</p>

<p class="footnote" id="fn5" markdown="1"><a href="#fnr5"><sup>5</sup></a> Just as C++ iterators are a generalization of pointers, D ranges generalize the notion of an array or a slice of data. In its most basic form, a range offers three primitives, `empty`, `front` and `popFront`. This interface is completely oblivious to how the underlying data is stored – it could come from a chunk of memory as well as from a network transport or the standard input –, and provides an easy to use, yet powerful abstraction for algorithms to work on.</p>
