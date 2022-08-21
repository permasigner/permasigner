import math

FIELD_BUILT_USING = "Built-Using"
FIELD_HOMEPAGE = "Homepage"
FIELD_DESCRIPTION = "Description"
FIELD_MAINTAINER = "Maintainer"
FIELD_INSTALLED_SIZE = "Installed-Size"
FIELD_PROVIDES = "Provides"
FIELD_CONFLICTS = "Conflicts"
FIELD_BREAKS = "Breaks"
FIELD_PRE_DEPENDS = "Pre-Depends"
FIELD_REPLACES = "Replaces"
FIELD_ENHANCES = "Enhances"
FIELD_SUGGESTS = "Suggests"
FIELD_RECOMMENDS = "Recommends"
FIELD_DEPENDS = "Depends"
FIELD_ESSENTIAL = "Essential"
FIELD_ARCHITECTURE = "Architecture"
FIELD_PRIORITY = "Priority"
FIELD_SECTION = "Section"
FIELD_VERSION = "Version"
FIELD_SOURCE = "Source"
FIELD_PACKAGE = "Package"
FIELD_NAME = "Name"
FIELD_AUTHOR = "Author"
FIELD_TAGS = "Tags"
FIELD_DEPICTION = "Depiction"

BINARY_CONTROL_ALLOWED_FIELDS = (
    FIELD_DEPICTION,
    FIELD_TAGS,
    FIELD_AUTHOR,
    FIELD_NAME,
    FIELD_PACKAGE,
    FIELD_SOURCE,
    FIELD_VERSION,
    FIELD_SECTION,
    FIELD_PRIORITY,
    FIELD_ARCHITECTURE,
    FIELD_ESSENTIAL,
    FIELD_DEPENDS,
    FIELD_RECOMMENDS,
    FIELD_SUGGESTS,
    FIELD_ENHANCES,
    FIELD_REPLACES,
    FIELD_PRE_DEPENDS,
    FIELD_BREAKS,
    FIELD_CONFLICTS,
    FIELD_PROVIDES,
    FIELD_INSTALLED_SIZE,
    FIELD_MAINTAINER,
    FIELD_DESCRIPTION,
    FIELD_HOMEPAGE,
    FIELD_BUILT_USING
)

BINARY_CONTROL_REQUIRED_FIELDS = (FIELD_PACKAGE, FIELD_VERSION, FIELD_ARCHITECTURE, FIELD_MAINTAINER, FIELD_DESCRIPTION)

BINARY_DEPENDS_ET_AL_FIELDS = (FIELD_DEPENDS, FIELD_RECOMMENDS, FIELD_SUGGESTS, FIELD_ENHANCES, FIELD_PRE_DEPENDS,
                               FIELD_BREAKS, FIELD_CONFLICTS, FIELD_PROVIDES, FIELD_REPLACES)


class BinaryControl(object):
    def __init__(self, package, version, architecture, maintainer, description):
        self._control_fields = {
            FIELD_PACKAGE: package,
            FIELD_VERSION: version,
            FIELD_ARCHITECTURE: architecture,
            FIELD_MAINTAINER: maintainer,
            FIELD_DESCRIPTION: description
        }
        self.installed_size_bytes = None

    def get_control_line(self, field_name):
        if field_name not in self._control_fields:
            raise KeyError("{} is not set.".format(field_name))

        field_value = self._control_fields[field_name]

        return "{}: {}".format(field_name, field_value)

    def get_control_line_value(self, field_name):
        if field_name not in self._control_fields:
            raise KeyError("{} is not set.".format(field_name))

        return self._control_fields[field_name]

    def set_control_field(self, field_name, field_value):
        if field_name not in BINARY_CONTROL_ALLOWED_FIELDS:
            raise KeyError("{} is not a valid field for a binary control file".format(field_name))

        self._control_fields[field_name] = field_value

    def set_control_fields(self, new_control_fields):
        for field_name, field_value in new_control_fields.items():
            self.set_control_field(field_name, field_value)

    def get_calculated_install_size_line(self):
        if self.installed_size_bytes is None:
            return None

        return '{}: {}'.format(FIELD_INSTALLED_SIZE, int(math.ceil(self.installed_size_bytes / 1024.0)))

    def get_control_text(self):
        control_lines = []
        for field_name in BINARY_CONTROL_REQUIRED_FIELDS:
            control_lines.append(self.get_control_line(field_name))

        if FIELD_INSTALLED_SIZE not in self._control_fields:
            install_size_line = self.get_calculated_install_size_line()

            if install_size_line is not None:
                control_lines.append(install_size_line)

        for field_name in BINARY_CONTROL_ALLOWED_FIELDS:
            if field_name in BINARY_CONTROL_REQUIRED_FIELDS:
                continue

            if field_name not in self._control_fields:
                continue

            control_lines.append(self.get_control_line(field_name))

        return "\n".join(control_lines) + "\n"

    def is_field_defined(self, field_name):
        return field_name in self._control_fields

    def get_default_output_name(self):
        package = self._control_fields[FIELD_PACKAGE]
        version = self._control_fields[FIELD_VERSION]
        architecture = self._control_fields[FIELD_ARCHITECTURE]

        return '{}_{}_{}.deb'.format(package, version, architecture)
