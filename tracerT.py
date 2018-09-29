#!/usr/bin/env python

import sys, os, re
import ttargs
import requests, urllib
from bs4 import BeautifulSoup
from texttable import Texttable

__author__ = '@2xxeformyshirt'
__version__ = '2.0.0'

'''
--------------------------------
start GHDB functions
--------------------------------
'''
def writeoutdorks(dorks):
    '''Write dorks to a file'''
    err = False
    with open(args['outdork'],'w+') as f:
        f.write('GHDB ID,Dork\n')
        for dork in dorks:
            try:
                f.write(dork.encode('ascii','replace'))
                f.write('\n')
            except:
                err = True
                pass
    if err:
        print '[-] Error writing one or more dorks to file'
    print '[+] Dorks written to: '+args['outdork']

def extractdorks(soup):
    '''extracts all (full) dorks from page of dorks'''
    dorks = []
    table = soup.find('table',{'class':'sortable category-list'})
    for each in table.findAll('tr'):
        for a in each.findAll('a'):
            '''need to retrieve the full page for each table 
               entry b/c the table truncates the longer dorks'''
            dork,ghdbid = retrievedork(a.get('href'))
            dorks.append(ghdbid+','+dork)
    return dorks

def retrievedork(url):
    '''retrieve single dork from GHDB entry'''
    r = requests.get(url, headers=useragent, allow_redirects=True)
    soup = BeautifulSoup(r.content, 'lxml')
    dork = soup.findAll('a', attrs={'target':'_blank'})[0].contents[0].strip()
    ghdbid = url.split('/')[-2]
    return dork,ghdbid

def retrievedorklist(catid):
    '''given a category id, return a list of dorks'''
    print '[+] Pulling list of dorks from GHDB'
    url = 'https://www.exploit-db.com/google-hacking-database/%s/' % str(catid)
    r = requests.get(url, headers=useragent, allow_redirects=True)
    soup = BeautifulSoup(r.content, 'lxml')
    dorks = extractdorks(soup)
    pages = []
    '''get links for numbered pages'''
    for nums in soup.findAll('div', attrs={'class':['pagination', 'gd-pagination']}):
        for num in nums.find_all('a'):
            pages.append(num.get('href'))
    pages = set(pages)

    '''extract dorks for remaining pages'''
    print '[+] Retrieving full dorks'
    for page in pages:
        r = requests.get(page, headers=useragent, allow_redirects=True) 
        soup = BeautifulSoup(r.content, 'lxml')
        dorks.extend(extractdorks(soup))   
    return dorks

def printcategories():
    categories={'Footholds':1,
                'Files Containing Usernames':2,
                'Sensitive Directories':3,
                'Web Server Detection':4,
                'Vulnerable Files':5,
                'Vulnerable Servers':6,
                'Error Messages':7,
                'Files Containing Juicy Info':8,
                'Files Containing Passwords':9,
                'Sensitive Online Shopping Info':10,
                'Network or Vulnerability Data':11,
                'Pages Containing Login Portals':12,
                'Various Online Devices':13,
                'Advisories and Vulnerabilities':14
    }
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["l", "r"])
    table.add_row(['Category','Category ID'])
    for cat,key in categories.items():
        table.add_row([cat,key])
    print table.draw()+'\n'

'''
--------------------------------
end GHDB functions
--------------------------------

--------------------------------
start CSE functions
--------------------------------
'''
def readindorks(file, fformat):
    '''Read in list of dorks'''
    dorks = []
    if fformat == 'csv':
        with open(file,'r') as f:
            for line in f:
                dorks.append(line.split(',')[-1])
        '''delete csv column line'''
        dorks.pop(0)
    elif fformat == 'txt':
        with open(file,'r') as f:
            for line in f:
                dorks.append(line)
    return dorks

def querycse(dorks):
    '''query CSE using dorks + target scoping'''
    results = []
    for dork in dorks:
        dork = dork.replace('\n','')
        queryu = urlbase + urllib.quote_plus(dork)
        r = requests.get(queryu, headers=useragent, allow_redirects=True)
        
        if str(r.status_code)[:1] == '2':
            if int(rjson['queries']['request'][0]['totalResults']) > 0:
                numres = rjson['queries']['request'][0]['totalResults']
                results.append(dork+','+numres)  
        else:
            print '[-] Error querying dork: '+dork

    return results

