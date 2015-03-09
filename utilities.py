from fabric.api import *
import sys

def read_hosts():
    env.hosts = [ h.strip().split(' ')[0] for h in sys.stdin.readlines() if h.strip() and not h.strip().startswith(('#','/')) ]

def sudo_cmd(command):
    sudo(command)

def sudo_check(user):
    sudo('sudo -l -U {user}'.format(**locals()))
