import math


class BinaryControl(object):
    def __init__(self):
        self._control_fields = {}
        self.installed_size_bytes = None

    def get_control_line(self, field_name):
        field_value = self._control_fields[field_name]

        return f"{field_name}: {field_value}"

    def get_control_line_value(self, field_name):
        return self._control_fields[field_name]

    def set_control_field(self, field_name, field_value):
        self._control_fields[field_name] = field_value

    def set_control_fields(self, new_control_fields):
        for field_name, field_value in new_control_fields.items():
            self.set_control_field(field_name, field_value)

    def get_calculated_install_size_line(self):
        return f"{'Installed-Size'}: {int(math.ceil(self.installed_size_bytes / 1024.0))}"

    def get_control_text(self):
        control_lines = []
        install_size_line = self.get_calculated_install_size_line()
        control_lines.append(install_size_line)

        for field_name in self._control_fields:
            control_lines.append(self.get_control_line(field_name))

        return "\n".join(control_lines) + "\n"

    def get_default_output_name(self):
        package = self._control_fields['Name']
        version = self._control_fields['Version']

        return f"{package.replace(' ', '')}_{version}.deb"
