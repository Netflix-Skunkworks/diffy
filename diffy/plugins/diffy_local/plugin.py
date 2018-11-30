"""
.. module: diffy.plugins.diffy_simple.plugin
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import os
import subprocess
import shlex
import datetime
import json
import logging
from typing import List

from jsondiff import diff

from diffy.config import CONFIG
from diffy.exceptions import BadArguments
from diffy.plugins import diffy_local as local
from diffy.plugins.bases import AnalysisPlugin, PersistencePlugin, PayloadPlugin, CollectionPlugin, TargetPlugin


logger = logging.getLogger(__name__)


def get_local_file_path(file_type: str, key: str) -> str:
    """Creates the full path for given local file."""
    if file_type:
        file_name = f"{file_type}-{key}.json"
    else:
        file_name = f"{key}.json"

    return os.path.join(CONFIG.get("DIFFY_LOCAL_FILE_DIRECTORY"), file_name)


class SimpleAnalysisPlugin(AnalysisPlugin):
    title = "simple"
    slug = "local-simple"
    description = "Perform simple differential analysis on collection results."
    version = local.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/Netflix-Skunkworks/diffy.git"

    def run(self, items: List[dict], **kwargs) -> List[dict]:
        """Run simple difference calculation on results based on a baseline."""
        logger.debug("Performing simple local baseline analysis.")

        if not kwargs.get("baseline"):
            raise BadArguments("Cannot run simple analysis. No baseline found.")

        for i in items:
            i["diff"] = diff(kwargs["baseline"]["stdout"], i["stdout"])

        return items


class ClusterAnalysisPlugin(AnalysisPlugin):
    title = "cluster"
    slug = "local-cluster"
    description = "Perform cluster analysis on collection results."
    version = local.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/Netflix-Skunkworks/diffy.git"

    def run(self, items: List[dict], **kwargs) -> List[dict]:
        """Run cluster calculation on results based on a baseline."""
        logger.debug("Performing simple local cluster analysis.")
        return items


class FilePersistencePlugin(PersistencePlugin):
    title = "file"
    slug = "local-file"
    description = "Store results locally for further analysis."
    version = local.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/Netflix-Skunkworks/diffy.git"

    def get(self, file_type: str, key: str, **kwargs) -> dict:
        """Fetch data from local file system."""
        path = get_local_file_path(file_type, key)
        logging.debug(f"Reading persistent data. Path: {path}")

        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)

    def get_all(self, file_type: str) -> List[dict]:
        """Fetches all files matching given prefix"""
        path = os.path.join(CONFIG.get("DIFFY_LOCAL_FILE_DIRECTORY"))

        items = []
        for p in [os.path.abspath(x) for x in os.listdir(path)]:
            file = p.split("/")[-1]
            if file.startswith(file_type) and file.endswith(".json"):
                with open(p, "r") as f:
                    items.append(json.load(f))
        return items

    def save(self, file_type: str, key: str, item: dict, **kwargs) -> None:
        """Save data to local file system."""
        path = get_local_file_path(file_type, key)
        logging.debug(f"Writing persistent data. Path: {path}")

        with open(path, "w") as f:
            json.dump(item, f)


class CommandPayloadPlugin(PayloadPlugin):
    title = "command"
    slug = "local-command"
    description = "Sends command without any modification."
    version = local.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/Netflix-Skunkworks/diffy.git"

    def generate(self, incident: str, **kwargs) -> dict:
        return CONFIG.get('DIFFY_PAYLOAD_LOCAL_COMMANDS')


class LocalShellCollectionPlugin(CollectionPlugin):
    title = 'command'
    slug = 'local-shell-collection'
    description = 'Executes payload commands via local shell.'
    version = local.__version__

    author = 'Alex Maestretti'
    author_url = 'https://github.com/Netflix-Skunkworks/diffy.git'

    def get(self, targets: List[str], commands: List[str], **kwargs) -> dict:
        """Queries local system target via subprocess shell.

        :returns command results as dict {
            'command_id': [
                {
                    'instance_id': 'i-123343243',
                    'status': 'success',
                    'collected_at' : 'dtg'
                    'stdout': {json osquery result}
                }
                ...
            ]
        }
        """
        # TODO: check if we are root, warn user if not we may not get a full baseline
        results = {}
        for idx, cmd in enumerate(commands):
            logger.debug(f'Querying local system with: {cmd}')
            # format command which is a string with an osqueryi shell command into a list of args for subprocess
            formatted_cmd = shlex.split(cmd)

            # TODO support python37
            process_result = subprocess.run(formatted_cmd, stdout=subprocess.PIPE)  # python36 only
            stdout = process_result.stdout.decode('utf-8')
            
            # TODO: check return status and pass stderr if needed
            results[idx] = [{
                'instance_id': 'localhost',
                'status': 'success',
                'collected_at': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                'stdout': json.loads(stdout)
            }]
            logger.debug(f'Results[{idx}] : {format(json.dumps(stdout, indent=2))}')
        return results


class LocalTargetPlugin(TargetPlugin):
    title = 'command'
    slug = 'local-target'
    description = 'Targets the local system for collection.'
    version = local.__version__

    author = 'Alex Maestretti'
    author_url = 'https://github.com/Netflix-Skunkworks/diffy.git'

    def get(self, key, **kwargs):
        return 'local'  # returns arbitrary value that is ignored by local-collection
