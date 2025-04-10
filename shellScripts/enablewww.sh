#!/bin/bash
#first
#Type	Name	Value	TTL
#CNAME	www	adenrele.co.uk.	1 hour

#then
#One time script to enable www after cname was added 
flyctl certs add www.adenrele.co.uk