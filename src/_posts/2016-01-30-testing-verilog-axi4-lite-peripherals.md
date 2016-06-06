---
layout: post
title: "Testing Verilog AXI4-Lite Peripherals"
tags:
 - FPGA
 - HDL
 - Verilog
excerpt: "Chips that combine one or more processor cores and FPGA fabric into one integrated system have become quite popular recently, the most well-known product being Xilinx’ ARM-based Zynq series. The standardized AXI buses connecting them make it trivial to bring custom IP cores"
---

<p class="lead" markdown="1">Chips that combine one or more processor cores and FPGA fabric into one integrated system have become quite popular recently, the most well-known product being Xilinx' ARM-based [_Zynq_](http://www.xilinx.com/products/silicon-devices/soc/zynq-7000.html) series. The standardized AXI buses connecting them make it trivial to bring custom IP cores into the processor address space. This post describes how to interface with it from a standalone Verilog test-bench.</p>

The popularity these combined systems-on-a-chip have been enjoying lately in research labs is certainly in part due to the ease in which programmable logic can be connected to the CPU cores, as compared to having to design and implement an interface between a discrete ARM processor and a stand-alone FPGA chip. This is due to the fact that the Zynq chips feature several internal interconnects between the ARM cores and the programmable logic fabric (including access to the DDR system memory and cache coherency control). These buses follow ARM's open AMBA AXI4 standard, which is available in several flavors: the base _AXI4_ protocol, which defines a high-performance memory-mapped interface, _AXI4-Stream_, which realizes a unidirectional data flow with handshaking, and _AXI4-Lite_, which is similar to AXI4 but lacks advanced features like buffering, multiple widths and bursts. Each given device implementing one of these protocols can act as either a master or a slave.

Here, we will concern ourselves only with perhaps the simplest case, an AXI4-Lite slave. A typical example for this would be a low-bandwidth control channel from the ARM CPU to a custom IP core. Implementing such a device is quite easy as the Xilinx development environment includes tooling to generate the code for interfacing with the AXI bus (although it seems that, compared to the average programmer, FPGA designers lack any sensibility for writing _pretty_ or even just consistently formatted code). But of course, this leaves the question of how to verify that the IP core reacts correctly to these commands – as it is usually the case for HDL design, you certainly don't want to run the time-consuming synthesis process and re-flash the hardware on every iteration in the debugging process, only to then find yourself in an environment where it is hard to diagnose errors anyway unless you had enough foresight to litter the code with ChipScope debug probes in all the right places.

These days, I use [Icarus Verilog](http://iverilog.icarus.com/) for most all of my simulation needs, except when some proprietary IP is involved for which no functional model is available outside the vendor tools. It is an open source project that provides a Verilog parser, optimizer and virtual machine, and together with a waveform viewer such as [GtkWave](xxx) makes for a nice light-weight testing environment. For small-ish projects, it tends to have already finished the simulation before the clunky and bug-ridden vendor tools such as Xilinx _isim_ would have even completed starting up.

Co-simulating the code to run on the ARM CPU and the FPGA design is certainly possible – maybe by using Verilator and piping data flow on the AXI buses back and forth between the domains, or by bringing out the "big guns", i.e. system-level verification tools made by companies like Cadence. The most straightforward solution, however, is certainly to test the core in question in isolation, while just manually handling the necessary AXI communication in the test-bench.

Owing to the simplicity of the AXI4-Lite protocol, such functionality is not hard to implement. The "AMBA® AXI™ and ACE™ Protocol Specification" – available on the ARM website after logging in, and certainly floating around in other places as well – is quite clear and well-written. Interestingly, however, none of the templates provided by Xilinx seem to include the relevant pieces of HDL. So, without further ado, here is a Verilog task that reads a single word from the bus and compares it to the expected value: 

{% codeblock lang:verilog Reading a word from the AXI4-Lite bus and comparing it to an expected result. %}
task automatic enforce_axi_read;
  input [C_S_AXI_ADDR_WIDTH - 1 : 0] addr;
  input [C_S_AXI_DATA_WIDTH - 1 : 0] expected_data;
  begin
    s_axi_araddr = addr;
    s_axi_arvalid = 1;
    s_axi_rready = 1;
    wait(s_axi_arready);
    wait(s_axi_rvalid);

    if (s_axi_rdata != expected_data) begin
      $display("Error: Mismatch in AXI4 read at %x: ", addr,
        "expected %x, received %x",
        expected_data, s_axi_rdata);
    end

    @(posedge s_axi_aclk) #1;
    s_axi_arvalid = 0;
    s_axi_rready = 0;
  end
endtask
{% endcodeblock %}

All the `s_axi_…` signals are supposed to be hooked up to the corresponding ports of the unit under tests, as they would be in an auto-generated test-bench module. To use it, simply insert `enforce_axi_read(<addr>, <data>);` at the appropriate point in your test sequence.

In the same vein, the following task writes a data word to the given address:

{% codeblock lang:verilog Writing a word to the AXI4-Lite bus. %}
task automatic axi_write;
  input [C_S_AXI_ADDR_WIDTH - 1 : 0] addr;
  input [C_S_AXI_DATA_WIDTH - 1 : 0] data;
  begin
    s_axi_wdata = data;
    s_axi_awaddr = addr;
    s_axi_awvalid = 1;
    s_axi_wvalid = 1;
    wait(s_axi_awready && s_axi_wready);

    @(posedge s_axi_aclk) #1;
    s_axi_awvalid = 0;
    s_axi_wvalid = 0;
  end
endtask
{% endcodeblock %}

As a final note, be aware that these tasks are not at all intended to verify the protocol-level implementation of the AXI interface itself. A verified boilerplate solution, such as the one auto-generated by the Xilinx tools, would be used most of the time anyway. However, it might be interesting to know that ARM offers a set of [AXI 4 Protocol Assertion](http://infocenter.arm.com/help/topic/com.arm.doc.dui0534b/DUI0534B_amba_4_axi4_protocol_assertions_ug.pdf) cores that can be inserted into the design to verify that the bus signalling conforms to the specification.
