from functools import partial
from os import environ
from string import Template

from .dpkg import LINK_PATH_KEY

PARENT_KEY = "parent"
DEB_CONSTRICTOR_KEY = "deb_constrictor"
IGNORE_PATHS_KEY = "ignore_paths"
VARIABLES_KEY = "variables"
ENVIRONMENT_VARIABLES_KEY = "environment_variables"
EXTRA_CONTROL_FIELDS_KEY = "extra_control_fields"
DEPENDS_KEY = "Depends"
PROVIDES_KEY = "Provides"
DIRECTORIES_KEY = "directories"
LINKS_KEY = "links"
COMMANDS_KEY = "commands"
MAINTAINER_SCRIPTS_KEY = "maintainer_scripts"
CONFIG_FILES_KEY = "configuration_files"
DIRECTORY_PATH_KEYS = ('source', 'destination')


def ensure_trailing_slash(path):
    """Return path if path ends with a / or path + / if it doesn't."""
    return path if path.endswith('/') else path + '/'


def ensure_trailing_slashes_in_directory(directory):
    """Return a directory entry where all path entries will be guaranteed to have a trailing /"""
    new_directory = {}
    new_directory.update(directory)
    for path_type in DIRECTORY_PATH_KEYS:
        new_directory[path_type] = ensure_trailing_slash(directory[path_type])

    return new_directory


def extract_directory_paths(directory):
    """Return a dictionary for a directory containing only the path items."""
    return {k: v for k, v in directory.items() if k in DIRECTORY_PATH_KEYS}


def directory_entries_equal(dir1, dir2):
    """Compare two directory entries, considered equal if only the path items match."""
    dir1_paths, dir2_paths = map(extract_directory_paths, map(ensure_trailing_slashes_in_directory, (dir1, dir2)))
    return dir1_paths == dir2_paths


def directory_entries_not_equal(dir1, dir2):
    """Negate directory_entries_equal function (for use when inverse is required in map()/filter() call)"""
    return not directory_entries_equal(dir1, dir2)


def interpolate_value(v, context):
    if isinstance(v, dict):
        interpolate_dictionary(v, context)
        return None
    elif isinstance(v, list):
        interpolate_list(v, context)
        return None
    elif isinstance(v, (bool, int, float)):
        return None
    else:
        return Template(v).substitute(context)


def interpolate_list(list_, context):
    """Walk through list and interpolate variables for each value."""
    for i, v in enumerate(list_):
        interpolated = interpolate_value(v, context)
        if interpolated is not None:
            list_[i] = interpolated


def interpolate_dictionary(d, context):
    """Walk through dictionary and interpolate variables for each value."""
    for k, v in d.items():
        if k == COMMANDS_KEY:  # don't interpolate commands at build time as some variables are passed in at run time
            continue
        interpolated = interpolate_value(v, context)
        if interpolated is not None:
            d[k] = interpolated


