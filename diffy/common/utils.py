"""
.. module: diffy.common.utils
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Forest Monsen <fmonsen@netflix.com>
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
import pkg_resources


logger = logging.getLogger(__name__)


def chunk(l, n):
    """Chunk a list to sublists."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


def install_plugins():
    """
    Installs plugins associated with diffy
    :return:
    """
    from diffy.plugins.base import register

    # entry_points={
    #    'diffy.plugins': [
    #         'ssm = diffy_aws.plugin:SSMCollectionPlugin'
    #     ],
    # },
    for ep in pkg_resources.iter_entry_points("diffy.plugins"):
        logger.info(f"Loading plugin {ep.name}")
        try:
            plugin = ep.load()
        except Exception:
            import traceback

            logger.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
        else:
            register(plugin)
