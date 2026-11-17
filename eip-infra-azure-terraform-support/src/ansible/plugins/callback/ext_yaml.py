from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: ext_yaml
    type: stdout
    short_description: yaml-ized Ansible screen output
    version_added: 2.9
    description:
        - Ansible output that can be quite a bit easier to read than the
          default JSON formatting.
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout in configuration
'''

from ansible import constants as C
try:
    # ansible versions 2.10 and above need to install ansible_collections
    from ansible_collections.community.general.plugins.callback.yaml import CallbackModule as ExtYaml
except ImportError:
    from ansible.plugins.callback.yaml import CallbackModule as ExtYaml

class CallbackModule(ExtYaml):
    """
    Variation of the Default output which uses nicely readable YAML instead
    of JSON for printing results.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'ext_yaml'
    # Override
    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        msg = "RETRYING: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
        if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
            msg += "Result was: %s" % self._dump_results(result._result)
        self._display.display(msg, color=C.COLOR_DEBUG)
