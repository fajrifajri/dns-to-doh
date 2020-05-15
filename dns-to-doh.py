import json
import urllib.request
import socketserver
from dnslib import *


# curl -s -H 'accept: application/dns+json' 'https://dns.google.com/resolve?name=www.potaroo.net&type=A'

url = "https://dns.google.com/resolve?"
IP = "0.0.0.0"
PORT = 53

def get_dns_response(qname, qtype):
    query = url + "name=" +qname + "&type="+qtype
    doh_query = urllib.request.urlopen(query)
    doh_response = json.loads(doh_query.read())

    dns_response = []
    if doh_response['Status'] == 0:
        doh_output = doh_response['Answer']
        for i in doh_output:
            if i['type']==1:
                dns_response.append(i['data'])
    return(dns_response)

class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        response = dnsProcessing(data)
        socket.sendto(response, self.client_address)


def dnsProcessing(rawUdpData):
    dnsRequest = DNSRecord.parse(rawUdpData)
    dnsResponse = DNSRecord(
            DNSHeader(
                id=dnsRequest.header.id,
                qr=1,
                aa=1,
                ra=1),
            q=dnsRequest.q
            )
    dns_qname = dnsRequest.q.qname
    dns_qtype = dnsRequest.q.qtype
    dns_response = get_dns_response(str(dns_qname), str(dns_qtype))
    for i in dns_response:
        dnsResponse.add_answer(
            RR(
                rname=dns_qname,
                rtype=dns_qtype,
                rclass=1,
                ttl=60,
                rdata=A(i)
        ))
    return(dnsResponse.pack()) 
    
if __name__ == '__main__':
    server =socketserver.UDPServer((IP, PORT), UDPHandler)
    server.serve_forever()