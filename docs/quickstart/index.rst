Quickstart
==========

This guide will step you through setting up a Python-based virtualenv,
configuring it correctly, and running your first baseline and difference
against an autoscaling group (ASG).  This guide assumes you're operating on
a freshly-installed `Ubuntu 16.04 instance`_. Commands may differ in your
environment.

.. _Ubuntu 16.04 instance: https://www.ubuntu.com/download

Clone the repo::

    $ git clone git@github.com:Netflix-Skunkworks/diffy.git && cd diffy

Install a virtualenv there::

    $ virtualenv venv

Activate the virtualenv::

    $ source venv/bin/activate

Install the required "dev" packages into the virtualenv::

    $ pip install -r dev-requirements.txt

Install the local Diffy package::

    $ pip install -e .

Invoke the command line client with default options, to create a new functional
baseline. In the command below, replace the ``<asg>`` placeholder with the name of your
`autoscaling group`_ (a concept particular to AWS)::

    $ diffy new baseline <asg>

.. _`autoscaling group`: https://docs.aws.amazon.com/autoscaling/ec2/userguide/AutoScalingGroup.html

You'll find a JSON file in your current directory. This file contains the
observations collected as the baseline.

Next, run an analysis across all members of that autoscaling group, to locate
outliers::

    $ diffy new analysis <asg>

When done, deactivate your virtualenv::

    $ deactivate