def writeoutres(results):
    '''Write dorks to a file'''
    err = False
    with open(args['outres'],'w+') as f:
        f.write('Dork,NumResults\n')
        for res in results:
            try:
                f.write(res.encode('ascii','replace'))
                f.write('\n')
            except:
                err = True
                pass
    if err:
        print '[-] Error writing one or more results to file'
    print '[+] Results written to: '+args['outres']

'''
--------------------------------
end CSE functions
--------------------------------

--------------------------------
start TSV functions
--------------------------------
'''
def generatetsvfile(tlds,cxt):
    '''given input list of tlds, generate tsv in proper format'''
    tsv = 'URL\tLabel\tScore\n'
    for tld in tlds:
        tsv += '*.%s/*\t_cse_%s\t1.000000\n' % (tld,cxt)

    with open(args['outconf'], 'w+') as f:
        f.write(tsv)

    print '[+] Configuration written to: '+args['outconf']

'''
--------------------------------
end TSV functions
--------------------------------
'''

def tsv_main(args):
    '''Main function for GHDB operation'''

    '''basic arg checking'''
    if os.path.isfile(args['outconf']):
        print '[-] Output file already exists'
        os._exit(1)
    if ':' not in args['cseconf']:
        print '[-] Invalid CSE ID'
        os._exit(1)
    if len(args['itld']) < 2:
        print '[-] Invalid TLD input'
        os._exit(1)

    '''only second half of cse id is required for config'''
    cxt = (args['cseconf']).split(':')[-1]
    
    '''parse tld string'''
    tlds = []
    tsplit = (args['itld']).split(',')
    if len(tsplit) == 1:
        tlds.append(tsplit[0].strip())
    else:
        for tld in tsplit:
            tlds.append(tld.strip())

    print '[+] Generating configuration'
    generatetsvfile(tlds,cxt)   

def cse_main(args):
    '''Main function for CSE operation'''

    '''really basic arg checking'''
    if not os.path.isfile(args['ilist']):
        print '[-] Input file doesnt exist'
        os._exit(1)
    if '.' not in args['target']:
        print '[-] Invalid target domain'
        os._exit(1)
    if ':' not in args['cse']:
        print '[-] Invalid CSE ID'
        os._exit(1)
    if os.path.isfile(args['outres']):
        print '[-] Output file already exists'
        os._exit(1)
    print '[+] Reading in dorks'
    fformat = args['fformat']
    if fformat is None:
        fformat = args['ilist'].split('/')[-1]
    if fformat != 'csv' and fformat != 'txt':
        print '[-] Invalid input format. Accepted formats: txt, csv'
        os._exit(1)
    if args['skip'] is not True:
        with open(args['ilist'], 'r') as f:
            lc = f.read().count('\n')
            if fformat == 'csv':
                if lc > 101:
                    print '[-] Input file too long for free API tier'
                    os._exit(1)
            if fformat == 'txt':
                if lc > 100:
                    print '[-] Input file too long for free API tier'
                    os._exit(1)

    global urlbase
    urlbase = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&siteSearch=%s&num=10&q=' % (args['api'],args['cse'],args['target'])

    dorks = readindorks(args['ilist'],fformat) 
    print '[+] Querying custom search engine for dorks'
    results = querycse(dorks)
    print '[+] Writing results to disk'
    writeoutres(results)


def ghdb_main(args):
    '''Main function for GHDB operation'''

    '''basic arg checking'''
    if args['listbool']:
        printcategories()
        os._exit(1)
    if args['category'] < 1 or args['category'] > 14:
        print '[-] Invalid category ID'
        os._exit(1)
    if os.path.isfile(args['outdork']):
        print '[-] Output file already exists'
        os._exit(1)
    
    dorks = retrievedorklist(args['category'])
    print '[+] Writing dorks to disk'
    writeoutdorks(dorks)

if __name__ == "__main__":  
    print ttargs.banner
    if len(sys.argv) == 1:
        print '[-] Missing arguments...quitting!'
        os._exit(1)
    args = vars(ttargs.parser.parse_args())
    try:
        global useragent
        useragent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        if sys.argv[1] == 'ghdb':
            ghdb_main(args)
        if sys.argv[1] == 'cse':
            cse_main(args)
        if sys.argv[1] == 'tsv':
            tsv_main(args)
    except KeyboardInterrupt:
        print '[-] User termination! Quitting early'
        os._exit(1)
    #except:
    #    print '[-] Error! Quitting early'