
from django.conf import settings

import codecs
import glob
import os
import subprocess


def inc(i, limit=999):
    if i < limit:
        return i + 1
    else:
        raise Exception('inc has reached its limit: %d + 1 >= %d' % (i, limit))

def get_next_filename(fn, limit=999, format='%s.%03d'):
    """tests if filename n exists, if so adds/increments .nnn on end until limit.
        returns filename, using format: '%s %d' % (fn, inc)
    """
    i = 0
    n = fn
    while os.path.exists(n):
        i = inc(i, limit)
        n = format % (fn, i)
        # print n
    return n
    
def save_version(fn, txt, encoding='UTF-8'):
    """docstring for save_version"""
    
    outfile = codecs.open(get_next_filename(fn), 'wt', encoding=encoding)
    try:
        outfile.write(txt)
    finally:
        outfile.close()
    
def _git(params, repoDir):
    cmd = 'git %s' % params
    pipe = subprocess.Popen(cmd, shell=True, cwd=repoDir)
    pipe.wait()

def gitAdd(fileName, repoDir):
    return _git('add %s' % fileName, repoDir)
    
def gitRm(fileName, repoDir):
    return _git('rm %s' % fileName, repoDir)

def gitMv(fileName, repoDir):
    return _git('mv %s' % fileName, repoDir)

def gitCommit(fileName, repoDir, m='auto commit'):
    return _git('commit -m "%s" %s' % (m, fileName), repoDir)

def gitPull(repoDir):
    return _git('pull', repoDir)

def gitPush(repoDir):
    return _git('push', repoDir)

def commit_versions(version_path):
    """docstring for commit_versions"""
    
    # version_path = '/Users/derek/dev_django/ct_repo/dcm/' 
    gitPull(version_path)   
    gitAdd('*.xml', version_path)
    gitCommit('', version_path)
    files = filter(os.path.isfile, glob.glob(version_path + "*.xml.???"))
    files.sort(key=lambda x: os.path.getmtime(x))
    for f in files:
        xml = f[:-4]
        # rename will silently delete target if it exists
        os.rename(f, xml)
        gitAdd(os.path.split(xml)[1], version_path)
        gitCommit('', version_path)
    gitPush(version_path)

if __name__ == '__main__':
    
    from django.core.management import setup_environ
    
    import sys
    
    sys.path.append('../')
    sys.path.append('../shared_apps')
    # sys.path.append('../r4c')
    # print sys.path
    
    from r4c import settings
    setup_environ(settings)

    # from ct_template.models import ClinTemplate
    # ct = ClinTemplate.objects.get(id=1)
    # ct.save()

    commit_versions(settings.CT_VERSION_PATH)
    print '======\ncommitted any changed versions'

