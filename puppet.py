from fabric.api import *
from fabric.utils import *

DNS_DOMAIN = local('hostname -d', capture=True).strip()

# Restart puppet
def puppet_run():
    sudo('service puppet stop; puppet agent --onetime --no-daemonize; service puppet start')
    #sudo('service puppet restart && tail -f /var/log/messages | { sed "/Finished catalog/ q" && kill $$ ;} | grep puppet-agent')

# (Re-)install puppet, must be run on puppet server
def puppet_install(fqdn=None, force_pluginsync=True):

    # if we have puppet, stop it
    sudo('/sbin/service puppet stop || true')

    # get DNS domain to make FQDN
    if not fqdn:
        fqdn = '.' in env.host and env.host or '{host}.{dns_domain}'.format(host=env.host, dns_domain=DNS_DOMAIN)

    # get RHEL version
    with settings(warn_only=True):
        if run('grep "release 5" /etc/redhat-release'):
            epel_repo = 'http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm'
        elif run ('grep "release 6" /etc/redhat-release'):
            epel_repo = 'http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm'
        else:
            error('Not a supported RHEL-based OS')
            return

    # install EPEL 
    sudo('rpm --import http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL')
    sudo('rpm -Uvh {0} || true'.format(epel_repo))

    # install puppet
    sudo('yum install -y -q puppet')

    # clean certificate locally
    local('sudo puppet cert clean {fqdn} || true'.format(**locals()))

    # make sure time is synchronized
    sudo('/usr/sbin/ntpd -q -g')

    # remove old certificates and re-run puppet to create new cert
    sudo('rm -rf /var/lib/puppet/ssl')
    sudo('puppet agent -t --report --pluginsync || true')

    # plugin sync force
    if force_pluginsync:
        sudo("grep 'pluginsync = true' /etc/puppet/puppet.conf || sed -i'' 's/.*pluginsync.*//' /etc/puppet/puppet.conf; sed -i'' 's/\[main\]/\[main\]\\n    pluginsync = true/' /etc/puppet/puppet.conf")

    # sign certificate on server
    local('sudo puppet cert --sign {fqdn} --allow-dns-alt-names'.format(**locals()))

    # finally, re-start puppet
    sudo('/sbin/service puppet start')
