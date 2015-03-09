from fabric.api import *

DNS_DOMAIN = local('hostname -d', capture=True).strip()

def rhn_check():
    fqdn = '.' in env.host and env.host or '{host}.{dns_domain}'.format(host=env.host, dns_domain=DNS_DOMAIN)
    puts(fqdn)
    results = sudo('grep {fqdn} /etc/sysconfig/rhn/systemid'.format(**locals()), quiet=True)
    if results.return_code == 1:
        puts('RHNCHECK: Registered as another hostname')
    elif results.return_code == 2:
        puts('RHNCHECK: Not registered')

def rhn_register(rhn_server, key=None, cert_version='1.0-1', server_path='/XMLRPC', force=True):
    try:
        sudo('rpm -Uvh http://{rhn_server}/pub/rhn-org-trusted-ssl-cert-{cert_version}.noarch.rpm || true'.format(**locals()))
    except:
        pass
    server_param = rhn_server and ' --serverUrl http://{0}{1}'.format(rhn_server, server_path) or ''
    force_param = force and ' --force' or ''
    key_param = key and ' --activationkey {0}'.format(key) or ''
    sudo('/usr/sbin/rhnreg_ks{0}{1}{2}'.format(key_param, server_param, force_param))
