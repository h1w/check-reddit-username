#!/usr/bin/env python3
version = "1.0.0"

import urllib3
import json
import itertools
import optparse

parser = optparse.OptionParser(usage="usage: %prog [options] arg", version=version)
http = urllib3.PoolManager() # Instance to make requests.

url = "https://www.reddit.com/api/username_available.json?user={}" # Url to reddit api for check username available
dictionary = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890" # Char dictionary for names creating

def Check_Available_Username(username):
    response = http.request("GET", url.format(username)) # Get response from reddit api
    result = json.dumps(json.loads(response.data.decode("utf-8"))) # Result. Decoding, converting to string from json
    format_print = "Username: {} - {}"
    if result == "true":
        print(format_print.format(username, "Available"))
    else:
        print(format_print.format(username, "Not Available"))

def Check_Available_Username_By_Length(length):
    permutations = list(map(lambda x: "".join(x), itertools.product(dictionary, repeat=length))) # String which contains usernames from itertools.product. Example of itertools.product: product('ABCD', repeat=2) - AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD
    file = open("availables.txt", "a") # File for available usernames
    for username in permutations:
        response = http.request("GET", url.format(username)) # Get response from reddit api
        result = json.dumps(json.loads(response.data.decode("utf-8"))) # Result. Decoding, converting to string from json
        format_print = "Username: {} - {}"
        if result == "true":
            print(format_print.format(username, "Available\tYES!"))
            file.write("{}\n".format(username)) # Add Available result to file
        elif result == "false":
            print(format_print.format(username, "Not Available"))

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
    Check_Available_Username_By_Length(options.usernames_length)