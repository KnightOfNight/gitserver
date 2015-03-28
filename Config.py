

import ConfigParser
import os

from GitServer import fatal_error


def get():
    config_opts = {
        'log_file' : '',
        'repo_dir' : '',
        'database' : '',
    }

    config = ConfigParser.ConfigParser()

    config_files = config.read(['/etc/gitserver.cfg', os.path.expanduser('~/.gitserver.cfg')])

    if not config_files:
        fatal_error('configuration file not found')

    if not config.has_section('default'):
        fatal_error('configuration error, [default] section not found')

    for opt in config_opts:
        if not config.has_option('default', opt):
            fatal_error('configuration error, [default] section missing option "%s"' % opt)

        config_opts[opt] = config.get('default', opt)

        if not config_opts[opt]:
            fatal_error('configuration error, option "%s" is empty' % opt)

    return(config_opts)

