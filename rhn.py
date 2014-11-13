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

def rhn_register(key, server=None, server_path='/XMLRPC', force=True):
    server_param = server and ' --serverUrl https://{0}{1}'.format(server, server_path) or ''
    force_param = force and ' --force' or ''
    sudo('/usr/sbin/rhnreg_ks --activationkey {0}{1}{2}'.format(key, server_param, force_param))
