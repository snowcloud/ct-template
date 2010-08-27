
import codecs
import os


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
    
    

if __name__ == '__main__':
    
    from django.core.management import setup_environ
    
    import sys
    
    sys.path.append('../')
    sys.path.append('../shared_apps')
    # sys.path.append('../r4c')
    # print sys.path
    
    from r4c import settings
    
    setup_environ(settings)
    
    from ct_template.models import ClinTemplate
    
    ct = ClinTemplate.objects.get(id=1)
    fn = '%sdcm.xml' % settings.CT_VERSIONS
    save_version(fn, ct.xmlmodel)

    print '======\nyurp'

