"""
.. module: diffy.core
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging

logger = logging.getLogger(__name__)


def analysis(
    target_key: str,
    target_plugin: dict,
    payload_plugin: dict,
    collection_plugin: dict,
    persistence_plugin: dict,
    analysis_plugin: dict,
    **kwargs,
) -> dict:
    """Creates a new analysis."""
    logger.debug(f'Attempting to collect targets with {target_plugin}. TargetKey: {target_key}')
    target_plugin['options'].update(kwargs)
    targets = target_plugin['plugin'].get(target_key, **target_plugin['options'])

    logger.debug(f'Generating payload with {payload_plugin}')
    payload_plugin['options'].update(kwargs)
    commands = payload_plugin['plugin'].generate(None, **kwargs)

    logger.debug(f'Attempting to collect data from targets with {collection_plugin}. NumberTargets: {len(targets)}')
    collection_plugin['options'].update(kwargs)
    results = collection_plugin['plugin'].get(targets, commands, **collection_plugin['options'])

    logger.debug(f'Persisting result data with {persistence_plugin}.')

    # TODO how does this work for non-local analysis?
    items = []
    for k, v in results.items():
        for i in v:
            instance_id = i["instance_id"]
            key = f"{target_key}-{instance_id}"

            items.append(i)
            persistence_plugin["plugin"].save(None, key, i)

    logger.debug('Running analysis.')

    results = analysis_plugin["plugin"].run(
        items,
        baseline=persistence_plugin["plugin"].get("baseline", target_key),
        syntax="compact",
    )

    persistence_plugin["options"].update(kwargs)
    persistence_plugin["plugin"].save(
        "analysis", target_key, results, **persistence_plugin["options"]
    )
    return {"analysis": results}


def baseline(
    target_key: str,
    target_plugin: dict,
    payload_plugin: dict,
    collection_plugin: dict,
    persistence_plugin: dict,
    **kwargs,
) -> dict:
    """Creates a new baseline."""
    target_plugin["options"].update(kwargs)
    targets = target_plugin["plugin"].get(target_key, **target_plugin["options"])[:1]

    logger.debug("Generating payload.")

    payload_plugin["options"].update(kwargs)
    commands = payload_plugin["plugin"].generate(None, **payload_plugin["options"])

    logger.debug(
        f"Attempting to collect data from targets. NumberTargets: {len(targets)}"
    )

    collection_plugin["options"].update(kwargs)
    results = collection_plugin["plugin"].get(
        targets, commands, **collection_plugin["options"]
    )

    logger.debug("Persisting result data")

    baselines = []
    for k, v in results.items():
        persistence_plugin["options"].update(kwargs)
        persistence_plugin["plugin"].save(
            "baseline", target_key, v[0], **persistence_plugin["options"]
        )  # only one baseline
        baselines.append({target_key: v[0]})

    return {"baselines": baselines}
