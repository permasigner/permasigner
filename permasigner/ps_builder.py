import tarfile
import unix_ar
from .constrictor.control import BinaryControl
from .constrictor.dpkg import DPKGBuilder


class Control:
    def __init__(self, package, version, min_ios, name, author, executable):
        self.package = package
        self.version = version
        self.section = "Applications"
        self.arch = "iphoneos-arm"
        self.min_ios = min_ios
        self.depends = f"firmware (>={self.min_ios})"
        self.name = name
        self.description = f"{self.name} resigned with Linus Henze's CoreTrust bypass so it doesn't expire, and will persist in stock."
        self.author = author
        self.maintainer = self.author
        self.tags = f"compatible_min::ios{self.min_ios}"
        self.depiction = f"https://permasigner-depictions.itsnebula.net/depiction?name={self.name}"
        self.executable = executable


class Deb(object):
    def __init__(self, source, output, args):
        self.source = source
        self.output = output
        self.args = args

    def build(self, postinst, prerm, control):
        dirs = [
            {
                'source': self.source,
                'destination': '/Applications',
                'executable': control.executable

            }
        ]

        scripts = {
            'postinst': postinst,
            'prerm': prerm
        }

        ctrl = BinaryControl()
        ctrl.set_control_fields({'Name': control.name,
                                 'Package': control.package,
                                 'Version': control.version,
                                 'Architecture': control.arch,
                                 'Maintainer': control.maintainer,
                                 'Description': control.description,
                                 'Author': control.author,
                                 'Section': control.section,
                                 'Depends': control.depends,
                                 'Tags': control.tags,
                                 'Depiction': control.depiction
                                 })
        d = DPKGBuilder(self.output, ctrl, dirs, scripts)
        return d.build_package()

    def extract(self):
        ar_file = unix_ar.open(self.source)
        try:
            try:
                tarball = ar_file.open('data.tar.xz')
            except KeyError:
                tarball = ar_file.open('data.tar.gz')
        except KeyError:
            tarball = ar_file.open('data.tar.bz2')
        with tarfile.open(fileobj=tarball) as data:
            data.extractall(path=self.output)
        ar_file.close()