class ConstrictorConfiguration(object):
    """
    Configuration for the DpkgBuilder. Should be instantiated with the root config dict, and then updated with child
    (overriding) configuration dictionaries by calling the update_configuration method with reach child.
    """

    def __init__(self, base_configuration):
        self.configuration = {}
        self.environment_variables = {}
        self.variables = {}
        self.update_configuration(base_configuration)

    def update_configuration(self, configuration):
        """
        Override the existing configuration with the new values. Is more advanced than just doing old[k] = new[k] as it
        is also aware of what items are lists and should be appended to.
        """
        for k, v in configuration.items():
            if k == PARENT_KEY:
                continue
            elif k == DEB_CONSTRICTOR_KEY:
                self.update_deb_constrictor_configuration(v)
            elif k == EXTRA_CONTROL_FIELDS_KEY:
                self.update_extra_control_fields(v)
            elif k == DIRECTORIES_KEY:
                self.update_directory_entries(v)
            elif k == LINKS_KEY:
                self.update_link_entries(v)
            elif k == MAINTAINER_SCRIPTS_KEY:
                self.update_maintainer_scripts(v)
            elif k == CONFIG_FILES_KEY:
                self.update_configuration_files(v)
            else:
                self.configuration[k] = v

    def update_deb_constrictor_configuration(self, configuration):
        """
        Updates items in the DEB_CONSTRICTOR_KEY value dict with new items. Will append items to lists where
        appropriate.
        """
        if DEB_CONSTRICTOR_KEY not in self.configuration:
            self.configuration[DEB_CONSTRICTOR_KEY] = {}

        for k, v in configuration.items():
            if k == IGNORE_PATHS_KEY:
                self.update_ignore_paths(v)
            elif k in (VARIABLES_KEY, ENVIRONMENT_VARIABLES_KEY):
                self.update_variables(k, v)
            elif k == COMMANDS_KEY:
                self.update_commands(v)
            else:
                self.configuration[DEB_CONSTRICTOR_KEY][k] = v

    def update_ignore_paths(self, ignore_paths):
        """
        Updates the IGNORE_PATHS_KEY list in the DEB_CONSTRICTOR_KEY dict with the passed in list. Will only add the
        path if it does not exist in the list already (no duplicates).
        """
        if IGNORE_PATHS_KEY not in self.configuration[DEB_CONSTRICTOR_KEY]:
            self.configuration[DEB_CONSTRICTOR_KEY][IGNORE_PATHS_KEY] = []

        for ignore_path in ignore_paths:
            if ignore_path not in self.configuration[DEB_CONSTRICTOR_KEY][IGNORE_PATHS_KEY]:
                self.configuration[DEB_CONSTRICTOR_KEY][IGNORE_PATHS_KEY].append(ignore_path)

    def update_extra_control_fields(self, control_fields):
        """
        Updates existing EXTRA_CONTROL_FIELDS_KEY dictionary with items from the passed in dictionary. Appends
        (uniquely) to list type items instead of overriding.
        """
        if EXTRA_CONTROL_FIELDS_KEY not in self.configuration:
            self.configuration[EXTRA_CONTROL_FIELDS_KEY] = {}

        for k, v in control_fields.items():
            if k in (DEPENDS_KEY, PROVIDES_KEY):
                self.update_extra_control_field_list(k, v)
            else:
                self.configuration[EXTRA_CONTROL_FIELDS_KEY][k] = v

    def update_extra_control_field_list(self, control_field_name, new_list):
        """
        Appends items in new_list to the given key (control_field_name) in the EXTRA_CONTROL_FIELDS_KEY dictionary.
        Makes sure items are unique.
        """
        if control_field_name not in self.configuration[EXTRA_CONTROL_FIELDS_KEY]:
            self.configuration[EXTRA_CONTROL_FIELDS_KEY][control_field_name] = []

        for field_item in new_list:
            if field_item not in self.configuration[EXTRA_CONTROL_FIELDS_KEY][control_field_name]:
                self.configuration[EXTRA_CONTROL_FIELDS_KEY][control_field_name].append(field_item)

    def update_directory_entries(self, directories_list):
        """
        Append the given directory entries in directories_list to the existing directories in the configuration.
        Existing directories are removed and replaced if they have the same source and destination as an incoming entry
        (as there may be legitimate cases to source the same destination to multiple targets or multiple sources to the
        same target [if they contain different files] so if either differ to an existing entry it will be added).
        """
        if DIRECTORIES_KEY not in self.configuration:
            self.configuration[DIRECTORIES_KEY] = []

        for new_directory in directories_list:
            self.configuration[DIRECTORIES_KEY] = list(filter(partial(directory_entries_not_equal, new_directory),
                                                              self.configuration[DIRECTORIES_KEY]))
            self.configuration[DIRECTORIES_KEY].append(new_directory)

    def update_link_entries(self, links_list):
        """
        Append the given links in the links_list to the existing links in the configuration. Existing link entries are
        removed and replaced with incoming if they match on the source field only (as it doesn't make sense to create
        two links in the same place).
        """
        if LINKS_KEY not in self.configuration:
            self.configuration[LINKS_KEY] = []

        for new_link in links_list:
            self.configuration[LINKS_KEY] = list(filter(lambda link: link[LINK_PATH_KEY] != new_link[LINK_PATH_KEY],
                                                        self.configuration[LINKS_KEY]))
            self.configuration[LINKS_KEY].append(new_link)

    def update_maintainer_scripts(self, maintainer_scripts):
        """Override existing maintainer script keys with the new ones."""
        if MAINTAINER_SCRIPTS_KEY not in self.configuration:
            self.configuration[MAINTAINER_SCRIPTS_KEY] = {}

        self.configuration[MAINTAINER_SCRIPTS_KEY].update(maintainer_scripts)

    def update_configuration_files(self, configuration_files):
        """Append configuration files to existing."""
        if CONFIG_FILES_KEY not in self.configuration:
            self.configuration[CONFIG_FILES_KEY] = []

        self.configuration[CONFIG_FILES_KEY] += list(
            filter(lambda path: path not in self.configuration[CONFIG_FILES_KEY], configuration_files))

    def update_variables(self, variables_key, new_variables):
        """
        Append the list of variables to the given variables_key. Does not do de-duplication of the variable name as it
        might be good to have parent variables populate and the be able to be used in a child config.
        """
        if variables_key not in self.configuration[DEB_CONSTRICTOR_KEY]:
            self.configuration[DEB_CONSTRICTOR_KEY][variables_key] = []

        self.configuration[DEB_CONSTRICTOR_KEY][variables_key] += new_variables

    def update_commands(self, commands):
        if COMMANDS_KEY not in self.configuration[DEB_CONSTRICTOR_KEY]:
            self.configuration[DEB_CONSTRICTOR_KEY][COMMANDS_KEY] = {}

        self.configuration[DEB_CONSTRICTOR_KEY][COMMANDS_KEY].update(commands)

    def interpolate_variables(self):
        """
        Should be called before variables are used, when we have finished updating all configs down the hierarchy, to
        interpolate the variables with variables before they can be used.
        """
        self.store_variable_list(VARIABLES_KEY, self.variables)
        self.store_variable_list(ENVIRONMENT_VARIABLES_KEY, self.environment_variables)

    def store_variable_list(self, variables_list_key, variables_container):
        """
        Interpolate each variable in the variables list (a list of lists, each item is [key, value]) and store it in the
        dictionary for use later, i.e: [[k, v]] => {k: interpolate_value(v)}

        Because the items are processed in order, items further along the list might be interpolated with variables set
        by earlier elements.
        """
        for k, v in self.configuration[DEB_CONSTRICTOR_KEY].get(variables_list_key, []):
            variables_container[k] = self.interpolate_value(v)

    def get_template_context(self):
        """
        Template context (for interpolating variables) is os.environ, which is overridden by self.environment_variables
        and then overridden by self.variables.

        If you wanted to be more performant you would cache the ctx and invalidate it when the var variables change, but
        I don't foresee this being an issue.
        """
        ctx = dict(environ)
        ctx.update(self.environment_variables)
        ctx.update(self.variables)
        return ctx

    def interpolate_value(self, value):
        return interpolate_value(value, self.get_template_context())

    def interpolate_configuration_values(self):
        """
        Recurse through the configuration and interpolate all the values with the template context. This should be
        called after all the configurations have been loaded (parent hierarchy resolved and updated) and then
        interpolate_variables called.
        """
        interpolate_dictionary(self.configuration, self.get_template_context())

    def __getitem__(self, item):
        return self.configuration[item]

    def get(self, item, default=None):
        return self.configuration.get(item, default)
