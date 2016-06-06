---
layout: post
title: "<code>getaddrinfo</code> cross-platform edge case behavior"
tags:
- D
- Sockets
- Wine
excerpt: "An often-needed piece of functionality in network programming is to resolve human-readable host or port names to their numerical equivalent, for example in order to pass the latter to operating system socket APIs. The <code>getaddrinfo</code> function fills this role on POSIX and Windows. Apart from some flags, it accepts…"
---

An often-needed piece of functionality in network programming is to resolve human-readable host or port names to their numerical equivalent, for example in order to pass the latter to operating system socket APIs. The `getaddrinfo` function fills this role on POSIX and Windows. Apart from some flags, it accepts two string parameters for host and service (port) names and returns a list of corresponding IP addresses and port numbers, superseding the older `gethostbyname` and `getservbyname` functions.

Either of its string parameters is allowed to be `null`, representing the local host/all interfaces (depending on whether `AI_PASSIVE` is specified) and an automatically assigned port, respectively. Both parameters being `null` at the same time, however, is disallowed by the specification, and leads to a `EAI_NONAME` error on Posix or `WSAHOST_NOT_FOUND` on Windows. What happens if the strings are empty (`"\0"`) instead of `null`, however, is left open by RFC 2553, and not really mentioned in the operating system API documentation either.

It turns out that there are quite a few differences there between the various operating systems, which is obviously likely to cause issues for [Wine](http://winehq.org) (an implementation of the Windows API on Posix/X systems). To get a clear understanding of how the different cases are handled, I put together a little [D](http://dlang.org) program which tests a few combinations of host name, port, and flag parameters (see end of post). The snippet could be written in C just the same, as `getAddressInfo` directly maps to `getaddrinfo`, I just chose D to avoid platform dependencies and writing an unduly large amount of more boilerplate code.

The results are summarized in the following table, where »loopback« means that the IP addresses returned were `127.0.0.1` and `::1`, »catchall« refers to `0.0.0.0` and `::`, »public« means that the actual IP addresses of all available network interfaces were returned, and `NONAME` refers to a lookup error. »hostname« means that the actual fully qualified name of the host that ran the test was used (care: the host part of the FQDN only does usually _not_ resolve on OS X).

<figure>
  <table>
    <thead>
      <tr>
        <th>Host</th>
        <th>Port</th>
        <th>Flags</th>
        <th>Windows</th>
        <th>Linux</th>
        <th>OS X</th>
      </tr>
    </thead>
    <tbody>
      <tr class="odd">
        <td><code>null</code></td>
        <td><code>null</code></td>
        <td>-</td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>""</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback</td>
        <td><code>NONAME</code></td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>catchall</td>
        <td>catchall</td>
        <td><code>NONAME</code></td>
      </tr>
      <tr class="odd">
        <td>&nbsp;</td>
        <td><code>"0"</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback</td>
        <td>loopback</td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>catchall</td>
        <td>catchall</td>
        <td>catchall</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>"80"</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback</td>
        <td>loopback</td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>catchall</td>
        <td>catchall</td>
        <td>catchall</td>
      </tr>
      <tr class="odd">
        <td><code>""</code></td>
        <td><code>null</code></td>
        <td>-</td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>""</code></td>
        <td>-</td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td><code>NONAME</code></td>
      </tr>
      <tr class="odd">
        <td>&nbsp;</td>
        <td><code>"0"</code></td>
        <td>-</td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td>loopback</td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td>catchall</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>"80"</code></td>
        <td>-</td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td>loopback</td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td><code>NONAME</code></td>
        <td>catchall</td>
      </tr>
      <tr class="odd">
        <td><code>"localhost"</code></td>
        <td><code>null</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>""</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr class="odd">
        <td>&nbsp;</td>
        <td><code>"0"</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>"80"</code></td>
        <td>-</td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>loopback</td>
        <td>loopback (v4)</td>
        <td>loopback</td>
      </tr>
      <tr class="odd">
        <td>hostname</td>
        <td><code>null</code></td>
        <td>-</td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>""</code></td>
        <td>-</td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr class="odd">
        <td>&nbsp;</td>
        <td><code>"0"</code></td>
        <td>-</td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr class="odd">
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td><code>"80"</code></td>
        <td>-</td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
      <tr>
        <td colspan="2">&nbsp;</td>
        <td><code>AI_PASSIVE</code></td>
        <td>public</td>
        <td>loopback (v4)</td>
        <td>public</td>
      </tr>
    </tbody>
  </table>
  <figcaption><code>getaddrinfo()</code> behavior on Windows Server 2008 R2, Arch Linux (Kernel 3.1.4, glibc 2.14.1), and OS X 10.7.2 (Lion).</figcaption>
</figure>

What caused me to investigate the issue in the first place is the behavior when given an empty, non-null host string: Windows returns the public addresses of the present interfaces, while OS X resolves them to `::1`/`::`, but only if a port is given, and Linux doesn't resolve them at all! Windows generally accepts the most combinations, returning an error only for the explicitly disallowed combination, which is relied on by some applications (e.g. the game _League of Legends_).

There were also some less significant differences in behavior which are mostly not listed in the table. First, in both of the Linux VMs I tried (an up-to-date Arch box and Ubuntu Oneric), only the IPv4 address of the loopback interface was returned. Second, as in the test no address family, socket type or protocol hints were passed to `getaddrinfo()`, each address was returned twice on OS X, once with `SOCK_STREAM`/`IPPROTO_TCP` and once with `SOCK_DGRAM`/`IPPROTO_UDP` set. Linux returned three copies of each address, for `STREAM`, `DGRAM` and `RAW`, with the according protocol types set, whereas Windows only returned a single copy with protocol type `IPPROTO_IP` and socket type set to 0.

In any case, as a result I have prepared a patch for Wine to emulate at least the succeeding/failing behavior of the Winsock incarnation of `getaddrinfo` on Linux and OS X, which should solve the bigger part of the related problems. There ideally shouldn't be any Windows software relying on details beyond that (such as the actual number/layout of addresses returned), but who knows…

{% codeblock lang:d D program used for gathering the data (longer than necessary for somewhat nicely formatted output). %}
import std.algorithm, std.conv, std.range, std.socket, std.stdio;
alias AIF = AddressInfoFlags;
void main() {
  foreach (host; [null, "", "localhost", Socket.hostName()])
  foreach (port; [null, "", "0", "80"])
  foreach (flags; [cast(AIF)0, AIF.PASSIVE]) {
    write(
      host ? "'" ~ host ~ "'" : "null", ":",
      port ? "'" ~ port ~ "'" : "null", " (", flags, "): "
    );
    try {
      getAddressInfo(host, port, flags)
        .sort!((a, b) => a.family < b.family)
        .map!(a => text(a.address, " (", a.protocol, ")"))
        .join(", ")
        .writeln;
    } catch (Exception e) {
      writefln("[%s]", e.msg);
    }
  }
}
{% endcodeblock %}
