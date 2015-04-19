#!/usr/bin/python
"""
-------------
 Description
-------------
This script tails the end of a file attempting to match a pattern against each subsequent
line. If it can't match the line with in a specific time interval it exits with a failure.

----------------
 Usage Example
----------------
log-wait.py -l /var/log/myservice.log -t 60 -p "Transaction complete"
"""

import os
import sys
import signal
import time
import re
from optparse import OptionParser

__author__ = "Andrew Tanner <andrew@refleqtive.com>"

class TimeoutException(Exception):
    """ Exception that gets thrown when the pattern search times out """
    pass

class PatternMatchException(Exception):
    """ Exception that gets thrown when a pattern match is found """
    pass

def log_waiter(filename, pattern, timeout=30):
    """ Tails the end of a file attempting to match a pattern against each subsequent line,
        if the method doesn't match the pattern with in the passed in timeout, it throws
        a TimeoutException().
    """
    def timeout_handler(signum, frame):
        raise TimeoutException()

    fh = open(filename, 'r')

    # set a signal handler for the alarm signal
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    # obtain the length of the file and seek to the end
    st_results = os.stat(filename)
    st_size = st_results[6]
    fh.seek(st_size)

    # loop over all subsequent lines written to the log file
    while 1:
        pos = fh.tell()
        line = fh.readline()

        if not line:
            time.sleep(1)
            fh.seek(pos)
        else:
            if re.search(pattern, line):
                raise PatternMatchException()

if __name__=="__main__":
    parser = OptionParser()

    parser.add_option("-l", "--logfile", dest="logfile",
        help="The name of the log file to monitor")

    parser.add_option("-t", "--timeout", dest="timeout", default=30, type="int",
        help="The length of time to wait for the line to appear in the log")

    parser.add_option("-p", "--pattern", dest="pattern", 
        help="Pattern to match searching through log lines in the log file")

    (options, args) = parser.parse_args()

    if (not options.logfile):
        print "Error: MUST specify a log file to monitor using the --logfile option"
        parser.print_help()
        sys.exit(1)

    if (not options.pattern):
        print "Error: MUST specify a pattern to look for in the log using the --pattern option"
        parser.print_help()
        sys.exit(1)

    try:
        log_waiter(options.logfile, options.pattern, options.timeout)
    except PatternMatchException, e:
        print "Success: Captured log line %s from file %s" % (options.pattern, options.logfile)
        sys.exit(0)
    except TimeoutException, e:
        print "Failure: Hit timeout waiting for log line %s from file %s" % (options.pattern, options.logfile)
        sys.exit(1)

    # we got neither exception, something went wrong
    print "Failure: Unexpected situation occured, no log line match or timeout was hit"
    sys.exit(2)
