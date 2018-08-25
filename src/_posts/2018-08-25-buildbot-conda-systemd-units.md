---
layout: post
title: "Systemd units for Buildbot in Conda"
tags:
 - Conda
 - Linux
 - Python
excerpt: Buildbot is a Python framework for continuous integration systems. In my research group we are deploying it in a Conda environment, which we also use to manage all the different moving parts of our Python-centric control infrastructure on both Windows and Linux. To start up the master and worker services, the corresponding Conda environment 
---

Buildbot is a Python framework for continuous integration systems. In [my research group](https://www2.physics.ox.ac.uk/research/ion-trap-quantum-computing-group) we are deploying it in a [Conda](https://conda.io/) environment, which we also use to manage all the different moving parts of our Python-centric control infrastructure on both Windows and Linux. To start up the master and worker services, the corresponding Conda environment needs to be activated first. This is easiest to achieve using simple wrapper scripts.

For this, let's assume we've created a `bb` user, with the master and worker configurations in its home directory (`~/master` and `~/worker`). First, create a wrapper script to start up the master process:

{% codeblock lang:bash ~bb/start-master.sh %}
#!/bin/bash
set -eo pipefail

export PATH=~/anaconda3/bin:$PATH
source activate buildbot
buildbot start --nodaemon master
{% endcodeblock %}

This assumes Conda has been installed into `~bb/anaconda3`, and the environment with the Buildbot installation is called `buildbot`. `master` is the name of the configuration directory, and `--nodaemon` prevents daemonisation (i.e. keeps the process running in the foreground).

Make the script executable, and create a Systemd unit file that invokes it:

{% codeblock lang:ini /etc/systemd/system/buildbot-master.service %}
[Unit]
Description=Buildbot master service
After=network.target

[Service]
User=bb
Group=bb
WorkingDirectory=/home/bb
ExecStart=/home/bb/start-master.sh
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
{% endcodeblock %}

To start the master process, run

{% codeblock lang:bash %}
systemctl start buildbot-master
{% endcodeblock %}

and to do so every time the system boots:

{% codeblock lang:bash %}
systemctl enable buildbot-master
{% endcodeblock %}

<hr>

The analogous configuration for the worker process is

{% codeblock lang:bash ~bb/start-worker.sh %}
#!/bin/bash
set -eo pipefail

export PATH=~/anaconda3/bin:$PATH
source activate buildbot
buildbot-worker start --nodaemon worker
{% endcodeblock %}

and 

{% codeblock lang:ini /etc/systemd/system/buildbot-worker.service %}
[Unit]
Description=Buildbot worker service
After=network.target

[Service]
User=bb
Group=bb
WorkingDirectory=/home/bb
ExecStart=/home/bb/start-worker.sh
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
{% endcodeblock %}

Start it using 

{% codeblock lang:bash %}
systemctl enable buildbot-worker
systemctl start buildbot-worker
{% endcodeblock %}

<hr>

This is it; Buildbot is now run automatically when the system boots. To avoid starting the graphical user interface on a desktop Ubuntu install, run `systemctl set-default multi-user.target`.

