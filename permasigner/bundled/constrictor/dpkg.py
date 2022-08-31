import os
import fnmatch
import sys
from functools import partial
import tarfile
import tempfile
import time
from pathlib import Path, PurePath

from .ar import ARWriter

TAR_INFO_KEYS = ('uname', 'gname', 'uid', 'gid', 'mode')
DEBIAN_BINARY_VERSION = '2.0'
TAR_DEFAULT_MODE = 0o755
AR_DEFAULT_MODE = 0o644

LINK_PATH_KEY = "path"
LINK_TARGET_KEY = "target"


class DPKGBuilder(object):
    """
    Finds files to use, builds tar archive and then archives into ar format. Builds + includes debian control files.
    """

    def __init__(self, output_directory, executables, data_dirs, control, scripts):
        self.output_directory = Path(output_directory).expanduser()
        self.data_dirs = data_dirs or []
        self.control = control
        self.maintainer_scripts = scripts
        self.executables = executables
        self.seen_data_dirs = set()
        self.working_dir = None

    @staticmethod
    def path_matches_glob_list(glob_list, path):
        path_matcher = partial(fnmatch.fnmatch, path)
        return any(map(path_matcher, glob_list))

    def generate_directories(self, path, existing_dirs=None):
        """Recursively build a list of directories inside a path."""
        existing_dirs = existing_dirs or []
        directory_name = os.path.dirname(path)

        if directory_name == '.':
            return

        existing_dirs.append(directory_name)
        self.generate_directories(directory_name, existing_dirs)

        return existing_dirs

    @staticmethod
    def list_data_dir(source_dir):
        """
        Iterator to recursively list all files in a directory that should be included. Returns a tuple of absolute
        file_path (on local) and the relative path (relative to source).
        If the file name matches a filename to skip (should_skip_file returns true) it will not be returned.
        """
        for root_dir, dirs, files in os.walk(source_dir):
            for file_name in files:
                file_path = str(PurePath(root_dir).joinpath(file_name))
                relative_path = file_path[len(str(source_dir)):]

                yield file_path, relative_path

    def add_directory_root_to_archive(self, archive, file_path):
        for directory in reversed(self.generate_directories(file_path)):
            if directory in self.seen_data_dirs:
                continue

            dir_ti = tarfile.TarInfo()
            dir_ti.type = tarfile.DIRTYPE
            dir_ti.name = directory
            dir_ti.mtime = int(time.time())
            dir_ti.mode = TAR_DEFAULT_MODE
            archive.addfile(dir_ti)

            self.seen_data_dirs.add(directory)

    def filter_tar_info(self, tar_info):
        if tar_info.name in self.executables:
            tar_info.mode = TAR_DEFAULT_MODE
            tar_info.uname = 'root'
            tar_info.gname = 'wheel'

        return tar_info

    @property
    def data_archive_path(self):
        return self.working_dir / 'data.tar.xz'

    @staticmethod
    def open_tar_file(path):
        tf = tarfile.open(path, 'w:xz')
        tf.format = tarfile.GNU_FORMAT
        return tf

    def build_data_archive(self):
        data_tar_file = self.open_tar_file(self.data_archive_path)

        for dir_conf in self.data_dirs:
            source_dir = Path(dir_conf['source']).expanduser()

            for source_file_path, source_file_name in self.list_data_dir(source_dir):
                if sys.platform == 'win32':
                    source_file_name = source_file_name.replace('\\', '/')

                archive_path = f'.{dir_conf["destination"]}{source_file_name}'

                self.add_directory_root_to_archive(data_tar_file, archive_path)

                data_tar_file.add(source_file_path, arcname=archive_path, recursive=False,
                                  filter=lambda ti: self.filter_tar_info(ti))

        data_tar_file.close()

    @staticmethod
    def filter_control_tar_info(tar_info):
        tar_info.type = tarfile.REGTYPE
        tar_info.mtime = int(time.time())
        tar_info.uname = 'root'
        tar_info.gname = 'wheel'
        return tar_info

    @staticmethod
    def filter_maintainer_script_tar_info(tar_info):
        tar_info.uid = 0
        tar_info.gid = 0
        tar_info.mode = TAR_DEFAULT_MODE
        return tar_info

    @property
    def control_archive_path(self):
        return self.working_dir / 'control.tar.xz'

    def build_control_archive(self, maintainer_scripts):
        control_tar = self.open_tar_file(self.control_archive_path)

        for script_name, script_path in maintainer_scripts.items():
            control_tar.add(script_path, arcname=f'./{script_name}', filter=self.filter_maintainer_script_tar_info)

        control_tar.add(self.control, arcname='./control', filter=self.filter_control_tar_info)

        control_tar.close()

    def assemble_deb_archive(self, control_archive_path, data_archive_path):
        if not self.output_directory.parent.exists():
            self.output_directory.parent.mkdir()

        with open(self.output_directory, 'wb') as ar_fp:
            ar_writer = ARWriter(ar_fp)

            ar_writer.archive_text("debian-binary", f"{DEBIAN_BINARY_VERSION}\n", int(time.time()), 0, 0,
                                   AR_DEFAULT_MODE)
            ar_writer.archive_file(control_archive_path, int(time.time()), 0, 0, AR_DEFAULT_MODE)
            ar_writer.archive_file(data_archive_path, int(time.time()), 0, 0, AR_DEFAULT_MODE)

    def build_package(self):
        with tempfile.TemporaryDirectory() as tmpfolder:
            self.working_dir = Path(tmpfolder)
            self.build_data_archive()
            self.build_control_archive(self.maintainer_scripts)
            self.assemble_deb_archive(self.control_archive_path, self.data_archive_path)
