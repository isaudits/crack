#!/usr/bin/env python
'''
Crackclient makes xmlrpc calls to a crack server to automate password
cracking. Crackclient takes a file, a server:port combination, and a hash
type. The file and hash type are passed to the server and the server returns
an id. The id can be polled to get the results and to see if all of the
cracking processes are finished.

Acceptable hash types are defined in config file associated with
listening crackserver instance.

Optionally, the application can be run in standalone mode (no client/server
flags) and performs cracking operations locally using same config file
'''

import argparse
import xmlrpclib
import time
import SimpleXMLRPCServer as sxml

import modules.crackmanager
import modules.core

class hashlist:
    '''
    TODO: Find a more elegant way of doing this!!!
    
    Hashes that are passed to the cracking mechanism via RPC are passed using 
    xmlrpclib binary class, and are stored in a 'data' attribute. This dummy
    class is to allow us a local class in which to store the hashes in 
    a similarly named attribute so we can re-use the functionality
    
    Need to re-write the core module
    
    '''
    def __init__(self, data):
        self.data = data

        
#------------------------------------------------------------------------------
# Get values from main config file
#------------------------------------------------------------------------------
main_config_file = "config/main.cfg"
main_config_default = "config/main.default"
crack_config_default = "config/crack.default"

modules.core.check_default_config(main_config_file, main_config_default)

remote_ip = modules.core.check_config("REMOTE_IP", main_config_file)
if remote_ip == "": remote_ip = "127.0.0.1"

listener_ip = modules.core.check_config("LISTENER_IP", main_config_file)
if listener_ip == "": listener_ip = "0.0.0.0"

server_port = modules.core.check_config("SERVER_PORT", main_config_file)
if server_port == "": server_port = "8000"

crack_config = modules.core.check_config("CRACK_CONFIG", main_config_file)
if crack_config == "": crack_config = "config/crack.cfg"

config_file = crack_config

modules.core.check_default_config(crack_config, crack_config_default)

#------------------------------------------------------------------------------
# Configure Argparse to handle command line arguments
#------------------------------------------------------------------------------
desc = """
Password cracking automation utility. The script has 3 operating modes:
  Standalone (default)
  Server (--server)
  Client (--client)
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
group = parser.add_mutually_exclusive_group()
group.add_argument("--client", help="client mode",
                action="store_true")
group.add_argument("--server", help="server mode",
                action="store_true")
parser.add_argument("file", nargs="?", action="store", default="hashes.txt",
                    help="specify a hash file (default: hashes.txt)")
parser.add_argument("type", nargs="?", action="store", default="md5",
                    help="specify the hash type (default: md5)")
parser.add_argument("-c", dest="config", action="store", default="config/crack.cfg",
                    help="crack configuration file. (server, standalone modes only; default: config/crack.cfg)")
parser.add_argument("-s", dest="remote_ip", action="store", default=remote_ip,
                    help="IP address that the remote server is listening on. (client mode only; default: " + remote_ip + ")")
parser.add_argument("-l", dest="listener_ip", action="store", default=listener_ip,
                    help="IP address that the local server should listen on. (server mode only; default: " + listener_ip + ")")
parser.add_argument("-p", dest="port", action="store", default=server_port,
                    help="XMLRPC server listening port. (client, server modes only; default: " + server_port +")")

args = parser.parse_args()

#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------

if args.server:
    print "Running in server mode..."
    # Create new CrackManager object to handle cracking process.
    try:
        c = modules.crackmanager.CrackManager(args.config)
        print "CrackManager configured successfully using config file " + args.config
    except Exception, err:
        print "CrackManager configuration unsuccessful:\n"
        print str(err)
        exit()
        
    try:
        server = sxml.SimpleXMLRPCServer((args.listener_ip, int(args.port)),
            requestHandler=sxml.SimpleXMLRPCRequestHandler)
        print "XMLRPC server configuration successful; listening on " + args.listener_ip+":"+args.port
    except Exception, err:
        print "XMLRPC server configuration unsuccessful:\n"
        print str(err)
        exit()
    
    # Register CrackManager functions to be used with by XMLRPC client.
    server.register_introspection_functions()
    server.register_function(c.crack_passwords, 'crack')
    server.register_function(c.get_progress, 'results')
    server.serve_forever()
    
elif args.client:
    print "Running in client mode..."
    # Open connection to xmlrpc server
    connect_addr = 'http://' + args.remote_ip+ ":" + args.port
    try:
        s = xmlrpclib.ServerProxy(connect_addr)
    except Exception, err:
        print "Error opening connection to server " + connect_addr + " - " + str(err)
    
    #Upload hash file to server, send crack request to server and receive ID
    with open(args.file, 'rb') as handle:
        binary_data = xmlrpclib.Binary(handle.read())
    id, msg = s.crack(binary_data, args.type)
    
    if id == 0:
        print msg
    else:
        # Poll server for completion status and results using ID.
        complete = False
        wait = 10
        while True:
            time.sleep(wait)
            complete, results = s.results(id)
            if results != []:
                for r in results:
                    print r.rstrip('\r\n')
            if complete: break 
    
else:
    print "Running in standalone mode..."
    htype = args.type
    hashfile = open(args.file, "r")
    
    hlist = hashlist(hashfile.read())
    
    # Create new CrackManager object to handle cracking process.
    try:
        c = modules.crackmanager.CrackManager(args.config)
        print "CrackManager configured successfully using config file " + args.config
    except Exception, err:
        print "CrackManager configuration unsuccessful:\n"
        print str(err)
        exit()
        
    c.crack_passwords(hlist, htype)
