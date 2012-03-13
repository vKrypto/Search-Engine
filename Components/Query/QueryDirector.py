#!/usr/bin/env python

import Pyro4
import threading
import Queue
from QueryIndex import QueryIndex

class QueryThread(threading.Thread):
    
    def __init__(self, nameserver, queryindex_ident, result_list, queue):
        threading.Thread.__init__(self)
        queryindex_uri = nameserver.lookup('QueryIndex'+queryindex_ident)
        self.queryindex = Pyro4.Proxy(queryindex_uri)
        self.queryindex_ident = queryindex_ident
        self.result_list = result_list
        self.queue = queue

    def run(self):
        user_query = self.queue.get()
        self.queryindex.query(user_query)
        for result in self.queryindex.return_results():
            self.result_list.append((result[1], result[0]))
        self.queue.task_done()

class IndexData:
    
    def __init__(self, queue):
        ns_host = raw_input('enter nameserver ip: ')
        self.query_count = int(raw_input('Enter number of QueryIndexes: '))
        self.ns = Pyro4.naming.locateNS(ns_host)
        self.queue = queue
        user_query = raw_input('Search for: ')
        for i in range(self.query_count):
            self.queue.put(user_query)
        self.results = []
        
    def begin(self):
        for i in range(self.query_count):
            queryindex = QueryThread(self.ns, str(i), self.results, self.queue)
            queryindex.start()

    def return_results(self):
        results = sorted(self.results, reverse=True)
        for entry in results:
            print entry[1]

            


if __name__ == "__main__":
    queue = Queue.Queue()
    queryindex = IndexData(queue)
    queryindex.begin()
    queue.join()
    queryindex.return_results()
