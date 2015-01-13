#!/usr/bin/env python
from scanner import scanner
import wx
import wx.grid
import threading
import paramiko
from exceptions import IOError

class GridFrame(wx.Frame):
    grid = None
    scanGrid = None
    menuBar = None
    scanMenu = None
    menuStartScan = None
    def __init__(self, parent):

        wx.Frame.__init__(self, parent)
        self.grid = wx.grid.Grid(self, -1)

        # Menu
        self.menuBar = wx.MenuBar()

        self.scanMenu = wx.Menu()
        self.menuBar.Append(self.scanMenu, '&Scan')
        
        self.menuStartScan = self.scanMenu.Append(-1, '&Start', 'Start Scanning')
        self.menuStopScan = self.scanMenu.Append(-1, 'S&top', 'stop Scanning')
        self.Bind(wx.EVT_MENU, self.onMenuStartScan,self.menuStartScan)
        self.Bind(wx.EVT_MENU, self.onMenuStopScan,self.menuStopScan)
        #status bar
        self.CreateStatusBar(style=0)
        self.SetStatusText("Ready")


        self.SetTitle('Site Checker')
        self.SetMenuBar(self.menuBar)
        self.Centre()

        


        self.scanGrid = ScannerGrid(self)


        self.Maximize(True)
        self.Show(True)



    def onMenuStartScan(self,event):
        self.scanGrid.startScan()
    def onMenuStopScan(self,event):
        self.scanGrid.stopScan()

class ScanThread(threading.Thread):
    callback = None
    scanner = None
    def __init__(self,scanner=None, callback=None):
        self.scanner = scanner
        self.callback = callback
        threading.Thread.__init__(self,target=self.scanner.scan)

    def run(self):
        threading.Thread.run(self)
        if self.callback!=None:
            self.callback(self.scanner)

class ScannerGrid:
    scans = []
    threads = []
    runningThreads = []
    frame = None
    total = 0
    done = 0
    scanning = False

    SCANS_AT_A_TIME = 3

    def __init__(self,frame,urls = []):
        self.frame = frame
        self.grid = frame.grid


        self.grid.CreateGrid(1,4)


        self.grid.SetColLabelValue(0,"URL")
        self.grid.SetColLabelValue(1,"HTTP")
        self.grid.SetColLabelValue(2,"Latency")
        self.grid.SetColLabelValue(3,"Status")

        self.grid.SetColSize(0,500)
        self.grid.SetColSize(3,500)

        self.grid.ClearGrid()
        self.readyScan()

    def getSites(self):

        output = ''
        try:
            sites = open("scanwin.csv", "r")
        except IOError, e:
            print "scanwin.csv not found"
        finally:
            return sites.readlines()

    def readyScan(self):
        urls = []
        sites = self.getSites()
        for s in sites:
            urls.append('http://'+s)
        
        self.grid.DeleteRows( 0, self.grid.GetNumberRows())
        self.grid.AppendRows(len(urls))

        self.scans = []
        for u in urls:
            scn = scanner(u)
            self.scans.append(scn)
        wx.CallAfter(self.renderRows)

    def startScan(self):
        self.scanning = True
        self.threads = []
        for s in self.scans:
            if not s.scanned:
                t = ScanThread(scanner=s,callback=self.onScanFinished)
                t.daemon = True
                self.threads.append(t)
        wx.CallAfter(self.renderRows)
        self.scanLoop()

    def stopScan(self):
        self.scanning = False

    def scanLoop(self):

        if len(self.threads)>0:

            while len(self.runningThreads)<self.SCANS_AT_A_TIME:
                thread = None
                if len(self.threads)>0:
                    thread = self.threads[0]
                    del self.threads[0]

                if thread!=None:
                    thread.start()
                    self.runningThreads.append(thread)
        else:
            self.scanning = False
        wx.CallAfter(self.renderRows)

    def onScanFinished(self,scanner):
        wx.CallAfter(self.renderRows)
        #remove finished thread
        for t in self.runningThreads:
            if t.scanner == scanner:
                self.runningThreads.remove(t)
                break

        if self.scanning:
            self.scanLoop()


    def renderRows(self):
        row = 0
        self.total = len(self.scans)
        self.done = 0
        for s in self.scans:
            if s.scanned:
                self.done+=1

            if not s.scanning and not s.scanned:
                code = ''
                status = ''
                ttfb = ''
            if s.scanning and not s.scanned:
                code = ''
                status = 'Scanning...'
                ttfb = ''
            else:
                if s.code>=0:
                    status = s.status
                    code = str(s.code)
                else:
                    status = ''
                    code = ''
                
                if s.ttfb>0:
                    ttfb = '{:0.1n}s'.format(s.ttfb)
                else:
                    ttfb = ''

            self.grid.SetCellValue(row, 0, s.url)
            self.grid.SetCellValue(row, 1, code)
            self.grid.SetCellValue(row, 2, ttfb)
            self.grid.SetCellValue(row, 3, status.upper())
            
            if s.code==200:
                self.grid.SetCellBackgroundColour(row, 0, wx.GREEN)
            elif s.code>=0:
                self.grid.SetCellBackgroundColour(row, 0, wx.RED)
            else:
                self.grid.SetCellBackgroundColour(row, 0, wx.WHITE)


            if s.ttfb>0 and s.ttfb>=3:
                self.grid.SetCellBackgroundColour(row, 2, wx.RED)
            else:
                self.grid.SetCellBackgroundColour(row, 2, wx.WHITE)



            row+=1
        if not self.scanning and len(self.runningThreads)==0:
            self.frame.SetStatusText('Ready')
        if not self.scanning and len(self.runningThreads)>0:
            self.frame.SetStatusText('Stopping...')
        elif self.total==0 and self.scanning:
            self.frame.SetStatusText('Scanning...')
        elif self.total==self.done:
            self.frame.SetStatusText('Done')
        else:
            self.frame.SetStatusText('Scanning %i of %i' % (self.done,self.total))





if __name__ == '__main__':

    app = wx.App(0)
    frame = GridFrame(None)



    app.MainLoop()