import json
import os
from pathlib import Path, PurePath

from string import Template

from .configuration import PARENT_KEY, ConstrictorConfiguration

BASE_CONFIG_ENV_KEY = "CONSTRICTOR_BUILD_BASE_CONFIG_PATH"
BASE_CONFIG_PATH_DEFAULT = "~/constrictor-build-config.json"


def is_str(s):
    return isinstance(s, str)


def resolve_base_config_path(base_config_path):
    if base_config_path:
        return base_config_path

    if BASE_CONFIG_ENV_KEY in os.environ:
        return os.environ[BASE_CONFIG_ENV_KEY]

    return BASE_CONFIG_PATH_DEFAULT


class ConfigReader(object):
    def __init__(self, config_path, base_config_path=None):
        self.config_path = config_path
        self.base_config_path = Path(str(Path(resolve_base_config_path(base_config_path)).expanduser())).absolute()

    @staticmethod
    def read_json(path):
        with open(path) as config_fp:
            return json.load(config_fp)

    def load_base_config(self):
        if str(self.base_config_path) and Path(self.base_config_path).exists():
            return self.read_json(self.base_config_path)

        return {}

    def load_config_file(self, config_path):
        """
        Load a tuple of the (parent_config_path[str], config_data [dict]). parent_config_path will be None to indicate
        this is the root config (however the base_config_path config will always be the root if set).
        """
        config = self.read_json(config_path)
        return config.get(PARENT_KEY), config

    def get_configuration(self):
        resolved_configuration = ConstrictorConfiguration(self.load_base_config())

        configuration_list = []
        seen_paths = set()

        current_config_paths = [self.config_path]

        while len(current_config_paths):
            current_config_path = os.path.realpath(current_config_paths.pop(0))
            if current_config_path in seen_paths:
                raise RuntimeError(
                    "{} already loaded, possible recursive config parents.".format(current_config_paths))
            relative_parent_config_paths, configuration = self.load_config_file(current_config_path)

            configuration_list.insert(0, configuration)

            seen_paths.add(current_config_path)

            if relative_parent_config_paths is not None:
                if not isinstance(relative_parent_config_paths, list):
                    relative_parent_config_paths = [relative_parent_config_paths]

                for relative_parent_config_path in relative_parent_config_paths:
                    absolute_parent_config_path = PurePath(
                        f'{PurePath(current_config_path).parent}/{Path(relative_parent_config_path).expanduser()}')
                    current_config_paths.insert(0, str(absolute_parent_config_path))

        for configuration in configuration_list:
            resolved_configuration.update_configuration(configuration)

        resolved_configuration.interpolate_variables()
        resolved_configuration.interpolate_configuration_values()

        return resolved_configuration

    @staticmethod
    def parse_environment_variable_value(value):
        t = Template(value)
        return t.substitute(os.environ)

    def interpolate_environment_variables_in_list(self, value_list):
        for index, value in enumerate(value_list):
            if isinstance(value, dict):
                self.interpolate_environment_variables_in_dict(value)
            elif isinstance(value, list):
                self.interpolate_environment_variables_in_list(value)
            elif is_str(value):
                value_list[index] = self.parse_environment_variable_value(value)

    def interpolate_environment_variables_in_dict(self, value_dict):
        for key, value in value_dict.items():
            if isinstance(value, dict):
                self.interpolate_environment_variables_in_dict(value)
            elif isinstance(value, list):
                self.interpolate_environment_variables_in_list(value)
            elif is_str(value):
                value_dict[key] = self.parse_environment_variable_value(value)
