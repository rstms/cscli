Description
===========

``netchat`` is used to connect to a listening TCP port and interact with
text data sent over the stream.

Chat Script
***********
The interaction is described using a script, which is a list of EXPECT, SEND
elements.  

An EXPECT or SEND element is defined as a sequence of characters delimited by 
whitespace.  Quotes may be used to designate multiple word elements.  Quotes
may also describe an empty string, in which case the corresponding action is
skipped.

The simplest script consists of a single EXPECT.  In this case the program
will will connect and read data from the channel until the expected value 
is found.

Script Format
*************
The script may be specified as a command line argument or read from a file.
When provided as a file, comment lines beginning with ``#`` will be ignored.

Network Utilities
*****************
An internal communication function is the default.  Optionally the network
communication may be performed by either ``socat`` or ``netcat`` if one of
these is available on the system.


