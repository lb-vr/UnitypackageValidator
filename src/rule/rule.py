import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any
import tarfile
import logging
import json


class Rule:
    __logger = logging.getLogger('Rule')

    def __init__(self):
        self.author: str = 'No name'
        self.packages_fpath: List[str] = []

    def createRule(self, dst: str) -> bool:
        if not dst:
            Rule.__logger.fatal('Output filepath is empty.')
            return False

        jdict: Dict[str, Any] = {
            'created': {
                'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                'author': self.author
            },
            'common_packages': []
        }

        cwd = os.getcwd()
        for fpath in self.packages_fpath:
            Rule.__logger.debug('Package = %s', fpath)
            upack: Dict[str, Any] = {'name': os.path.basename(fpath), 'assets': []}
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                Rule.__logger.debug(' - Working dir = %s', tmpdir)
                # open tar
                with tarfile.open(fpath, 'r:gz') as tar:
                    Rule.__logger.debug(' - %d file(s) are included.', len(tar.getnames()))

                    # extract tar
                    def is_within_directory(directory, target):
                        
                        abs_directory = os.path.abspath(directory)
                        abs_target = os.path.abspath(target)
                    
                        prefix = os.path.commonprefix([abs_directory, abs_target])
                        
                        return prefix == abs_directory
                    
                    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                    
                        for member in tar.getmembers():
                            member_path = os.path.join(path, member.name)
                            if not is_within_directory(path, member_path):
                                raise Exception("Attempted Path Traversal in Tar File")
                    
                        tar.extractall(path, members, numeric_owner=numeric_owner) 
                        
                    
                    safe_extract(tar)
                    folders = os.listdir()
                    for f in folders:
                        path = ''
                        with open(os.path.join(f, 'pathname')) as fp:
                            path = fp.read()
                        upack['assets'].append({'guid': f, 'path': path})
                os.chdir(cwd)
            jdict['common_packages'].append(upack)
        with open(os.path.join(os.getcwd(), dst), mode='w', encoding='utf-8') as fjson:
            json.dump(jdict, fjson, indent=4)
        return True


def batch_main(args):
    rule = Rule()
    rule.author = args.author
    rule.packages_fpath = map(lambda x: os.path.join(os.getcwd(), x), args.packages)
    rule.createRule(args.output)
