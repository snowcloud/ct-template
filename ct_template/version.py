
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
    

def gitAdd(fileName, repoDir):
    cmd = 'git add ' + fileName
    pipe = subprocess.Popen(cmd, shell=True, cwd=repoDir)
    pipe.wait()
    return

def gitRm(fileName, repoDir):
    cmd = 'git rm ' + fileName
    pipe = subprocess.Popen(cmd, shell=True, cwd=repoDir)
    pipe.wait()
    return

def gitMv(fileName, repoDir):
    cmd = 'git mv ' + fileName
    pipe = subprocess.Popen(cmd, shell=True, cwd=repoDir)
    pipe.wait()
    return

def gitCommit(fileName, repoDir, m='auto commit'):
    cmd = 'git commit -m "%s" %s' % (m, fileName)
    pipe = subprocess.Popen(cmd, shell=True, cwd=repoDir)
    pipe.wait()
    return

def gitPush(repoDir):
    cmd = 'git push'
    pipe = subprocess.Popen(cmd, shell=True, cwd=repoDir)
    pipe.wait()
    return

def commit_versions(version_path):
    """docstring for commit_versions"""
    
    # version_path = '/Users/derek/dev_django/ct_repo/dcm/'    
    gitAdd('*.xml', version_path)
    gitCommit('', version_path)
    files = filter(os.path.isfile, glob.glob(version_path + "*.xml.???"))
    print version_path + "*.xml.???"
    print files
    files.sort(key=lambda x: os.path.getmtime(x))
    print files
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

    commit_versions(settings.CT_VERSIONS)
    print '======\ncommitted any changed versions'

