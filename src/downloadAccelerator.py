import sys
import requests
import threading
import time

class file:
	def __init__(self,length):
		self.sem = threading.Semaphore()
		#self.threads = threads
		self.stringOut = 'x' * length
		#self.dictionary = dict.fromkeys(x for x in range(threads))

	def add(self, content, Start):
		self.sem.acquire()
		self.stringOut = self.stringOut[:Start] + content + self.stringOut[Start+len(content):]
		self.sem.release()
	def write(self,filename):
		f = open(filename,'w')
	#	for x in self.dictionary.keys():
	#		f.write(self.dictionary[x])
		f.write(self.stringOut)
		f.close()	

class downloader:
	def __init__(self):
		self.args = None

	def extractFilename(self, url):
		if url[len(url)-1] == '/':
			return "index.html"
		tmp = url.split('/')
		return tmp[len(tmp)-1]

	def download(self,url,tcount):
		filename = self.extractFilename(url)

		h = requests.head(url,headers={'Accept-Encoding': 'identity'})
		if 'content-length' not in h.headers:
			length = -1
			tcount = 1
		else:
			length = int(h.headers['content-length'])
		#print "File Length: " + str(length)
		bytelen = length/tcount
		#print "ByteLen: " + str(bytelen)
		startbyte = 0
		threads = []
		f = file(length)
		for x in range(tcount):
			
			if x == tcount-1:
				bytelen = length
			d = downloadthread(url,startbyte,bytelen,f)
			threads.append(d)
			startbyte += (bytelen)
			length -= bytelen


		start = time.time()
		for t in threads:
			t.start()
		for t in threads:
			t.join()

		f.write(filename)
		end = time.time()	
		
		print url + " " + str(tcount) + " " + h.headers['content-length'] + " " + str(end-start)

class downloadthread(threading.Thread):
	def __init__(self,url,startbyte,bytelen,shared):
		#print str(startbyte) + ", " + str(bytelen)
		self.shared = shared
		self.url = url
		self.startbyte = startbyte
		threading.Thread.__init__(self)
		self._content_consumed = False
		self.requeststr = 'bytes='+str(startbyte)+'-'+str(startbyte+bytelen-1)



	def run(self):
		#print "Requeststr: " + requeststr
		r = requests.get(self.url,stream = True,headers={'Accept-Encoding': 'identity','Range': self.requeststr})
		self.shared.add(r.content,self.startbyte)


def printUsage():
	print "Usage: [-n threads] [url]" 

if len(sys.argv) != 4:
	printUsage()
	sys.exit()

try:
	threads = int(sys.argv[2])
	url = sys.argv[3]
except ValueError:
	printUsage()
	sys.exit()


d = downloader()
d.download(url, threads)
