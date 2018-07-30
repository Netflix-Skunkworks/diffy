Diffy
=====

.. image:: docs/images/diffy_small.png
    :align: right

.. image:: https://travis-ci.org/Netflix-Skunkworks/diffy.svg?branch=master
    :target: https://travis-ci.org/Netflix-Skunkworks/diffy

.. image:: https://img.shields.io/codecov/c/github/Netflix-Skunkworks/diffy/master.svg?style=flat-square
    :target: https://codecov.io/gh/Netflix-Skunkworks/diffy
    :alt: Codecov

.. image:: https://img.shields.io/gitter/room/nwjs/nw.js.svg?style=flat-square
    :target: https://gitter.im/diffy/diffy

.. image:: https://img.shields.io/pypi/v/diffy.svg?style=flat-square
    :target: https://pypi.python.org/pypi/diffy
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/diffy.svg?style=flat-square
    :target: https://pypi.org/project/diffy
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/diffy.svg?style=flat-square
    :target: https://choosealicense.com/licenses
    :alt: License

.. image:: https://img.shields.io/pypi/status/diffy.svg?style=flat-square
    :target: https://pypi.python.org/pypi/diffy
    :alt: Status

.. image:: https://img.shields.io/readthedocs/diffy.svg?style=flat-square
    :target: https://readthedocs.org/projects/diffy/badge/?version=latest
    :alt: RTD


Diffy is a digital forensics and incident response (DFIR) tool developed by
Netflix's Security Intelligence and Response Team (SIRT).

Diffy allows a forensic investigator to quickly scope a compromise across cloud
instances during an incident, and triage those instances for followup actions.
Diffy is currently focused on Linux instances running within Amazon Web
Services (AWS), but owing to our plugin structure, could support multiple
platforms and cloud providers.

It's called "Diffy" because it helps a human investigator to identify the
*differences* between instances, and because `Alex`_ pointed out that "The
Difforensicator" was unnecessarily tricky.

See `Releases`_ for recent changes. See `our Read the Docs site`_ for
well-formatted documentation.

.. _Alex: https://www.linkedin.com/in/maestretti/
.. _Releases: https://github.com/Netflix-Skunkworks/diffy/releases
.. _our Read the Docs site: http://diffy.readthedocs.io/

Supported Technologies
----------------------

- AWS (AWS Systems Manager / SSM)
- Local
- osquery

Each technology has its own plugins for targeting, collection and persistence.


Features
--------

- Efficiently highlights outliers in security-relevant instance behavior. For
  example, you can use Diffy to tell you which of your instances are listening
  on an unexpected port, are running an unusual process, include a strange
  crontab entry, or have inserted a surprising kernel module.
- Uses one, or both, of two methods to highlight differences:

    - Collection of a "functional" baseline from a "clean" running instance,
      against which your instance group is compared, and
    - Collection of a "clustered" baseline, in which all instances are surveyed,
      and outliers are made obvious.

- Uses a modular plugin-based architecture. We currently include plugins for
  collection using osquery via AWS Systems Manager (formerly known as Simple
  Systems Manager or SSM).


Installation
------------

Via pip::

    pip install diffy


Roadmap
-------

We are actively adding more plugins & tests, and improving the documentation.


Why python 3 only?
~~~~~~~~~~~~~~~~~~

Please see `Guido's guidance
<https://mail.python.org/pipermail/python-dev/2018-March/152348.html>`_
regarding the Python 2.7 end of life date.
