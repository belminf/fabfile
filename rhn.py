from fabric.api import *

def rhn_check():
    if run('ls /etc/sysconfig/rhn/systemid', quiet=True).return_code != 0:
        puts('Not registered')
