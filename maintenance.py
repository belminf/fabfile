from __future__ import with_statement
from fabric.api import *
#from fabric.operations import *

def read_hosts():
    import sys
    env.hosts = [ h.strip() for h in sys.stdin.readlines() if h.strip() and not h.strip().startswith(('#','/')) ]

def get_hash(user=env.user):
    with hide('everything'):
        print(sudo('grep {user} /etc/shadow | cut -d\':\' -f 2'.format(**locals())))

def up():
    with settings(warn_only=True, abort_on_prompts=True):
        try:
            run('uptime')
        except:
            pass

@parallel
def uptime():
        run('uptime')

@parallel
def reboot_servers():
    reboot()

def restart_puppet():
    sudo('service puppet restart')
    #sudo('service puppet restart && tail -f /var/log/messages | { sed "/Finished catalog/ q" && kill $$ ;} | grep puppet-agent')

def clean_puppet():
    dns_domain = local('hostname -d', capture=True).strip()
    fqdn = '.' in env.host and env.host or '{host}.{dns_domain}'.format(host=env.host, dns_domain=dns_domain)
    sudo('rpm --import http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL')
    sudo('rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm || true')
    sudo('yum install -y -q puppet')
    local('sudo puppet cert clean {fqdn} || true'.format(**locals()))
    sudo('/usr/sbin/ntpd -q -g')
    sudo('/sbin/service puppet stop')
    sudo('rm -rf /var/lib/puppet/ssl')
    sudo('puppet agent -t --report --pluginsync || true')
    local('sudo puppet cert --sign {fqdn} --allow-dns-alt-names'.format(**locals()))
    sudo('/sbin/service puppet start')


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
    
def yum_update(packages):
    sudo('yum update -y -q {packages}'.format(**locals()))
