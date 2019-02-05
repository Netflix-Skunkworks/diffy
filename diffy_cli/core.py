import logging
import json
import yaml
import click
import click_log

from tabulate import tabulate

from diffy.filters import AWSFilter

from diffy.config import CONFIG, configure_swag
from diffy.common.utils import install_plugins
from diffy._version import __version__
from diffy.plugins.base import plugins
from diffy.core import analysis, baseline
from diffy.exceptions import DiffyException
from diffy_cli.utils.dynamic_click import CORE_COMMANDS, func_factory, params_factory

log = logging.getLogger("diffy")
log.addFilter(AWSFilter())

click_log.basic_config(log)

install_plugins()


def plugin_command_factory():
    """Dynamically generate plugin groups for all plugins, and add all basic command to it"""
    for p in plugins.all():
        plugin_name = p.slug
        help = f"Options for '{plugin_name}'"
        group = click.Group(name=plugin_name, help=help)
        for name, description in CORE_COMMANDS.items():
            callback = func_factory(p, name)
            pretty_opt = click.Option(
                ["--pretty/--not-pretty"], help="Output a pretty version of the JSON"
            )
            params = [pretty_opt]
            command = click.Command(
                name,
                callback=callback,
                help=description.format(plugin_name),
                params=params,
            )
            group.add_command(command)

        plugins_group.add_command(group)


def get_plugin_properties(json_schema):
    for k, v in json_schema["definitions"].items():
        return v["properties"]


def add_plugins_args(f):
    """Adds installed plugin options."""
    schemas = []
    if isinstance(f, click.Command):
        for p in plugins.all():
            schemas.append(get_plugin_properties(p.json_schema))
        f.params.extend(params_factory(schemas))
    else:
        if not hasattr(f, "__click_params__"):
            f.__click_params__ = []

        for p in plugins.all():
            schemas.append(get_plugin_properties(p.json_schema))
        f.__click_params__.extend(params_factory(schemas))
    return f


class YAML(click.ParamType):
    name = "yaml"

    def convert(self, value: str, param: str, ctx: object) -> dict:
        try:
            with open(value, "rb") as f:
                return yaml.safe_load(f.read())
        except (IOError, OSError) as e:
            self.fail(f"Could not open file: {value}")


def get_plugin_callback(ctx: object, param: str, value: str) -> object:
    """Ensures that the plugin selected is available."""
    for p in plugins.all(plugin_type=param.name.split("_")[0]):
        if p.slug == value:
            return {"plugin": p, "options": {}}

    raise click.BadParameter(
        f"Could not find appropriate plugin. Param: {param.name} Value: {value}"
    )


@click.group()
@click_log.simple_verbosity_option(log)
@click.option("--config", type=YAML(), help="Configuration file to use.")
@click.option(
    "--dry-run",
    type=bool,
    default=False,
    is_flag=True,
    help="Run command without persisting anything.",
)
@click.version_option(version=__version__)
@click.pass_context
def diffy_cli(ctx, config, dry_run):
    return


#    if not ctx.dry_run:
#        ctx.dry_run = dry_run
#
#    if config:
#        CONFIG.from_yaml(config)
#
#    log.debug(f'Current context. DryRun: {ctx.dry_run} Config: {json.dumps(CONFIG, indent=2)}')


@diffy_cli.group("plugins")
def plugins_group():
    pass


@plugins_group.command("list")
def list_plugins():
    """Shows all available plugins"""
    table = []
    for p in plugins.all():
        table.append([p.title, p.slug, p.version, p.author, p.description])
    click.echo(
        tabulate(table, headers=["Title", "Slug", "Version", "Author", "Description"])
    )


@diffy_cli.group()
def new():
    pass


@new.command('baseline')
@click.argument('target-key')
@click.option('--target-plugin', default='local-target', callback=get_plugin_callback)
# TODO: Make 'target' and 'inventory' plugins mutually exclusive
# TODO: Consider an 'async' flag
@click.option('--inventory-plugin', callback=get_plugin_callback)
@click.option('--persistence-plugin', default='local-file', callback=get_plugin_callback)
@click.option('--payload-plugin', default='local-command', callback=get_plugin_callback)
@click.option('--collection-plugin', default='local-shell-collection', callback=get_plugin_callback)
@click.option('--incident-id', default='None')
@add_plugins_args
def baseline_command(
    target_key,
    target_plugin,
    inventory_plugin,
    persistence_plugin,
    payload_plugin,
    collection_plugin,
    incident_id,
    **kwargs,
):
    """Creates a new baseline based on the given ASG."""
    if inventory_plugin:
        for item in inventory_plugin['plugin'].get():
            target_plugin['options'] = item['options']
            baseline(
                item['target'],
                item['target_plugin'],
                payload_plugin,
                collection_plugin,
                persistence_plugin,
                incident_id=incident_id,
                **kwargs,
            )

    baselines = baseline(
        target_key,
        target_plugin,
        payload_plugin,
        collection_plugin,
        persistence_plugin,
        incident_id=incident_id,
        **kwargs,
    )
    click.secho(json.dumps(baselines), fg="green")


@new.command('analysis')
@click.argument('target-key')
@click.option('--analysis-plugin', default='local-simple', callback=get_plugin_callback)
@click.option('--payload-plugin', default='local-command', callback=get_plugin_callback)
@click.option('--target-plugin', default='local-target', callback=get_plugin_callback)
@click.option('--persistence-plugin', default='local-file', callback=get_plugin_callback)
@click.option('--collection-plugin', default='local-shell-collection', callback=get_plugin_callback)
@click.option('--incident-id', default='')
@add_plugins_args
def analysis_command(target_key, analysis_plugin, target_plugin, persistence_plugin, collection_plugin, payload_plugin,
                    incident_id, **kwargs):
    """Creates a new analysis based on collected data."""
    result = analysis(
        target_key,
        target_plugin,
        payload_plugin,
        collection_plugin,
        persistence_plugin,
        analysis_plugin,
        **kwargs,
    )

    for r in result['analysis']:
        if r['diff']:
            click.secho(
                r['instance_id'] + ': Differences found.',
                fg='red')
            click.secho(json.dumps(r['diff'], indent=2), fg='red')
        else:
            click.secho(r["instance_id"] + ": No Differences Found.", fg="green")


def entry_point():
    """The entry that CLI is executed from"""
    try:
        configure_swag()
        plugin_command_factory()
        diffy_cli(obj={"dry_run": True})
    except DiffyException as e:
        click.secho(f"ERROR: {e.message}", bold=True, fg="red")
        exit(1)


if __name__ == "__main__":
    entry_point()
