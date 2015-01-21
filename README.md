crack
===========

Password hash cracking automation utility with XMLRPC server and client modes

A hash file and type are submitted for processing and one or more commands are
parsed from a config file to crack the hashes.

3 modes of operation:
- standalone
- client (connects to remote server mode via XMLRPC)
- server (listens for connections from client mode)

Client/server modes allow hashes to be submitted from a client to a remote
running in server mode. The server processes the hashes in the same manner as a
standalone cracking session and returns the results when finished.

An example config file (crack.default) is included and should be copied to
crack.cfg and edited to specify the location of dictionaries / rainbow tables

---------------------------------------------------------------------------------------------------

Copyright 2011 Stephen Haywood aka AverageSecurityGuy (<https://github.com/averagesecurityguy/crack/>)

---------------------------------------------------------------------------------------------------

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
