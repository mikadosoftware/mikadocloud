# -*- coding: utf-8 -*-

'''
  confd = conf.get_config("/ini/file/path")

We now have a python dict, named confd, holding all the namesapced
configuration variables available in the "environment"

it would look like ::

  {
   'bamboo':
       {'www_host_name':"www.example.org",},
   'flagpole':
       {'flag': "RedWhiteBlue"}
  }



>>> x = """[test]
... foo=1
...
... [test2]
... bar=1
... """
>>> open("/tmp/foo.ini", "w").write(x)
>>> d = get_config(ini_file_path="/tmp/foo.ini")
>>> expected = {'test': {'foo': '1'}, 'test2': {'bar': '1'}}
>>> assert d == expected

'''

## root logger set in application startup
import logging
logging.basicConfig(level=logging.INFO)
lgr = logging.getLogger(__name__)

import os
import ConfigParser
import types

class ConfigError(Exception):
    pass

    
def get_config(ini_file_path=None):
    """
    Expect a .ini file at path location, parse and return dict

    """
    confd = {}
    if not os.path.isfile(ini_file_path):
        raise ConfigError("%s is not found" % ini_file_path)
    try:
        d = read_ini(ini_file_path)
        confd.update(d)
    except Exception, e:
        lgr.error("unable to parse conf file %s because %s" %
                  (ini_file_path, str(e)))
        raise e
    return confd


def read_ini(filepath):

    d = {}
    parser = ConfigParser.SafeConfigParser()
    parser.optionxform = str  # case sensitive
    try:
        parser.read(filepath)
    except Exception, e:
        raise ConfigError(
            'Could not find or could not process: %s - %s' % (filepath, e))

    ## convert ini file to a dict of dicts
    for sect in parser.sections():
        d[sect] = dict(parser.items(sect))


    return d


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
