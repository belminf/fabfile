from __future__ import with_statement
from fabric.api import *
#from fabric.operations import *
from fabric.utils import *

DNS_DOMAIN = local('hostname -d', capture=True).strip()

def get_hash(user=env.user):
    with hide('everything'):
        print(sudo('grep {user} /etc/shadow | cut -d\':\' -f 2'.format(**locals())))

def up():
    with settings(warn_only=True, abort_on_prompts=True):
        try:
            run('uptime')
        except:
            pass

def uptime():
    try:
        run('uptime')
    except Exception, e:
        warn(e)

def reboot_servers():
    run('date')
    reboot()

def collect_file_archives(file_match, local_dir='.', remote_dir='~', archive_cmd='tar -cjf', archive_ext='tar.bz2', archive_prefix='', archive_dir='/tmp', archive_delete=True):
    host = env.host
    archive_file = '{archive_dir}/{archive_prefix}{host}.{archive_ext}'.format(**locals())
    with cd(remote_dir):
        sudo('{archive_cmd} {archive_file} {file_match}'.format(**locals()))
        get(archive_file, local_path=local_dir+'/')
        if archive_delete:
            sudo('rm {archive_file}'.format(**locals()))

def collect_file(remote_file, local_dir='.'):
    # TODO: slugify hostname
    import os.path
    host = env.host
    this_path = os.path.join(local_dir,env.host)
    local('mkdir {0} || true'.format(this_path))
    get(remote_file, local_path=this_path+'/')

def rpm_lookup(package):
    run('rpm -q --queryformat \'v%{{VERSION}} (Release: %{{RELEASE}}, Arch: %{{ARCH}})\n\' {0}'.format(package))
    
def yum_update(packages=None):
    if packages:
        sudo('yum update -y -q {packages}'.format(**locals()))
    else:
        sudo('yum update -y')

def yum_clean():
    sudo('yum clean all')

def up2date_update(packages):
    sudo('up2date -u {packages}'.format(**locals()))

def rpm_fixed(package, cve):
    sudo('rpm -q --changelog {package} | grep -q {cve} && echo fixed || echo VULNERABLE!'.format(**locals()))

def fix_hostname(fqdn=None, use_env=None):
    if use_env:
        this_host = env.host
    else:
        this_host = run('hostname')

    if not this_host:
        warn('Could not determine a hostname')
    else:
        if not fqdn:
            fqdn = '.' in this_host and this_host or '{host}.{dns_domain}'.format(host=this_host, dns_domain=DNS_DOMAIN)
        sudo('hostname {fqdn}'.format(**locals()))
        sudo('sed -i"" "s/HOSTNAME=.*/HOSTNAME={fqdn}/" /etc/sysconfig/network'.format(**locals()))
        sudo('/sbin/sysctl kernel.hostname={fqdn}'.format(**locals()))
        sudo('sed -i"" "/kernel.hostname \=/d" /etc/sysctl.conf')


def add_static_host(host, ip):
    with settings(warn_only=True):
        host_exists = run('egrep "{ip}[[:blank:]]+{host}$" /etc/hosts'.format(**locals()))
        if not host_exists:
            sudo('echo "{ip}\t{host}" | tee -a /etc/hosts 2> /dev/null'.format(**locals()))

def set_dns_search(domains):
    # Remove current search first
    sudo('sed -i"" "/search[[:blank:]]/d" /etc/resolv.conf')

    # Add search
    sudo('echo "search\t{domains}" | tee -a /etc/resolv.conf 2> /dev/null'.format(**locals()))
