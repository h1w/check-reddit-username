#!/usr/bin/env python3
version = "1.0.2"

import asyncio
import aiohttp
import aiohttp_proxy
import urllib3
import itertools
import optparse
import json
import time

timestr = time.strftime("%Y%m%d-%H%M%S")
parser = optparse.OptionParser(usage="usage: %prog [options] arg", version=version)
http = urllib3.PoolManager() # Instance to make requests.

url_redditapi = "https://www.reddit.com/api/username_available.json?user={}" # Url to reddit api for check username available
dictionary = "qwertyuiopasdfghjklzxcvbnm1234567890" # Char dictionary for names creating

async def GetProxies():
    url = 'https://rach.gq/p'
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    proxies = list(map(lambda x: [x.split(' ')[0], x.split(' ')[1], x.split(' ')[2]], response.data.decode('utf-8').split('\n')[:-1]))
    return proxies

async def Request(url=None, connector=None):
    try:
        async with aiohttp.ClientSession(connector=connector) as client:
            async with client.get(url, timeout=10) as response:
                assert response.status == 200
                return await response.text()
    except Exception:
        pass

async def RequestProxy(url, host_port, ptype, country):
    connector = aiohttp_proxy.ProxyConnector.from_url('{}://{}'.format(ptype, host_port), verify_ssl=False)
    response = await Request(url, connector)
    if response is None: return "ProxyErr"
    #return [host_port, ptype, country]
    return response

async def Check_Available_Usernames_By_Length_Async(length):
    permutations = list(map(lambda x: "".join(x), itertools.product(dictionary, repeat=length))) # String which contains usernames from itertools.product. Example of itertools.product: product('ABCD', repeat=2) - AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD
    all_permutations_count = len(permutations)
    available_usernames = 0
    already_checked_usernames = 0
    with open('available-{}.txt'.format(timestr), 'w') as f: # File for available usernames
        while len(permutations) != 0:
            proxies = await GetProxies()
            usernames = permutations[:len(proxies)]
            ucount=0
            tasks=[]
            for proxy in proxies:
                host_port, ptype, country = proxy[0], proxy[1], proxy[2]
                url = url_redditapi.format(usernames[ucount])
                ucount+=1
                task = asyncio.ensure_future(RequestProxy(url, host_port, ptype, country))
                tasks.append(task)
            #responses = [x for x in await asyncio.gather(*tasks) if x != False]
            responses = await asyncio.gather(*tasks)
            
            for i in range(0,len(responses)):
                if responses[i] == "ProxyErr":
                    permutations.append(usernames[i])
                else:
                    #print(usernames[i], responses[i])
                    already_checked_usernames += 1
                    if responses[i] == 'true':
                        f.write('{}\n'.format(usernames[i]))
                        f.flush()
                        available_usernames+=1
            permutations = permutations[len(proxies):]
            print('\033[H\033[J', end='') # Clear python console output
            print('[Checking]\nAvailable usernames: {}\nAlready checked: {}\nLeft: {}\nTotal: {}'.format(available_usernames, already_checked_usernames, len(permutations), all_permutations_count)) # All info on clear console
        f.close()

async def Check_Available_Username_Async(username):
    proxies = await GetProxies()
    tasks=[]
    result = False
    for proxy in proxies:
        host_port, ptype, country = proxy[0], proxy[1], proxy[2]
        response = await RequestProxy(url_redditapi.format(username), host_port, ptype, country)
        if response == "ProxyErr":
            continue
        else:
            if response == 'true':
                print('Username: {} - Available'.format(username))
                result = True
            elif response == 'false':
                print('Username: {} - Not available'.format(username))
                result = True            
            break
    if result == False:
        print('Sorry, try again. =(\nProxy servers may be faulty, or you entered too long username.')

def Check_Available_Username(username):
    if len(username) < 3: # Checking the dimension of the username 
        print('Sorry, but username must be more than 2 characters.')
    asyncio.run(Check_Available_Username_Async(username))

def Check_Available_Usernames_By_Length(length):
    if length < 3: # Checking the dimension of the username 
        print('Sorry, but username must be more than 2 characters.')
        exit()
    print('\033[H\033[J', end='') # Clear python console output
    print('Checking...')
    asyncio.run(Check_Available_Usernames_By_Length_Async(length))

parser.add_option(
    "-n", "--byname",
    action="store",
    help="Check available username by name.",
    type="string",
    dest="username"
)

parser.add_option(
    "-l", "--bylen",
    action="store",
    help="Check available username by dictionary with declarated length. Result will be logged to file: available.txt",
    type=int,
    dest="usernames_length"
)

options, args = parser.parse_args()

if options.username != None:
    Check_Available_Username(options.username)
if options.usernames_length != None:
    Check_Available_Usernames_By_Length(options.usernames_length)