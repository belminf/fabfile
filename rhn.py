from fabric.api import *

def rhn_check():
    dns_domain = local('hostname -d', capture=True).strip()
    fqdn = '.' in env.host and env.host or '{host}.{dns_domain}'.format(host=env.host, dns_domain=dns_domain)
    puts(fqdn)
    results = sudo('grep {fqdn} /etc/sysconfig/rhn/systemid'.format(**locals()), quiet=True)
    if results.return_code == 1:
        puts('Registered as another hostname')
    elif results.return_code == 2:
        puts('Not registered')
