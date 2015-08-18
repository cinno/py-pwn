import optparse
import socket
import re
import time
from socket import *
from threading import *
from itertools import islice


DEF_PORT_LIST = [
    1,5,7,18,20,21,22,23,25,29,37,42,43,49,53,69,70,79,80,
    103, 108,109,110, 115,118,119,137,139,143,150,156,161,
    179,190, 194,197,389,396,443,444,445,458,546,547,563,569,
    1080,201,4380,4370,17603,17600,49588,15292,6263,6258,8080,
    8081,9091,9090,
]


screenLock = Semaphore(value=1)
def connScan(tgtHost, tgtPort, quiet):
    try:
        connSkt = socket(AF_INET, SOCK_STREAM)
        connSkt.connect((tgtHost, tgtPort))
        connSkt.send('jsdfijidsjfoi\r\n')
        results = connSkt.recv(100)
        screenLock.acquire()
        print '     [+]%d/tcp open' % tgtPort
        if (results == None) | (results == ''):
            print '        No Response'
        else:
            print '        [Port %d Response]' % tgtPort
            print '        ' + str(results).replace('\n', '\n        ')
    except:
        screenLock.acquire()
        if (quiet == False):
            print '     [-]%d/tcp closed' % tgtPort
    finally:
        connSkt.close()
        screenLock.release()


def portScan(tgtHost, tgtPorts, quiet):
    try:
        tgtIP = gethostbyname(tgtHost)
    except:
        print "[-] Cannot resolve '%s' Unknown host" %tgtHost
        return
    try:
        tgtName = gethostbyaddr(tgtIP)
        print '\n[+] Scan Results for: ' + tgtName[0]
    except:
        print '\n[+] Scan Results for: ' + tgtIP
    setdefaulttimeout(1)
    for tgtPort in tgtPorts:
        t = Thread(target=connScan, args=(tgtHost, int(tgtPort), quiet), name='scan[%s:%s]' % (tgtHost, tgtPort))
        t.start();
        time.sleep (0.10);



def main():
    parser = optparse.OptionParser('usage %prog -H' + '<target host> -p <target port>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-q', action='store_true', dest='quiet', help='specify quiet mode, will not show closed ports')
    parser.add_option('-p', dest='tgtPort', type='string', help='specify target ports', default=','.join("{0}".format(n) for n in DEF_PORT_LIST))
    (options, args) = parser.parse_args()
    tgtHost = options.tgtHost
    tgtPorts = str(options.tgtPort).split(',')
    quietMode = options.quiet

    if (tgtHost == None ) | (tgtPorts[0] == None):
        print parser.usage
        exit(0)

    if (tgtHost.find('.x') != -1):
        for lastOctet in range(1, 255):
            curIp = tgtHost.replace('x', str(lastOctet))
            t1 = Thread(target=portScan, name='scan[%s]' % curIp, args=(curIp, tgtPorts, quietMode))
            t1.start()
            time.sleep (0.25);
    else:
        portScan(tgtHost, tgtPorts, quietMode)


if __name__ == '__main__':
    main()

