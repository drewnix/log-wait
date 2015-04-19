# log-wait
A script that simply blocks until a log line appears. This is often useful 
in automation where a script or test needs to wait until a specific event 
happens before proceeding.

Usage is:

```
log-wait.py -l /var/log/myservice.log -t 60 -p "Transaction complete"
```
