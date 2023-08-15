#!/usr/bin/env python
import os
import time
import subprocess as sp
from prometheus_client import start_http_server, Gauge

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
        self.collect()
    def collect(self):
        try:
            numvolumesmetric.labels(self.path,self.filename,self.created,self.last_modified).set(self.num_volumes)
            compressedmetric.labels(self.path,self.filename,self.created,self.last_modified).set(self.metadata_size['compressed'])
            uncompressedmetric.labels(self.path,self.filename,self.created,self.last_modified).set(self.metadata_size['uncompressed'])
        except:
            print(self.__dict__)
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

class ArchiveSize:
    def __init__(self,path,projectname):
        self.path = path
        self.project = projectname
        self.size = self.get_archive_size()
    def collect(self):
        sizemetric.labels(self.path,self.project).set(self.size)
    def get_archive_size(self):
        size = 0
        for r,d,f in os.walk(self.path):
            for file in f:
                try:
                    size+=os.stat(os.path.join(r,file)).st_size
                except OSError:
                    pass
        return size
 
class ArchInfo:
    def __init__(self):
        self.ARCHINFO_PATH = os.environ.get('ARCHINFO_PATH', '/opt/Autodesk/io/bin/ArchInfo')
        self.ARCHIVE_PATH = os.environ.get('ARCHIVE_PATH', '/mnt/flame_archive')
        self.job_dirs = []
        self.header_files = self.get_headers()
        self.headers = [self.get_header_info(x) for x in self.header_files]
        self.archive_sizes = [ArchiveSize(os.path.join(self.ARCHIVE_PATH,x),x) for x in self.job_dirs]
    def get_headers(self):
        archive_headers = []
        exclude_paths = ['Central_OTOC']
        job_dirs = [x for x in os.listdir(self.ARCHIVE_PATH) if x not in exclude_paths]
        setattr(self,"job_dirs",job_dirs)
        for job_dir in job_dirs:
            print(job_dir)
            for r,d,f in os.walk(os.path.join(self.ARCHIVE_PATH,job_dir)):
                if len(d) == 0:
                    for _f in f:
                        if '.' not in _f:
                            if _f.endswith('-lock'):
                                print(f"rm -fv {os.path.join(r,_f)}")
                                os.remove(os.path.join(r,_f))
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

# arch_info = ArchInfo()
# data = [{'path':x.path,'size':x.metadata_size['uncompressed']} for x in arch_info.headers]
# for item in sorted(data, key=lambda x: (len(x['size']),x['size']),reverse=True):
# 	print(item)
numvolumesmetric = Gauge('flame_archive_num_volumes', 'Flame Archive Header Sized Before Compression',labelnames=['path','filename','created','last_modified'])
compressedmetric = Gauge('flame_archive_header_size_compressed', 'Flame Archive Header Sized Before Compression',labelnames=['path','filename','created','last_modified'])
uncompressedmetric = Gauge('flame_archive_header_size_uncompressed', 'Flame Archive Header Size Before Compression',labelnames=['path','filename','created','last_modified'])
sizemetric = Gauge('carbon_flame_archives', 'Flame Archive Size On Disk',labelnames=['path','projectname'])
start_http_server(int(os.environ.get('EXPORTER_PORT',9100)))
while True:
    arch_info = ArchInfo()
    time.sleep(30)