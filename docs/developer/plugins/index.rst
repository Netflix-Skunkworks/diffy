Several interfaces exist for extending Diffy:

* Analysis (diffy.plugins.bases.analysis)
* Collection (diffy.plugins.bases.collection)
* Payload (diffy.plugins.bases.payload)
* Persistence (diffy.plugins.bases.persistence)
* Target (diffy.plugins.bases.target)
* Inventory (diffy.plugins.bases.inventory)

Each interface has its own functions that will need to be defined in order for
your plugin to work correctly. See :ref:`Plugin Interfaces <PluginInterfaces>`
for details.


Structure
---------

A plugins layout generally looks like the following::

    setup.py
    diffy_pluginnae/
    diffy_pluginname/__init__.py
    diffy_pluginname/plugin.py

The ``__init__.py`` file should contain no plugin logic, and at most, a VERSION
= 'x.x.x' line. For example, if you want to pull the version using
pkg_resources (which is what we recommend), your file might contain::

    try:
        VERSION = __import__('pkg_resources') \
            .get_distribution(__name__).version
    except Exception as e:
        VERSION = 'unknown'

Inside of ``plugin.py``, you'll declare your Plugin class, inheriting from the
parent classes that establish your plugin's functionality::

    import diffy_pluginname
    from diffy.plugins.bases import AnalysisPlugin, PersistencePlugin

    class PluginName(AnalysisPlugin):
        title = 'Plugin Name'
        slug = 'pluginname'
        description = 'My awesome plugin!'
        version = diffy_pluginname.VERSION

        author = 'Your Name'
        author_url = 'https://github.com/yourname/diffy_pluginname'

        def widget(self, request, group, **kwargs):
            return "<p>Absolutely useless widget</p>"

And you'll register it via ``entry_points`` in your ``setup.py``::

    setup(
        # ...
        entry_points={
           'diffy.plugins': [
                'pluginname = diffy_pluginname.analysis:PluginName'
            ],
        },
    )

You can potentially package multiple plugin types in one package, say you want
to create a source and destination plugins for the same third-party. To
accomplish this simply alias the plugin in entry points to point at multiple
plugins within your package::

    setup(
        # ...
        entry_points={
            'diffy.plugins': [
                'pluginnamesource = diffy_pluginname.plugin:PluginNameSource',
                'pluginnamedestination = diffy_pluginname.plugin:PluginNameDestination'
            ],
        },
    )

Once your plugin files are in place and the ``setup.py`` file has been
modified, you can load your plugin by reinstalling diffy::

    (diffy)$ pip install -e .

That's it! Users will be able to install your plugin via ``pip install <package
name>``.

.. SeeAlso:: For more information about python packages see `Python Packaging <https://packaging.python.org/en/latest/distributing.html>`_

.. _PluginInterfaces:

Plugin Interfaces
=================

In order to use the interfaces all plugins are required to inherit and override
unimplemented functions of the parent object.

Analysis
--------

Analysis plugins are used when you are trying to scope or evaluate information
across a cluster. They can either process information locally or used an
external system (i.e. for ML).


The `AnalysisPlugin` exposes on function::

    def run(self, items, **kwargs):
        # run analysis on items

Diffy will pass all items collected it will additionally pass the optional
`baseline` flag if the current configuration is deemed to be a baseline.

Collection
----------

Collection plugins allow you to collect information from multiple hosts. This
provides flexibility on how information is collected, depending on the
infrastructure available to you.

The CollectionPlugin requires only one function to be implemented::

    def get(self, targets, incident, command, **kwargs) --> dict:
         """Queries system target.

        :returns command results as dict {
            'command_id': [
                {
                    'instance_id': 'i-123343243',
                    'status': 'success',
                    'collected_at' : 'datetime'
                    'stdout': {json osquery result}
                }
                ...
                {additional instances}
            ]
        }
        """

The `incident` string is intended to document a permanent identifier for your
investigation. You may insert any unique ticketing system identifier (for
example, `DFIR-21996`), or comment, here.

Payload
-------

Diffy includes the ability to modify the `payload` for any given command. In
general this payload is the dynamic generation of commands sent to the target.
For instance if you are simply running a `netstat` payload you may have to
actually run a series of commands to generate a JSON output from the `netstat`
command.

Here again the incident is passed to be dynamically included into the commands
if applicable.

The PayloadPlugin requires only one function to be implemented::

    def generate(self, incident, **kwargs) --> dict:
        # list of commands to be sent to the target


Persistence
-----------

Persistence plugins give Diffy to store the outputs of both collection and
analysis to location other than memory. This is useful for baseline tasks or
persisting data for external analysis tasks.

The PersistencePlugin requires two functions to be implemented::

    def get(self, key, **kwargs):
        # retrieve from location

    def save(self, key, item, **kwargs):
        # save to location

Target
------

Target plugins give Diffy the ability to interact with external systems to resolve
targets for commands.

The TargetPlugin class requires one function to be implemented::

    def get(self, key, **kwargs):
        # fetch targets based on key


Inventory
---------

Inventory plugins interact with asset inventory services to pull a list of
targets for baselining and analysis.

Inheriting from the InventoryPlugin class requires that you implement a ``process``
method::

    def process(self, **kwargs):
        # Process a new set of targets from a desired source.
        #
        # This method should handle the interaction with your desired source,
        # and then send the results to :meth:`diffy_api.core.async_baseline`.
        #
        # If you poll the source regularly, ensure that you
        # only request recently deployed assets.


Testing
=======

Diffy provides a basic py.test-based testing framework for extensions.

In a simple project, you'll need to do a few things to get it working:

setup.py
--------

Augment your setup.py to ensure at least the following:

.. code-block:: python

   setup(
       # ...
       install_requires=[
          'diffy',
       ]
   )


conftest.py
-----------

The ``conftest.py`` file is our main entry-point for py.test. We need to
configure it to load the Diffy pytest configuration:

.. code-block:: python

   from diffy.tests.conftest import *  # noqa


Running Tests
-------------

Running tests follows the py.test standard. As long as your test files and
methods are named appropriately (``test_filename.py`` and ``test_function()``)
you can simply call out to py.test:

::

    $ py.test -v
    ============================== test session starts ==============================
    platform darwin -- Python 2.7.10, pytest-2.8.5, py-1.4.30, pluggy-0.3.1
    cachedir: .cache
    collected 346 items

    diffy/plugins/diffy_acme/tests/test_aws.py::test_ssm PASSED

    =========================== 1 passed in 0.35 seconds ============================


.. SeeAlso:: Diffy bundles several plugins that use the same interfaces mentioned above.
