#!/usr/bin/python

import multiprocessing
import subprocess
import os
from time import sleep
from argparse import ArgumentParser

#TODO: No validation added yet
#TODO: For Mac only


def parse_args():
    parser = ArgumentParser(description="Tool for ping scanning a /24 IP range")
    #parser.add_argument("IPrange", help="The IP range to scan")
    parser.add_argument("--IPsegment", default="192.168")
    parser.add_argument("--start-subnet", default=1, type=int)

    return parser.parse_args()


def pinger( job_q, results_q ):
    DEVNULL = open(os.devnull,'w')
    while True:
        ip = job_q.get()
        if ip is None: break

        try:
            subprocess.check_call(['ping','-c1',ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass


def ping(args, segment):
    pool_size = 255
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()


    pool = [ multiprocessing.Process(target=pinger, args=(jobs,results)) for i in range(pool_size)]

    for p in pool:
        p.start()

    for i in range(1,255):
        jobs.put('{}.{}.{}'.format(args.IPsegment, segment, i))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    while not results.empty():
        ip = results.get()
        print(ip)


def change_int_ip(args, segment):
    print("Changing interface IP")
    subprocess.call([
        'networksetup', '-setmanual', 'Ethernet', '{}.{}.23'.format(args.IPsegment, segment), '255.255.255.0'
    ])
    sleep(3)


if __name__ == '__main__':
    args = parse_args()
    for i in range(args.start_subnet,255):
        change_int_ip(args=args, segment=i)
        ping(args=args, segment=i)
