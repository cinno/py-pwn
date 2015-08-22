import optparse
import socket
import time
import re
from socket import *
from threading import *
from multiprocessing import Process
from gevent.pool import Pool
import gevent
import datetime


DEF_PORT_LIST = [
    1,5,7,18,20,21,22,23,25,29,37,42,43,49,53,69,70,79,80,103,108,109,110,115,118,119,137,139,143,150,156,161,9090,
    179,190,194,197,389,396,443,444,445,458,546,547,563,569,1080,201,4380,4370,17603,17600,49588,15292,6263,6258,8080,
    8081,9091,9000, 9999, 9998, 9997, 138, 873, 3260, 6281, 5000, 5001, 995, 3005, 5353, 8324, 32469
] + list(range(6890, 6999))

def connScan(tgtHost, tgtPort, quiet):
    portReport = ''
    try:
        connSkt = socket(AF_INET, SOCK_STREAM)
        connSkt.connect((tgtHost, tgtPort))
        connSkt.send('jsdfijidsjfoi\r\n')
        results = connSkt.recv(512)
        portReport += '\n     [+]%d/tcp open' % tgtPort
        if (results == None):
            portReport += '\n        No Response'
        else:
            portReport += '\n        [Port %d Response]' % tgtPort
            portReport += '\n        ' + str(results).replace('\n', '\n        ')
    except:
        if (quiet == False):
            portReport += '\n     [-]%d/tcp closed' % tgtPort
    finally:
        connSkt.close()
        return portReport

def reportResults(workerReports, jobReport, timeDelta, numPortsScanned):
    if (workerReports == ''):
        # print jobReport.replace('&TIME', '%d days %d hours %d minutes %d seconds' % prntime(timeDelta))
        return
    else:
        print '------------------------------------------------------------------'
        print jobReport.replace('&TIME', '%d days %d hours %d minutes %d seconds' % prntime(timeDelta)).replace('&PORT_NUM', numPortsScanned )
        print workerReports
        print '------------------------------------------------------------------'

def prntime(ms):
    s = ms/1000
    m, s = divmod(s,60)
    h, m = divmod(m,60)
    d, h = divmod(h,24)
    return (d,h,m,s)

def portScan(tgtHost, tgtPorts, quiet):
    startTime = time.time()
    jobReport = ''
    try:
        tgtIP = gethostbyname(tgtHost)
    except:
        jobReport += "[-] Cannot resolve '%s' Unknown host" % tgtHost
        return
    try:
        tgtName = gethostbyaddr(tgtIP)
        jobReport += '[+] Scan Results for: ' + tgtName[0]
    except:
        jobReport += '[+] Scan Results for: ' + tgtIP
    finally:
        jobReport += '\n    Scanned &PORT_NUM ports in &TIME'
    setdefaulttimeout(1)
    p = Pool()
    workers = []
    numPortsScanned = 0;
    for tgtPort in tgtPorts:
        workers.append(p.apply_async(connScan, args=((tgtHost, int(tgtPort), quiet))))
        numPortsScanned += 1
    p.join() # wait for pool to complete
    reportResults('\n'.join([x.value for x in workers if ((x.value != '') & (x.value != None))]), \
        jobReport, int((time.time() - startTime) * 1000), str(numPortsScanned))


def main():
    parser = optparse.OptionParser('usage %prog -H' + '<target host> -p <target port>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-q', dest='quiet', action='store_true', help='specify quiet mode, will not show closed ports')
    parser.add_option('-p', dest='tgtPort', type='string', help='specify target ports', \
        default=','.join("{0}".format(n) for n in DEF_PORT_LIST))
    (options, args) = parser.parse_args()
    tgtHost = options.tgtHost
    tgtPorts = str(options.tgtPort).split(',')
    quietMode = options.quiet

    if (tgtHost == None ):
        print parser.usagef
        exit(0)

    if (tgtPorts[0] == 'tcp'):
        tgtPorts = (x for x in range(1, 65536))
    else:
        if not ((re.search('\\d+[-]\\d+',tgtPorts[0]))):
           return
        (min, max) = tgtPorts[0].split('-')
        tgtPorts = (x for x in range(int(min), int(max) + 1))


    startTime = time.time()
    p = Pool()
    if (tgtHost.find('.x') != -1):
        for lastOctet in range(1, 255):
            curIp = tgtHost.replace('x', str(lastOctet))
            p = p.apply_async(portScan, args=(curIp, tgtPorts, quietMode))
    else:
        p = p.apply_async(portScan, args=(tgtHost, tgtPorts, quietMode))
    p.join()
    timeDelta = int((time.time() - startTime)*1000)
    print '-----------------------------------------------------------------------------------'
    print 'Total Time To Run ' + '%d days %d hours %d minutes %d seconds' % prntime(timeDelta)
    print '-----------------------------------------------------------------------------------'



if __name__ == '__main__':
    main()

