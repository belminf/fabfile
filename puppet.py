from fabric.api import *
from fabric.utils import *

DNS_DOMAIN = local('hostname -d', capture=True).strip()

# Restart puppet
def puppet_restart():
    sudo('service puppet restart')
    #sudo('service puppet restart && tail -f /var/log/messages | { sed "/Finished catalog/ q" && kill $$ ;} | grep puppet-agent')

# (Re-)install puppet, must be run on puppet server
def puppet_install():

    # get DNS domain to make FQDN
    fqdn = '.' in env.host and env.host or '{host}.{dns_domain}'.format(host=env.host, dns_domain=DNS_DOMAIN)

    # get RHEL version
    try:
        if run('grep "release 5" /etc/redhat-release'):
            epel_repo = 'http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm'
        elif run ('grep "release 6" /etc/redhat-release'):
            epel_repo = 'http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm'
        else:
            error('Not a supported RHEL-based OS')
            return
    except:
        error('Not a RHEL-based OS')
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

    # stop puppet service if running
    sudo('/sbin/service puppet stop')

    # remove old certificates and re-run puppet to create new cert
    sudo('rm -rf /var/lib/puppet/ssl')
    sudo('puppet agent -t --report --pluginsync || true')

    # sign certificate on server
    local('sudo puppet cert --sign {fqdn} --allow-dns-alt-names'.format(**locals()))

    # finally, re-start puppet
    sudo('/sbin/service puppet start')