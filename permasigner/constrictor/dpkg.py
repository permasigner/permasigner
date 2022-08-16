import os
import fnmatch
from functools import partial
from io import BytesIO
import tarfile
import tempfile
import time

from .ar import ARWriter
from .control import FIELD_INSTALLED_SIZE
from .helpers import md5_for_path

MAINTAINER_SCRIPT_NAMES = ('preinst', 'postinst', 'prerm', 'postrm')
TAR_INFO_KEYS = ('uname', 'gname', 'uid', 'gid', 'mode')
FORCE_DIRECTORY_INCLUSION_FILENAMES = (".debkeep", ".gitkeep")
DEBIAN_BINARY_VERSION = '2.0'
TAR_DEFAULT_MODE = 0o755
AR_DEFAULT_MODE = 0o644

LINK_PATH_KEY = "path"
LINK_TARGET_KEY = "target"


def generate_directories(path, existing_dirs=None):
    """Recursively build a list of directories inside a path."""
    existing_dirs = existing_dirs or []
    directory_name = os.path.dirname(path)

    if directory_name == '.':
        return

    existing_dirs.append(directory_name)
    generate_directories(directory_name, existing_dirs)

    return existing_dirs


class DPKGBuilder(object):
    """
    Finds files to use, builds tar archive and then archives into ar format. Builds + includes debian control files.
    """

    def __init__(self, output_directory, control, data_dirs, links, maintainer_scripts=None, output_name=None,
                 ignore_paths=None, configuration_files=None):
        self.output_directory = os.path.expanduser(output_directory)
        self.data_dirs = data_dirs or []
        self.links = links or {}
        self.maintainer_scripts = maintainer_scripts
        self.seen_data_dirs = set()
        self.working_dir = tempfile.mkdtemp()
        self.control = control
        self.output_name = output_name or control.get_default_output_name()
        self.ignore_paths = ignore_paths or []
        self.configuration_files = configuration_files or []
        self.actual_config_files = []

    @staticmethod
    def path_matches_glob_list(glob_list, path):
        path_matcher = partial(fnmatch.fnmatch, path)
        return any(map(path_matcher, glob_list))

    def should_skip_path(self, path):
        return self.path_matches_glob_list(self.ignore_paths, path)

    def path_is_config(self, path):
        return self.path_matches_glob_list(self.configuration_files, path)

    def list_data_dir(self, source_dir):
        """
        Iterator to recursively list all files in a directory that should be included. Returns a tuple of absolute
        file_path (on local) and the relative path (relative to source).
        If the file name matches a filename to skip (should_skip_file returns true) it will not be returned.
        """
        for root_dir, dirs, files in os.walk(source_dir):
            for file_name in files:
                file_path = os.path.join(root_dir, file_name)
                relative_path = file_path[len(source_dir):]

                if self.should_skip_path(relative_path):
                    continue

                yield file_path, relative_path

    def add_directory_root_to_archive(self, archive, dir_conf, file_path):
        for directory in reversed(generate_directories(file_path)):
            if directory in self.seen_data_dirs:
                continue

            dir_ti = tarfile.TarInfo()
            dir_ti.type = tarfile.DIRTYPE
            dir_ti.name = directory
            dir_ti.mtime = int(time.time())
            dir_ti.mode = TAR_DEFAULT_MODE
            dir_ti = self.filter_tar_info(dir_ti, dir_conf)
            archive.addfile(dir_ti)

            self.seen_data_dirs.add(directory)

    @staticmethod
    def filter_tar_info(tar_info, dir_conf):
        for tar_info_key in TAR_INFO_KEYS:
            if dir_conf.get(tar_info_key) is not None:
                setattr(tar_info, tar_info_key, dir_conf[tar_info_key])

        if 'uid' in dir_conf and 'uname' not in dir_conf:
            tar_info.uname = ''

        if 'gid' in dir_conf and 'gname' not in dir_conf:
            tar_info.gname = ''

        return tar_info

    @property
    def data_archive_path(self):
        return os.path.join(self.working_dir, 'data.tar.gz')

    @staticmethod
    def open_tar_file(path):
        tf = tarfile.open(path, 'w:gz')
        tf.format = tarfile.USTAR_FORMAT
        return tf

    def build_data_archive(self):
        data_tar_file = self.open_tar_file(self.data_archive_path)
        file_size_bytes = 0

        file_md5s = []

        for dir_conf in self.data_dirs:
            source_dir = os.path.expanduser(dir_conf['source'])

            for source_file_path, source_file_name in self.list_data_dir(source_dir):
                if source_file_name.startswith('/'):
                    source_file_name = source_file_name[1:]
                archive_path = '.' + os.path.join(dir_conf['destination'], source_file_name)

                if os.path.islink(source_file_path) and not os.path.exists(source_file_path):
                    # this is a link to a file that doesn't exist but should when we deploy if we are on the same OS
                    # (e.g. venv build with docker and .deb assembled on host) so add it as a link
                    self.links.append({
                        LINK_PATH_KEY: archive_path,
                        LINK_TARGET_KEY: os.readlink(source_file_path)
                    })
                else:
                    self.add_directory_root_to_archive(data_tar_file, dir_conf, archive_path)
                    if os.path.basename(source_file_name) in FORCE_DIRECTORY_INCLUSION_FILENAMES:
                        continue

                    file_size_bytes += os.path.getsize(source_file_path)

                    file_md5s.append((md5_for_path(source_file_path), archive_path))
                    data_tar_file.add(source_file_path, arcname=archive_path, recursive=False,
                                      filter=lambda ti: self.filter_tar_info(ti, dir_conf))

                    config_path = archive_path[1:] if archive_path.startswith(".") else archive_path

                    if config_path not in self.actual_config_files and self.path_is_config(config_path):
                        self.actual_config_files.append(config_path)

        for symlink_conf in self.links:
            target = symlink_conf[LINK_TARGET_KEY]
            path = symlink_conf[LINK_PATH_KEY]

            if not path.startswith('.'):
                path = '.' + path

            self.add_directory_root_to_archive(data_tar_file, symlink_conf, path)
            link_ti = self.build_link_tarinfo(symlink_conf, target, path)

            data_tar_file.addfile(link_ti)
            file_size_bytes += len(path)

        data_tar_file.close()

        return file_size_bytes, file_md5s

    def build_link_tarinfo(self, symlink_conf, target, path):
        link_ti = tarfile.TarInfo()
        link_ti.type = tarfile.SYMTYPE
        link_ti.linkname = target
        link_ti.name = path
        link_ti.mtime = int(time.time())
        link_ti = self.filter_tar_info(link_ti, symlink_conf)
        return link_ti

    @staticmethod
    def build_member_from_string(name, content):
        content_file = BytesIO(content)
        member = tarfile.TarInfo()
        member.type = tarfile.REGTYPE
        member.name = name
        member.mtime = int(time.time())
        member.uname = 'root'
        member.gname = 'root'
        member.size = len(content)
        return member, content_file

    @staticmethod
    def validate_maintainer_scripts(maintainer_scripts):
        for script_name in maintainer_scripts.keys():
            if script_name not in MAINTAINER_SCRIPT_NAMES:
                raise ValueError("Unknown maintainer script {}".format(script_name))

    @staticmethod
    def filter_maintainer_script_tar_info(tar_info):
        tar_info.uid = 0
        tar_info.gid = 0
        tar_info.mode = TAR_DEFAULT_MODE
        return tar_info

    @property
    def control_archive_path(self):
        return os.path.join(self.working_dir, 'control.tar.gz')

    def build_control_archive(self, control_text, file_md5s, maintainer_scripts):
        maintainer_scripts = maintainer_scripts or {}
        self.validate_maintainer_scripts(maintainer_scripts)

        control_tar = self.open_tar_file(self.control_archive_path)

        for script_name, script_path in maintainer_scripts.items():
            control_tar.add(script_path, arcname=script_name, filter=self.filter_maintainer_script_tar_info)

        control_tar.addfile(*self.build_member_from_string('./control', control_text.encode()))

        md5sum_text = '\n'.join(['  '.join(md5_file_pair) for md5_file_pair in file_md5s]) + '\n'
        control_tar.addfile(*self.build_member_from_string('./md5sums', md5sum_text.encode()))

        if self.actual_config_files:
            conf_file_text = '\n'.join(self.actual_config_files) + "\n"
            control_tar.addfile(*self.build_member_from_string('./conffiles', conf_file_text.encode()))

        control_tar.close()

    def assemble_deb_archive(self, control_archive_path, data_archive_path):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        pkg_path = os.path.join(self.output_directory, self.output_name)

        with open(pkg_path, 'wb') as ar_fp:
            ar_writer = ARWriter(ar_fp)

            ar_writer.archive_text("debian-binary", "{}\n".format(DEBIAN_BINARY_VERSION), int(time.time()), 0, 0,
                                   AR_DEFAULT_MODE)
            ar_writer.archive_file(control_archive_path, int(time.time()), 0, 0, AR_DEFAULT_MODE)
            ar_writer.archive_file(data_archive_path, int(time.time()), 0, 0, AR_DEFAULT_MODE)

        return pkg_path

    def build_package(self):
        file_size_bytes, file_md5s = self.build_data_archive()

        if not self.control.is_field_defined(FIELD_INSTALLED_SIZE):
            self.control.installed_size_bytes = file_size_bytes

        self.build_control_archive(self.control.get_control_text(), file_md5s, self.maintainer_scripts)

        return self.assemble_deb_archive(self.control_archive_path, self.data_archive_path)
