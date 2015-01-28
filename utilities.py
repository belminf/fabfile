from fabric.api import *
import sys

def read_hosts():
    env.hosts = [ h.strip() for h in sys.stdin.readlines() if h.strip() and not h.strip().startswith(('#','/')) ]

def sudo_su():
    sudo('su -')
