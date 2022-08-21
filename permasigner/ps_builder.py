import tarfile
import unix_ar
from urllib.parse import urlparse
from .ps_utils import Utils
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
        self.name_encoded = urlparse(self.name).path
        self.depiction = f"https://permasigner-depictions.itsnebula.net/depiction?name={urlparse(self.name).path}"
        self.executable = executable


class Deb(object):
    def __init__(self, source, output, args):
        self.source = source
        self.output = output
        self.args = args
        self.utils = Utils(self.args)

    def build(self, postinst, postrm, control):
        dirs = [
            {
                'source': self.source,
                'destination': '/Applications',
                'executable': control.executable

            }
        ]

        scripts = {
            'postinst': postinst,
            'postrm': postrm
        }

        links = []

        c = BinaryControl(control.package, control.version, control.arch, control.maintainer, control.description)
        c.set_control_fields({'Name': control.name,
                              'Author': control.author,
                              'Section': control.section,
                              'Depends': control.depends,
                              'Tags': control.tags,
                              'Depiction': control.depiction
                              })
        output_name = control.name + '_' + control.version + '.deb'
        d = DPKGBuilder(self.output, c, dirs, links, scripts, output_name=output_name)
        d.build_package()
        return d.output_name

    def extract(self):
        ar_file = unix_ar.open(str(self.source[0]))
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
