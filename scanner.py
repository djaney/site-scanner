#!/usr/bin/env python
 
import csv
import sys
import urllib2
import time
import socket
import threading
import os
 
class scanner:
 
 
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
 
    url = ''
    ttfb = -1.0
    scanned = False
    scanning = False
    status = '--'
    code = -1
    def __init__(self,url):
        self.url = url
        
 
 
    def scan(self):
        self.scanning = True
        tstart = time.time()
 
        try:
            self.handle = urllib2.urlopen(self.url)
        except urllib2.URLError as e:
            self.code = 0
            self.ttfb = 0
            self.status = str(e.reason)
        except urllib2.HTTPError as e:
            self.code = 0
            self.ttfb = 0
            self.status = str(e.reason)
        except socket.timeout as e:
            self.code = 0
            self.ttfb = 0
            self.status = 'timeout'
        else:
            self.code = self.handle.getcode()
            self.ttfb = time.time() - tstart
            if self.code==200:
                self.status = 'ok'
            else:
                self.status = 'down'
        finally:
            self.scanned = True
            self.scanning = False
 
 
 
 
    @classmethod
    def mass_scan(cls,urls):
        scans = []
        for u in urls:
            scn = cls(u)
            scans.append(scn)
        print cls.mass_print(scans)
 
        done = False
        for s in scans:
            t = threading.Thread(target=s.scan)
            t.start()
        print cls.mass_print(scans)
 
        print "Start..."
 
 
        while not done:
            os.system('cls' if os.name == 'nt' else 'clear')
            site_count = 0.0
            failed_count = 0.0
            scanned_count = 0.0
 
            print cls.mass_print(scans)
 
            done = True
            for s in scans:
                if not s.scanned:
                    done = False
                else:
                    scanned_count+=1
                site_count+=1
                if s.scanned and not s.code==200:
                    failed_count+=1
 
            print "Progress: "+str(round(scanned_count/site_count*100.00,1)) + '%'
            print "Sites: "+str(site_count)
            print "Scanned: "+str(scanned_count)
            print "Down: "+str(failed_count)
            
            time.sleep(1)
        
        print "Done"
 
        return cls.mass_print(scans)
 
 
    @classmethod
    def mass_print(cls,arr):
        
        stream = ''
        num = 1
        for s in arr:
            if not s.scanned:
                url = s.url
                code = "---"
                status = "scanning..."
                timeout = "--"
            else:
                url = s.url
                code = str(s.code)
                status = s.status
 
                timeout = ''
                if s.ttfb>5 or s.ttfb<=0:
                    timeout +=cls.FAIL
                elif s.ttfb>3:
                    timeout +=cls.WARNING
                else:
                    timeout +=cls.OKGREEN
                timeout += str(round(s.ttfb,1))+"s"
 
                timeout +=cls.ENDC
 
            if not s.scanned:
                url = cls.WARNING+url+cls.ENDC
            elif s.code==200:
                url = cls.OKGREEN+url+cls.ENDC
            else:
                url = cls.FAIL+url+cls.ENDC
            
            stream += "| {:<4} | {:100} | {:^6} | {:20}\n\r".format(num,url[:100],code,status.upper())
            num+=1
 
 
        return stream
 
    
if __name__ =='__main__':
 
    urls = [];
    if not sys.stdin.isatty():
        for line in sys.stdin:
            urls.append('http://'+line.strip())
 
        out = scanner.mass_scan(urls)
 
 
        f = open('sites_status.log','w')
        f.write(out)
        f.close()
    elif len(sys.argv) > 1:
        filename = sys.argv[1]
        
        with open(filename, 'r') as csvfile:
            sites = csv.DictReader(csvfile)
            for row in sites:
                urls.append('http://'+row['Domain']) 
 
 
        out = scanner.mass_scan(urls)
 
        f = open('sites_status.log','w')
        f.write(out)
        f.close()
 
    else:
        print 'Input filename'