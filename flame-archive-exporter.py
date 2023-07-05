#!/usr/bin/env python
import os
import subprocess as sp

class Info:
    def __init__(self,header_info,header_path):
        self.path = header_path
        self.filename = ""
        self.version = ""
        self.features = ""
        self.format = ""
        self.metadata_size = {}
        self.description = ""
        self.comments = ""
        self.created = ""
        self.last_modified = ""
        self.block_size = ""
        self.num_volumes = ""
        self.parse_header_info(header_info)
    def parse_header_info(self,header_info):
        """
        stripped DL database info:

        'DL Database: "ups_proudlyunstoppablernd2_235608_AUTO_ARCHIVE"\n\tVersion:\t2023.3 (0x2530)\n\tFeatures:\tCOMPRESSED_METADATA, AUDIO_DATA_422\n\tFormat:\t\t0xa000\n\tMetadata Size:\t65561438 (Compressed: 8153830)\n\tDescription:\t\n\tComments:\t\n\tCreated:\tTue Mar  7 20:35:54 2023\n\tLast modified:\tWed Mar 22 17:36:11 2023\n\tBlock size:\t1\n\t# of volumes:\t92'
        """
        for _line in header_info.split('\n'):
            line = _line.strip().split(':')
            if line[0] ==  "DL Database":
                self.filename = line[-1].strip().replace('"','')
            elif line[0] == "Version":
                self.version= line[-1].strip()
            elif line[0] == "Features":
                self.features = line[-1].strip().split(',')
            elif line[0] == "Format":
                self.format = line[-1].strip()
            elif line[0] == "Metadata Size":
                self.metadata_size = {
                    'compressed':line[1].strip().split()[0],
                    'uncompressed':line[-1].strip().replace(')','').replace('(','')
                }
            elif line[0] == "Description":
                self.description = line[-1].strip()
            elif line[0] == "Comments":
                self.comments = line[-1].strip()
            elif line[0] == "Created":
                self.created = ':'.join(line[1:]).strip()
            elif line[0] == "Last modified":
                self.last_modified = ':'.join(line[1:]).strip()
            elif line[0] == "Block size":
                self.block_size = line[-1].strip()
            elif line[0] == "# of volumes":
                self.num_volumes = line[-1].strip()

class ArchInfo:
    def __init__(self):
        self.ARCHINFO_PATH = os.environ.get('ARCHINFO_PATH', '/opt/Autodesk/io/bin/ArchInfo')
        self.ARCHIVE_PATH = os.environ.get('ARCHIVE_PATH', '/mnt/flame_archive')
        self.header_files = self.get_headers()
        self.headers = [self.get_header_info(x) for x in self.header_files]
    def get_headers(self):
        archive_headers = []
        for r,d,f in os.walk(self.ARCHIVE_PATH):
            if 'Central_OTOC' in r or "Central_OTOC" in d or "Central_OTOC" in f:
                continue
            if len(d) == 0:
                for _f in f:
                    if '.' not in _f:
                        if _f.endswith('-lock'):
                            print(f"rm -fv {os.path.join(r,_f)}")
                            # os.remove(os.path.join(r,_f))
                        else:
                            archive_headers.append(os.path.join(r,_f))
        return archive_headers
    def get_header_info(self,header_path):
        cmd = [self.ARCHINFO_PATH,header_path]
        runit = sp.Popen(cmd,stdout=sp.PIPE,stderr=sp.PIPE)
        out,err = runit.communicate()
        if err:
            print(err)
        return Info(out.decode().strip(),header_path)

arch_info = ArchInfo()
data = [{'path':x.path,'size':x.metadata_size['uncompressed']} for x in arch_info.headers]
for item in sorted(data, key=lambda x: (len(x['size']),x['size']),reverse=True):
	print(item)
