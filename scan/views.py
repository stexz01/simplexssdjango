from django.shortcuts import render,HttpResponse,redirect

from os import remove
import requests,threading,queue,time,sys,re,random
from bs4 import BeautifulSoup
from art import *
import urllib.parse

Parameters,doneParameters,found,total,foundcount = [],[],[],0,0

def param_extracter(domain):
    global Parameters,doneParameters,total
    Parameters.clear()
    doneParameters.clear()
    total=0
    blacklist = ['.png', '.jpg', '.jpeg', '.mp3', '.mp4', '.avi', '.gif', '.svg','.pdf','.js','.css']

    url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=txt&fl=original&collapse=urlkey&page=/"
    response = requests.get(url)

    ''' 
    Function to extract URLs with parameters (ignoring the black list extention)
    regexp : r'.*?:\/\/.*\?.*\=[^$]'
    
    '''

    parsed = list(set(re.findall(r'.*?:\/\/.*\?.*\=[^$]' , response.text)))
    final_uris = []
        
    for i in parsed:
        delim = i.find('=')
        final_uris.append((i[:delim+1]))

    blacklisted_url = []
    dublicates = []
    if final_uris != []:
        for x in final_uris:
            for b in blacklist:
                if b in x:
                    blacklisted_url.append(x)
            if x not in blacklisted_url:
                if x not in Parameters:
                    dublicates.append(x)
        for x in dublicates:
            hash0x = re.findall('0x[0-9]+',x)
            if not hash0x:
                if 'api' not in x:
                    if x not in Parameters:
                        if x not in doneParameters:
                            Parameters.append(x)
                            doneParameters.append(x)
                            total += 1

def index(request):
    if request.POST.get('search'):
        if len(request.POST.get('search')) > 3 and '.' in request.POST.get('search'):
            try:
                domain = re.findall(r'https?://([a-z.-]+)', request.POST.get('search'))[0]
            except:
                domain = request.POST.get('search')
            param_extracter(domain)
            context = {
                "params":Parameters,
                "totalcount":total,
                "totalreq":total*2,
            }
            return render(request, 'home.html', context)
        else:
            return render(request, 'home.html')
    else:
        return render(request, 'home.html')


def noobscan(target):
    global found,foundcount
    found.clear()
    foundcount = 0

    xss_payloads = ['%3Ch1%3Exxxxx%3C%2Fh1%3E%0A']

    domain = re.findall(r'https?://([a-z.-]+)', target)
    if domain:
        try:
            for payload in xss_payloads:
                response = requests.get(target+payload,timeout=3)
                if urllib.parse.unquote(payload).strip() in response.text:
                    if target+payload not in found:
                        found.append(target+payload)
                        foundcount += 1
        except:
            None


def result(request):
    if Parameters != []:
        scannerqueue = queue.Queue()
        for param in Parameters:
            scannerqueue.put(param)

        def QueueScanning():
            while not scannerqueue.empty():
                parameter = scannerqueue.get()
                noobscan(parameter)

        threads2 = []
        for _ in range(20):
            t = threading.Thread(target=QueueScanning)
            t.start()
            threads2.append(t)
        for thread in threads2:
            thread.join()

        context = {
            "founds":found,
            "foundcount":foundcount,
        }
        return render(request, 'result.html', context)
    else:
        return redirect('/')
