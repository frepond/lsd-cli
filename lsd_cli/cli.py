from __future__ import unicode_literals

import gc
import logging
import traceback
from os.path import expanduser

import pkg_resources  # part of setuptools

import click
from lsd_cli import lsd
from lsd_cli.lsd import Lsd
from lsd_cli.shell_cmd import _loadconf, process_input
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from xtermcolor import colorize

VERSION = pkg_resources.require("lsd-cli")[0].version
click.disable_unicode_literals_warning = True
HOME = expanduser("~")
HISTORY = FileHistory(HOME + '/.lsd-cli_history')
CLI_RC = HOME + '/.lsdclirc'
AUTO_SUGGEST = AutoSuggestFromHistory()
SHELL_CTX = {
    'lsd_api': None,
    'json_mode_enabled': False,
    'vi_mode_enabled': True,
    'prefix_mapping': {},
    'rules': [],
    'includes': [],
    'limit': 1000
}
STYLE = style_from_dict({
    Token.Prompt: '#ffc853',
    Token.Toolbar: '#ffffff bg:#298594'
})


def get_bottom_toolbar_tokens(cli):
    text = 'Vi' if SHELL_CTX['vi_mode_enabled'] else 'Emacs'
    output = 'Json' if SHELL_CTX['json_mode_enabled'] else 'Tabular'
    limit = SHELL_CTX['limit']

    return [(Token.Toolbar, '|lsd-cli v{}| '.format(VERSION)),
            (Token.Toolbar, ' h() Help '),
            (Token.Toolbar, ' [F4] %s ' % text),
            (Token.Toolbar, ' [F5] %s ' % output),
            (Token.Toolbar, ' [LIMIT] %s ' % limit),
            (Token.Toolbar, ' (%0.2fms/%0.2fms, %d rows) '
             % (lsd.cli_time, lsd.lsd_time, lsd.tuples))]


def get_title():
    return 'lsd-cli v{0}'.format(VERSION)


@click.command()
@click.option('--host', '-h', default='localhost', help='LSD host.', show_default=True)
@click.option('--port', '-p', default=10018, type=int, help='LSD port.', show_default=True)
@click.option('--verbose', '-v', is_flag=True)
@click.argument('tenant', default='leapsight', required=False)
def main(tenant, host, port, verbose):
    """Leapsight Semantic Dataspace Command Line Tool"""
    # Create a set of key bindings that have Vi mode enabled if the
    # ``vi_mode_enabled`` is True.
    if verbose:
        fmt = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=fmt)

    # try to connect to lsd
    try:
        SHELL_CTX['lsd_api'] = Lsd(tenant, host, port)
    except Exception as e:
        click.echo(colorize('ERROR: connection refused {0}:{1}({2})'.format(
            host, port, tenant), rgb=0xE11500))
        logging.debug(e)

        exit(1)

    manager = KeyBindingManager.for_prompt(
        enable_vi_mode=Condition(lambda cli: SHELL_CTX['vi_mode_enabled']))

    # add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F4)
    def _f4(_event):
        """ Toggle between Emacs and Vi mode. """
        SHELL_CTX['vi_mode_enabled'] = not SHELL_CTX['vi_mode_enabled']

    # add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F5)
    def _f5(_event):
        """ Toggle between Json and Tabular mode. """
        SHELL_CTX['json_mode_enabled'] = not SHELL_CTX['json_mode_enabled']

    # add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F6)
    def _f6(_event):
        """ Toggle between Json and Tabular mode. """
        SHELL_CTX['pretty_print'] = not SHELL_CTX['pretty_print']

    click.clear()
    click.echo(colorize("""
Welcome to    _/         _/_/_/_/    _/_/_/
             _/         _/          _/    _/
            _/         _/_/_/_/    _/    _/
           _/               _/    _/    _/
          _/_/_/_/   _/_/_/_/    _/_/_/      command line interface!
"""
                        , rgb=0x2cb9d0))

    ll_completer = WordCompleter(
        ['@prefix prefix: <uri>.', '@include <uri>.', '++().', '--().', '+().', '-().',
         '?().', 'import(filename)', 'export(filename)', 'help()', 'clear()', 'limit(n)'
         'loadconf(filename)', 'loadll(filename)', 'loadrs(uri, filename)', 'listrs()',
         'listm()'])

    # load init file ~/lsd-cli.rc
    try:
        _loadconf(SHELL_CTX, CLI_RC)
    except Exception:
        pass

    while True:
        input_str = prompt('lsd> ', history=HISTORY, auto_suggest=AUTO_SUGGEST,
                           get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                           style=STYLE, vi_mode=SHELL_CTX['vi_mode_enabled'],
                           key_bindings_registry=manager.registry,
                           get_title=get_title, completer=ll_completer)
        try:
            gc.disable()
            if input_str:
                process_input(SHELL_CTX, input_str.strip())
        except Exception as e:
            click.echo(colorize(e, rgb=0xE11500))
            logging.debug(traceback.print_exc())
        finally:
            gc.enable()
