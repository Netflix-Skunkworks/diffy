Contributing
============

Want to contribute back to Diffy? This page describes the general development
flow, our philosophy, the test suite, and issue tracking.

Impostor Syndrome Disclaimer
----------------------------

Before we get into the details: **We want your help. No, really.**

There may be a little voice inside your head that is telling you that you're
not ready to be an open source contributor; that your skills aren't nearly good
enough to contribute. What could you possibly offer a project like this one?

We assure you -- the little voice in your head is wrong. If you can write code
at all, you can contribute code to open source. Contributing to open source
projects is a fantastic way to advance one's coding skills. Writing perfect
code isn't the measure of a good developer (that would disqualify all of us!);
it's trying to create something, making mistakes, and learning from those
mistakes. That's how we all improve.

We've provided some clear `Contribution Guidelines`_ that you can read below.
The guidelines outline the process that you'll need to follow to get a patch
merged. By making expectations and process explicit, we hope it will make it
easier for you to contribute.

And you don't just have to write code. You can help out by writing
documentation, tests, or even by giving feedback about this work. (And yes,
that includes giving feedback about the contribution guidelines.)

(`Adrienne Friend`_ came up with this disclaimer language.)

.. _Adrienne Friend: https://github.com/adriennefriend/imposter-syndrome-disclaimer

Documentation
-------------

If you're looking to help document Diffy, your first step is to get set up with
Sphinx, our documentation tool. First you will want to make sure you have a few
things on your local system:

* python-dev (if you're on OS X, you already have this)
* pip
* virtualenvwrapper

Once you've got all that, the rest is simple:

::

    # If you have a fork, you'll want to clone it instead
    git clone git://github.com/Netflix-Skunkworks/diffy.git

    # Create a python virtualenv
    mkvirtualenv diffy

    # Make the magic happen
    make dev-docs

Running ``make dev-docs`` will install the basic requirements to get Sphinx
running.


Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

Inside the ``docs`` directory, you can run ``make`` to build the documentation.
See ``make help`` for available options and the `Sphinx Documentation
<http://sphinx-doc.org/contents.html>`_ for more information.


Developing Against HEAD
-----------------------

We try to make it easy to get up and running in a development environment using
a git checkout of Diffy. You'll want to make sure you have a few things on your
local system first:

* python-dev (if you're on OS X, you already have this)
* pip
* virtualenv (ideally virtualenvwrapper)
* node.js (for npm and building css/javascript)
* (Optional) PostgreSQL

Once you've got all that, the rest is simple:

::

    # If you have a fork, you'll want to clone it instead
    git clone git://github.com/Netflix-Skunkworks/diffy.git

    # Create a python virtualenv
    mkvirtualenv diffy


Coding Standards
----------------

Diffy follows the guidelines laid out in `pep8
<http://www.python.org/dev/peps/pep-0008/>`_  with a little bit of flexibility
on things like line length. We always give way for the `Zen of Python
<http://www.python.org/dev/peps/pep-0020/>`_. We also use strict mode for
JavaScript, enforced by jshint.

You can run all linters with ``make lint``, or respectively ``lint-python`` or
``lint-js``.

Spacing
~~~~~~~

Python:
  4 Spaces

JavaScript:
  2 Spaces

CSS:
  2 Spaces

HTML:
  2 Spaces


Running the Test Suite
----------------------

If you've setup your environment correctly, you can run the entire suite with
the following command:

::

    pytest


You'll notice that the test suite is structured based on where the code lives,
and strongly encourages using the mock library to drive more accurate
individual tests.

.. note:: We use py.test for the Python test suite.


Contribution Guidelines
=======================

All patches should be sent as a pull request on GitHub, include tests, and
documentation where needed. If you're fixing a bug or making a large change the
patch **must** include test coverage.

Uncertain about how to write tests? Take a look at some existing tests that are
similar to the code you're changing, and go from there.

You can see a list of open pull requests (pending changes) by visiting
https://github.com/Netflix-Skunkworks/diffy/pulls

Pull requests should be against **master** and pass all TravisCI checks.

We use `pre-commit hooks`_ to help us all maintain a consistent standard for
code. To get started, run:

::

    pre-commit install


Before submitting code, run these:

::

	pre-commit run --all-files


.. _pre-commit hooks: https://pre-commit.com/#usage

Writing a Plugin
================

.. toctree::
    :maxdepth: 2

    plugins/index


Internals
=========

.. toctree::
    :maxdepth: 2

    internals/diffy
