#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
import socket
import os
import sys
import struct
import time
import random
import traceback
import threading
# NOTE: Do NOT import other libraries!

UDP_CODE = socket.IPPROTO_UDP
ICMP_ECHO_REQUEST = 8
MAX_DATA_RECV = 65535
MAX_TTL = 30

def setupArgumentParser() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='A collection of Network Applications developed for SCC.231.')
        parser.set_defaults(func=ICMPPing, hostname='lancaster.ac.uk')
        subparsers = parser.add_subparsers(help='sub-command help')
        
        parser_p = subparsers.add_parser('ping', aliases=['p'], help='run ping')
        parser_p.set_defaults(timeout=2, count=10)
        parser_p.add_argument('hostname', type=str, help='host to ping towards')
        parser_p.add_argument('--count', '-c', nargs='?', type=int,
                              help='number of times to ping the host before stopping')
        parser_p.add_argument('--timeout', '-t', nargs='?',
                              type=int,
                              help='maximum timeout before considering request lost')
        parser_p.set_defaults(func=ICMPPing)

        parser_t = subparsers.add_parser('traceroute', aliases=['t'],
                                         help='run traceroute')
        parser_t.set_defaults(timeout=2, protocol='udp')
        parser_t.add_argument('hostname', type=str, help='host to traceroute towards')
        parser_t.add_argument('--timeout', '-t', nargs='?', type=int,
                              help='maximum timeout before considering request lost')
        parser_t.add_argument('--protocol', '-p', nargs='?', type=str,
                              help='protocol to send request with (UDP/ICMP)')
        parser_t.set_defaults(func=Traceroute)
        
        parser_m = subparsers.add_parser('mtroute', aliases=['mt'],
                                         help='run traceroute')
        parser_m.set_defaults(timeout=2, protocol='udp')
        parser_m.add_argument('hostname', type=str, help='host to traceroute towards')
        parser_m.add_argument('--timeout', '-t', nargs='?', type=int,
                              help='maximum timeout before considering request lost')
        parser_m.add_argument('--protocol', '-p', nargs='?', type=str,
                              help='protocol to send request with (UDP/ICMP)')
        parser_m.set_defaults(func=MultiThreadedTraceRoute)

        parser_w = subparsers.add_parser('web', aliases=['w'], help='run web server')
        parser_w.set_defaults(port=8080)
        parser_w.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_w.set_defaults(func=WebServer)

        parser_x = subparsers.add_parser('proxy', aliases=['x'], help='run proxy')
        parser_x.set_defaults(port=8000)
        parser_x.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_x.set_defaults(func=Proxy)

        if len(sys.argv) < 2:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args()

        return args


class NetworkApplication:

    def checksum(self, dataToChecksum: bytes) -> int: 
        csum = 0
        countTo = (len(dataToChecksum) // 2) * 2
        count = 0

        while count < countTo:
            thisVal = dataToChecksum[count+1] * 256 + dataToChecksum[count]
            csum = csum + thisVal
            csum = csum & 0xffffffff
            count = count + 2

        if countTo < len(dataToChecksum):
            csum = csum + dataToChecksum[len(dataToChecksum) - 1]
            csum = csum & 0xffffffff

        csum = (csum >> 16) + (csum & 0xffff)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)

        answer = socket.htons(answer)

        return answer

    # Print Ping output
    def printOneResult(self, destinationAddress: str, packetLength: int, time: float, seq: int, ttl: int, destinationHostname=''):
        if destinationHostname:
            print("%d bytes from %s (%s): icmp_seq=%d ttl=%d time=%.3f ms" % (packetLength, destinationHostname, destinationAddress, seq, ttl, time))
        else:
            print("%d bytes from %s: icmp_seq=%d ttl=%d time=%.3f ms" % (packetLength, destinationAddress, seq, ttl, time))

    def printAdditionalDetails(self, host, numPacketsTransmitted, rtts):
        if len(rtts) > 0:
            print(f'--- {host} ping statistics ---')
            lossPercent = int((100.0 - 100.0*(len(rtts)/numPacketsTransmitted)))
            print(f'{numPacketsTransmitted} packets transmitted, {len(rtts)} received, {lossPercent}% packet loss')
            avgRTT = sum(rtts) / len(rtts)
            deviations = [abs(rtt - avgRTT) for rtt in rtts]
            mdev = sum(deviations) / len(deviations)
            minRTT = min(rtts)
            maxRTT = max(rtts)
            print("rtt min/avg/max/mdev = %.3f/%.3f/%.3f/%.3f ms" % (1000*minRTT, 1000*avgRTT, 1000*maxRTT, 1000*mdev))

    # Print one line of traceroute output
    def printMultipleResults(self, ttl: int, pkt_keys: list, hop_addrs: dict, rtts: dict, destinationHostname = ''):
        if pkt_keys is None:
            print(str(ttl) + '   * * *')
            return
        # Sort packet keys (sequence numbers or UDP ports)
        pkt_keys = sorted(pkt_keys)
        output = str(ttl) + '   '
        last_hop_addr = None
        last_hop_name = None

        for pkt_key in pkt_keys:
            # If packet key is missing in hop addresses, this means no response received: print '*'
            if pkt_key not in hop_addrs.keys():
                output += '* '
                continue
            hop_addr = hop_addrs[pkt_key]

            # Get the RTT for the probe
            rtt = rtts[pkt_key]
            if last_hop_addr is None or hop_addr != last_hop_addr:
                hostName = None
                try:
                    # Get the hostname for the hop
                    hostName = socket.gethostbyaddr(hop_addr)[0]
                    if last_hop_addr is None:
                        output += hostName + ' '
                    else: 
                        output += ' ' + hostName + ' '
                except socket.herror:
                    output += hop_addr + ' '
                last_hop_addr = hop_addr
                last_hop_name = hostName
                output += '(' + hop_addr + ') '

            output += str(round(1000*rtt, 3))
            output += ' ms  '
                
        print(output)           

class ICMPPing(NetworkApplication):
    
    def __init__(self, args):
        host = None
        # 1. Look up hostname, resolving it to an IP address
        try:
            host = socket.gethostbyname(args.hostname)
        except socket.gaierror:
            print('Invalid hostname: ', args.hostname) 
            return

        print('Ping to: %s (%s)...' % (args.hostname, host))

        # 1. Create an ICMP socket 
        try:
            self.icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except socket.error as err:
            traceback.print_exception(err)
            exit(1)

        # 2. Set a timeout on the socket
        self.icmpSocket.settimeout(args.timeout)

        # 3. Send ping probes and collect responses 
        numPings = args.count
        seq_num = 0
        numPingsSent = numPings
        rtts = [] 
        while(numPings > 0):

            # 4. Do one ping approximately every second
            rtt, ttl, packetSize, seq = self.doOnePing(host, args.timeout, seq_num)

            # 5. Print out the RTT (and other relevant details) using the printOneResult method
            if rtt is not None:
                self.printOneResult(host, packetSize, rtt*1000, seq, ttl) 
                rtts.append(rtt)

            # 6. Sleep for a second
            time.sleep(1) 

            # 7. Update sequence number and number of pings
            seq_num += 1
            numPings -= 1

        # 8. Print loss and RTT statistics (average, max, min, etc.)
        self.printAdditionalDetails(args.hostname, numPingsSent, rtts)
        
        # 9. Close ICMP socket
        self.icmpSocket.close()

    # Receive Echo ping reply
    def receiveOnePing(self, destinationAddress, packetID, sequenceNumSent, timeout):
        
        # 1. Wait for the socket to receive a reply
        echoReplyPacket = None
        isTimedout = False
        try:
            echoReplyPacket, addr = self.icmpSocket.recvfrom(MAX_DATA_RECV)
        except socket.timeout as e:
            isTimedout = True

        # 2. Once received, record time of receipt, otherwise, handle a timeout
        timeRecvd = time.time()
        if isTimedout: # timeout
            return None, None, None, None

        # 3. Extract the IP header: 

        # The first 20 bytes is the IP header:  
        # (see: https://en.wikipedia.org/wiki/IPv4#/media/File:IPv4_Packet-en.svg):
        # 0          4             8          16          24           32 bits
        # |  Version | IP Hdr  Len |     TOS   |      Total Length     |
        # |         Identification             |Flag |  Fragment offset|
        # |        TTL             |  Protocol |     Header Checksum   |
        # |           Source IP  Address(32 bits, i.e., 4 bytes)       |
        # |           Destination IP Address (32 bits, i.e., 4 bytes)  |
        # |     Option (up to 40 bytes) this is an optional field      |

        ip_header = echoReplyPacket[:20]
        version_ihl, tos, total_length, identification, flags_offset, ttl, proto, checksum, src_ip, dest_ip = struct.unpack('!BBHHHBBH4s4s', ip_header)

        # Read the IP Header Length (using bit masking) 
        ip_header_len_field = (version_ihl & 0x0F)

        # This field contains the length of the IP header in terms of 
        # the number of 4-byte words. So value 5 indicates 5*4 = 20 bytes. 
        ip_header_len = ip_header_len_field * 4

        payloadSize = total_length - ip_header_len

        # Now parse the ICMP header:
        # 0         8           16         24          32 bits
        #     Type  |    Code   |       Checksum       |
        #     Packet Identifier |       Sequence num   |
        #        <Optional timestamp (8 bytes) for     |
        #        a stateless ping>                     |        
        icmpHeader = echoReplyPacket[ip_header_len:ip_header_len + 8]
        icmpType, code, checksum, p_id, sequenceNumReceived = struct.unpack('!BBHHH', icmpHeader)

        # 5. Check that the ID and sequence numbers match between the request and reply
        if packetID != p_id or sequenceNumReceived != sequenceNumSent:
            return None, None, None, None

        # 6. Return the time of Receipt
        return timeRecvd, ttl, payloadSize, sequenceNumReceived

    # NOTE: This method can be re-used by ICMP traceroute
    # Send Echo Ping Request
    def sendOnePing(self, destinationAddress, packetID, sequenceNumber, ttl=None, dataLength=0):
        # 1. Build ICMP header
        header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, packetID, sequenceNumber)
        
        # 2. Checksum ICMP packet using given function
        # include some bytes 'AAA...' in the data (payload) of ping
        data = str.encode(dataLength * 'A')
        my_checksum = self.checksum(header+data)

        # 3. Insert checksum into packet
        # NOTE: it is optional to include an additional 8-byte timestamp (time when probe is sent)
        # in which case, a stateless ping can be implemented: the response will contain
        # the sending time so no need to keep that state, 
        # but we don't do that here (instead, we record sending time state in step 5)
        packet = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), packetID, sequenceNumber)

        if ttl is not None:
            self.icmpSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # 4. Send packet using socket
        self.icmpSocket.sendto(packet+data, (destinationAddress, 1))

        # 5. Record time of sending (state)
        timeSent = time.time()
        return timeSent

    def doOnePing(self, destinationAddress, timeout, seq_num):

        # 3. Call sendOnePing function
        packetID = random.randint(1, 65535)
        timeSent = self.sendOnePing(destinationAddress, packetID, seq_num, dataLength=48)

        # 4. Call receiveOnePing function
        timeReceipt, ttl, packetSize, seq = self.receiveOnePing(destinationAddress, packetID, seq_num, timeout)

        # 5. Compute RTT
        rtt = None
        if timeReceipt is None:
            print("Error receiveOnePing() has timed out")
        else:
            rtt = timeReceipt - timeSent

        # 6. Return total network delay, ttl, size and sequence number
        return rtt, ttl, packetSize, seq

# A partially implemented traceroute 
class Traceroute(ICMPPing):

    def __init__(self, args):
        args.protocol = args.protocol.lower()
        self.args = args
        
        # 1. Look up hostname, resolving it to an IP address
        self.dstAddress = None
        try:
            self.dstAddress = socket.gethostbyname(args.hostname)
            #socket.getaddrinfo(args.hostname, None, socket.AF_INET6)
        except socket.gaierror:
            print('Invalid hostname: ', args.hostname) 
            return
        print('%s traceroute to: %s (%s) ...' % (args.protocol, args.hostname, self.dstAddress))

        # 2. Initialise instance variables
        self.isDestinationReached = False

        # 3. Create a raw socket bound to ICMP protocol
        self.icmpSocket = None
        try:
            self.icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except socket.error as err:
            traceback.print_exception(err)
            exit(1)

        # 4. Set a timeout on the socket
        self.icmpSocket.settimeout(args.timeout)

        # 5. Run traceroute
        self.runTraceroute()

        # 6. Close ICMP socket
        self.icmpSocket.close()

    def runTraceroute(self):

        hopAddr = None
        pkt_keys = []
        hop_addrs = dict()
        rtts = dict()
        ttl = 1

        while(ttl <= MAX_TTL and self.isDestinationReached == False):
            if self.args.protocol == "icmp":
                self.sendIcmpProbesAndCollectResponses(ttl)

            elif self.args.protocol == "udp":
                self.sendUdpProbesAndCollectResponses(ttl)
            else:
                print(f"Error: invalid protocol {args.protocol}. Use udp or icmp")
                sys.exit(1)
            ttl += 1

    # Send 3 ICMP traceroute probes per TTL and collect responses
    def sendIcmpProbesAndCollectResponses(self, ttl):
 
        pkt_keys = []
        hop_addrs = dict()
        rtts = dict()

        for _ in range(3):


        # Use a deterministic, unique seq number per probe
            seq_num = (ttl - 1) * 3 + _
            pkt_keys.append(seq_num)

            # 1. Send ICMP probe
            timeSent = self.sendOnePing(self.dstAddress, seq_num, seq_num, ttl=ttl, dataLength=48)

            # 2. Receive reply
            trReplyPacket, hopAddr, timeRecvd = self.receiveOneTraceRouteResponse()
            if trReplyPacket is None:
                continue

            # 3. Extract identifiers
            p_id_recv, seq_recv, icmpType = self.parseICMPTracerouteResponse(trReplyPacket)
            if p_id_recv is None or seq_recv is None:
                continue

            # 4. Check destination
            if hopAddr == self.dstAddress and (icmpType == 0 or icmpType == 3):
                self.isDestinationReached = True

            # 5. Match probe
            if seq_recv == seq_num:
                hop_addrs[seq_num] = hopAddr
                rtts[seq_num] = timeRecvd - timeSent

        # 6. Print ICMP results exactly like UDP version
        self.printMultipleResults(ttl, pkt_keys, hop_addrs, rtts, self.args.hostname)
    

    # Send 3 UDP traceroute probes per TTL and collect responses
    def sendUdpProbesAndCollectResponses(self, ttl):
        
        hopAddr = None
        icmpType = None
        pkt_keys = []
        hop_addrs = dict()
        rtts = dict()

        numBytes = 52
        dstPort = 33439
        
        for _ in range(3): 
            # 1. Send one UDP traceroute probe
            dstPort += 1
            timeSent = self.sendOneUdpProbe(self.dstAddress, dstPort , ttl, numBytes)

            # 2. Record a unique key (UDP destination port) associated with the probe
            pkt_keys.append(dstPort)

            # 3. Receive the response (if one arrives within the timeout)
            trReplyPacket, hopAddr, timeRecvd = self.receiveOneTraceRouteResponse()
            if trReplyPacket is None:
                # Nothing is received within the timeout period
                continue
            
            # 4. Extract destination port from the reply
            dstPortReceived, icmpType = self.parseUDPTracerouteResponse(trReplyPacket)
        
            # 5. Check if we reached the destination 
            if self.dstAddress == hopAddr and icmpType == 3:
                self.isDestinationReached = True

            # 6. If the response matches the request, record the rtt and the hop address
            if dstPort == dstPortReceived:
                rtts[dstPort] = timeRecvd - timeSent
                hop_addrs[dstPort] = hopAddr

        # 7. Print one line of the results for the 3 probes
        self.printMultipleResults(ttl, pkt_keys, hop_addrs, rtts, args.hostname)

    # Parse the response to UDP probe 
    def parseUDPTracerouteResponse(self, trReplyPacket):

        # 1. Parse the IP header
        dst_port = None
        # Extract the first 20 bytes 
        ip_header = struct.unpack("!BBHHHBBH4s4s", trReplyPacket[:20])

        # 2. Read the IP Header Length (using bit masking) 
        ip_header_len_field = (ip_header[0] & 0x0F)

        # 3. Compute the IP header length
        # This field contains the length of the IP header in terms of 
        # the number of 4-byte words. So value 5 indicates 5*4 = 20 bytes. 
        ip_header_len = ip_header_len_field * 4
        
        # 4. Parse the outermost ICMP header which is 8 bytes long:
        # 0         8           16         24          32 bits
        #     Type  |    Code   |       Checksum       |
        #     Packet Identifier |       Sequence num   |
        # This header contains type, Code and Checksum + 4 bytes of padding (0's)
        # We only care about type field
        icmpType, _, _, _, _  = struct.unpack("!BBHHH", trReplyPacket[ip_header_len:ip_header_len + 8])
        
        # 5. Parse the ICMP message if it has the expected type
        if icmpType == 3 or icmpType == 11:
            ip_header_inner = struct.unpack("!BBHHHBBH4s4s", trReplyPacket[ip_header_len + 8:ip_header_len+28])

            # This is the original IP header sent in the probe packet
            # It should be 20 bytes, but let's not assume anything and extract the length
            # of the header
            ip_header_len_field = (ip_header_inner[0] & 0x0F)
            ip_header_inner_len = ip_header_len_field * 4
            
            # Extract the destination port and match using source port (UDP)
            _, dst_port, _, _ = struct.unpack('!HHHH', trReplyPacket[ip_header_len + 8 + ip_header_inner_len : ip_header_len + 8 + ip_header_inner_len + 8])

        return dst_port, icmpType
    
    def parseICMPTracerouteResponse(self, trReplyPacket):
        # 1. Parse the outer IP header
        ip_header = struct.unpack("!BBHHHBBH4s4s", trReplyPacket[:20])

        # 2. Compute the IP header length
        ip_header_len = (ip_header[0] & 0x0F) * 4

        # 3. Parse the outermost ICMP header to get type, id and sequence
        icmpType, _, _, packet_id, seq = struct.unpack("!BBHHH", trReplyPacket[ip_header_len:ip_header_len + 8])

        # 4. If the packet is an ICMP error (TTL exceeded or destination unreachable),
        # the original ICMP probe header is embedded: extract id and sequence from it
        if icmpType == 11 or icmpType == 3:
            inner_ip_header = struct.unpack("!BBHHHBBH4s4s", trReplyPacket[ip_header_len + 8:ip_header_len + 28])
            inner_ip_header_len = (inner_ip_header[0] & 0x0F) * 4
            inner_icmp = struct.unpack("!BBHHH", trReplyPacket[ip_header_len + 8 + inner_ip_header_len : ip_header_len + 8 + inner_ip_header_len + 8])
            packet_id, seq = inner_icmp[3], inner_icmp[4]

        # 5. Return the identifier, sequence number and ICMP type
        return packet_id, seq, icmpType           

    def receiveOneTraceRouteResponse(self):

        timeReceipt = None
        hopAddr = None
        pkt = None

        # 1. Receive one packet or timeout
        try:
            pkt, addr = self.icmpSocket.recvfrom(MAX_DATA_RECV)
            timeReceipt = time.time()
            hopAddr = addr[0]
        
        # 2. Handler for timeout on receive
        except socket.timeout as e:
            timeReceipt = None

        # 3. Return the packet, hop address and the time of receipt
        return pkt, hopAddr, timeReceipt

    def sendOneUdpProbe(self, destAddress, port, ttl, dataLength):

        # 1. Create a UDP socket
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP_CODE)

        # 2. Use a socket option to set the TTL in the IP header
        udpSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # 3. Send the UDP traceroute probe
        udpSocket.sendto(str.encode(dataLength * '0'), (destAddress, port))

        # 4. Record the time of sending
        timeSent = time.time()

        # 5. Close the UDP socket
        udpSocket.close()

        return timeSent

class MultiThreadedTraceRoute(Traceroute):

    def __init__(self, args):
        # 1. Initialise instance variables (add others if needed)
        args.protocol = args.protocol.lower()
        self.protocol = args.protocol
        self.timeout = args.timeout
        self.send_complete = threading.Event()
        # NOTE you must use a lock when accessing data shared between the two threads
        self.lock = threading.Lock()
        self.sent_probes = dict()
        self.udp_port = 33439
        self.ttl_keys = dict()
        self.hop_addrs = dict()
        self.rtts = dict()
        self.hostname = args.hostname

        # 2. Look up hostname, resolving it to an IP address
        self.dstAddress = None
        try:
            self.dstAddress = socket.gethostbyname(args.hostname)
            #socket.getaddrinfo(args.hostname, None, socket.AF_INET6)
        except socket.gaierror:
            print('Invalid hostname: ', args.hostname) 
            return
        print('%s multi-threaded traceroute to: %s (%s) ...' % (args.protocol, args.hostname, self.dstAddress))


        # 3. Initialise instance variables
        self.isDestinationReached = False

        # 4. Create a raw socket bound to ICMP protocol
        self.icmpSocket = None
        try:
            self.icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except socket.error as err:
            traceback.print_exception(err)
            exit(1)

        # 5. Set a timeout on the socket
        self.icmpSocket.settimeout(args.timeout)



        # 6. Create a thread to send probes
        self.send_thread = threading.Thread(target=self.send_probes)

        # 7. Create a thread to receive responses 
        self.recv_thread = threading.Thread(target=self.receive_responses)

        # 8. Start the threads
        self.send_thread.start()
        self.recv_thread.start()

        # 9. Wait until both threads are finished executing
        self.send_thread.join()
        self.recv_thread.join()

        # 10. Print results after both threads complete
        for ttl in sorted(self.ttl_keys.keys()):
            pkt_keys = self.ttl_keys.get(ttl, [])
            hop_addrs = self.hop_addrs.get(ttl, {})
            rtts = self.rtts.get(ttl, {})
            self.printMultipleResults(ttl, pkt_keys, hop_addrs, rtts, self.hostname)

        self.icmpSocket.close()
            
    # Thread to send probes (to be implemented, a skeleton is provided)
    def send_probes(self):

        ttl = 1
        while ttl <= MAX_TTL and not self.isDestinationReached:
            # Send three probes per TTL
            with self.lock:
                self.ttl_keys.setdefault(ttl, [])
            for _ in range(3):  
                if self.protocol == "icmp":
                    packetID = random.randint(1, 65535)
                    seq_num = (ttl - 1) * 3 + _
                    timeSent = self.sendOnePing(self.dstAddress, packetID, seq_num, ttl, dataLength=48)
                    with self.lock:
                        self.ttl_keys[ttl].append(seq_num)
                        self.sent_probes[seq_num] = {"ttl": ttl, "id": packetID, "time": timeSent, "type": "icmp"}
                    
                elif self.protocol == "udp":
                    self.udp_port += 1
                    timeSent = self.sendOneUdpProbe(self.dstAddress, self.udp_port, ttl, 48)
                    with self.lock:
                        self.ttl_keys[ttl].append(self.udp_port)
                        self.sent_probes[self.udp_port] = {"ttl": ttl, "time": timeSent, "type": "udp"}

                # Sleep for a short period between sending probes
                time.sleep(0.05)  # Small delay between probes

            ttl += 1

        # A final sleep before notifying the receive thread to exit
        time.sleep(self.timeout)
        # Notify the other thread that sending is complete
        self.send_complete.set()

    # Thread to receive responses (to be implemented, a skeleton is provided)
    def receive_responses(self):

        # Keep receiving responses until notified by the other thread
        while True:
            with self.lock:
                pending = bool(self.sent_probes)
            if self.send_complete.is_set() and not pending:
                break

            # 1. Receive one traceroute reply (or timeout)
            pkt, hopAddr, timeRecvd = self.receiveOneTraceRouteResponse()
            if pkt is None:
                if self.send_complete.is_set():
                    # 2. Drop any expired outstanding probes after sender is done
                    now = time.time()
                    with self.lock:
                        expired = [k for k, v in self.sent_probes.items() if now - v["time"] >= self.timeout]
                        for key in expired:
                            self.sent_probes.pop(key, None)
                    with self.lock:
                        pending = bool(self.sent_probes)
                    if not pending:
                        break
                continue

            if self.protocol == "icmp":
                # 3. Parse ICMP response and match to sent probe
                packet_id, seq, icmpType = self.parseICMPTracerouteResponse(pkt)
                if seq is None or packet_id is None:
                    continue
                with self.lock:
                    probe = self.sent_probes.get(seq)
                    if probe is None or probe.get("type") != "icmp" or probe.get("id") != packet_id:
                        continue
                    ttl = probe["ttl"]
                    timeSent = probe["time"]
                    self.hop_addrs.setdefault(ttl, {})[seq] = hopAddr
                    self.rtts.setdefault(ttl, {})[seq] = timeRecvd - timeSent
                    self.sent_probes.pop(seq, None)
                if hopAddr == self.dstAddress and (icmpType == 0 or icmpType == 3):
                    self.isDestinationReached = True
                    self.send_complete.set()

            elif self.protocol == "udp":
                # 4. Parse UDP-triggered ICMP response and match to sent probe
                dst_port, icmpType = self.parseUDPTracerouteResponse(pkt)
                if dst_port is None:
                    continue
                with self.lock:
                    probe = self.sent_probes.get(dst_port)
                    if probe is None or probe.get("type") != "udp":
                        continue
                    ttl = probe["ttl"]
                    timeSent = probe["time"]
                    self.hop_addrs.setdefault(ttl, {})[dst_port] = hopAddr
                    self.rtts.setdefault(ttl, {})[dst_port] = timeRecvd - timeSent
                    self.sent_probes.pop(dst_port, None)
                if hopAddr == self.dstAddress and icmpType == 3:
                    self.isDestinationReached = True
                    self.send_complete.set()
                    
# A basic multi-threaded web server implementation

# You can test the web server as follows: 
# First, run the server in the terminal: python3 NetworkApplications.py web 
# Then, copy the following and paste to a browser's address bar: 127.0.0.1:8080/index.html
# NOTE: the index.html file needs to be downloaded from the Moodle (Dummy HTML file)
# and copied to the folder where you run this code
class WebServer(NetworkApplication):

    def __init__(self, args):
        print('Web Server starting on port: %i...' % args.port)
        
        # 1. Create a TCP socket 
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 2. Bind the TCP socket to server address and server port
        serverSocket.bind(("", args.port))
        
        # 3. Continuously listen for connections to server socket
        serverSocket.listen(100)
        print("Server listening on port", args.port)
        
        while True:
            # 4. Accept incoming connections
            connectionSocket, addr = serverSocket.accept()
            print(f"Connection established with {addr}")
            
            # 5. Create a new thread to handle each client request
            threading.Thread(target=self.handleRequest, args=(connectionSocket,)).start()

        # Close server socket (this would only happen if the loop was broken, which it isn't in this example)
        serverSocket.close()

    def handleRequest(self, connectionSocket):
        try:
            # 1. Receive request message from the client
            message = connectionSocket.recv(MAX_DATA_RECV).decode()

            # 2. Extract the path of the requested object from the message (second part of the HTTP header)
            filename = message.split()[1]
            if filename == '/':
                filename = '/index.html'

            # 3. Read the corresponding file from disk
            with open(filename[1:], 'r') as f:  # Skip the leading '/'
                content = f.read()

            # 4. Create the HTTP response
            response = 'HTTP/1.1 200 OK\r\n\r\n'
            response += content

            # 5. Send the content of the file to the socket
            connectionSocket.send(response.encode())

        except IOError:
            # Handle file not found error
            error_response = "HTTP/1.1 404 Not Found\r\n\r\n"
            error_response += "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n"
            connectionSocket.send(error_response.encode())

        except Exception as e:
            print(f"Error handling request: {e}")

        finally:
            # Close the connection socket
            connectionSocket.close()

class Proxy(NetworkApplication):

    def __init__(self, args):
        print('Web Proxy starting on port: %i...' % (args.port))

        # 1. Initialise instance variables
        self.port = args.port
        self.cache_dir = "cache"
        self.cache_index = dict()
        self.lock = threading.Lock()

        # 2. Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

        # 3. Create a socket (TCP)
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 4. Bind the socket to server address and port
        serverSocket.bind(("", self.port))
        
        # 5. Keep listening for connections
        serverSocket.listen(100)

        # 6. Use threads to handle multiple requests
        while True:
            connectionSocket, addr = serverSocket.accept()
            threading.Thread(target=self.handle_client, args=(connectionSocket,)).start()

    def handle_client(self, connectionSocket):
        try:
            # 1. Receive request from client
            request = connectionSocket.recv(MAX_DATA_RECV)
            if not request:
                return

            try:
                decoded = request.decode()
            except UnicodeDecodeError:
                self.send_error(connectionSocket, "400 Bad Request")
                return

            # 2. Parse HTTP request line and headers
            parsed = self.parse_request(decoded)
            if parsed is None:
                self.send_error(connectionSocket, "400 Bad Request")
                return

            host, port, path, headers = parsed
            print(f"Proxy request: {host}:{port}{path}")
            cache_key = f"{host}:{port}{path}"

            # 3. Serve from cache if available
            if self.serve_from_cache(cache_key, connectionSocket):
                return

            # 4. Loop protection
            if (host == "localhost" or host == "127.0.0.1") and port == self.port:
                self.send_error(connectionSocket, "502 Bad Gateway")
                return

            # 4. Forward to origin server
            response = self.fetch_from_server(host, port, path, headers)
            if response is None:
                self.send_error(connectionSocket, "502 Bad Gateway")
                return

            # 5. Send response to client and cache it
            connectionSocket.sendall(response)
            self.store_in_cache(cache_key, response)

        except Exception as e:
            print(f"Proxy error: {e}")
            try:
                self.send_error(connectionSocket, "500 Internal Server Error")
            except Exception:
                pass
        finally:
            connectionSocket.close()

    def parse_request(self, message):
        lines = message.split('\r\n')
        if len(lines) < 1:
            return None

        # 1. Parse request line
        request_line = lines[0]
        parts = request_line.split()
        if len(parts) < 3 or parts[0] != 'GET':
            return None

        url = parts[1]
        # 2. Collect headers
        header_lines = []
        for line in lines[1:]:
            if line == '':
                break
            header_lines.append(line)

        host_header = None
        for line in header_lines:
            if line.lower().startswith("host:"):
                host_header = line.split(":", 1)[1].strip()
                break

        # 3. Extract host, port and path
        if url.startswith("http://"):
            remainder = url[7:]
            if "/" in remainder:
                host_port, path_part = remainder.split("/", 1)
                path = "/" + path_part
            else:
                host_port = remainder
                path = "/"
        else:
            if host_header is None:
                return None
            host_port = host_header
            path = url

        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                return None
        else:
            host = host_port
            port = 80

        return host, port, path, header_lines

    def build_forward_request(self, host, path, headers):
        # 1. Filter headers and ensure Host is present
        filtered_headers = []
        has_host = False
        for header in headers:
            if header.lower().startswith("proxy-connection"):
                continue
            if header.lower().startswith("host:"):
                has_host = True
            filtered_headers.append(header)

        if not has_host:
            filtered_headers.append(f"Host: {host}")

        # 2. Build HTTP/1.1 GET request to origin
        request_line = f"GET {path} HTTP/1.1"
        forward = request_line + "\r\n" + "\r\n".join(filtered_headers) + "\r\n\r\n"
        return forward.encode()

    def fetch_from_server(self, host, port, path, headers):
        try:
            # 1. Forward request to origin server
            forward_request = self.build_forward_request(host, path, headers)
            serverSocket = socket.create_connection((host, port), timeout=10)
            serverSocket.settimeout(10)  # Explicitly set timeout for recv() operations
            try:
                serverSocket.sendall(forward_request)
                # 2. Receive full response
                response_chunks = []
                while True:
                    try:
                        data = serverSocket.recv(MAX_DATA_RECV)
                        if not data:
                            break
                        response_chunks.append(data)
                    except socket.timeout:
                        # Timeout on recv is expected when no more data is available
                        break
                return b"".join(response_chunks)
            finally:
                serverSocket.close()
        except Exception as e:
            print(f"Error fetching from server {host}:{port}{path} - {e}")
            return None

    def cache_path(self, cache_key):
        safe_name = str(abs(hash(cache_key)))
        return os.path.join(self.cache_dir, safe_name)

    def serve_from_cache(self, cache_key, connectionSocket):
        with self.lock:
            cache_file = self.cache_index.get(cache_key)
        if cache_file and os.path.exists(cache_file):
            try:
                # 1. Read cached response from disk
                with open(cache_file, "rb") as f:
                    data = f.read()
                # 2. Send cached response
                connectionSocket.sendall(data)
                return True
            except Exception as e:
                print(f"Error reading cache: {e}")
        return False

    def store_in_cache(self, cache_key, data):
        cache_file = self.cache_path(cache_key)
        try:
            # 1. Write response to cache file
            with open(cache_file, "wb") as f:
                f.write(data)
            # 2. Update in-memory index
            with self.lock:
                self.cache_index[cache_key] = cache_file
        except Exception as e:
            print(f"Error writing cache: {e}")

    def send_error(self, connectionSocket, status_line):
        error_response = f"HTTP/1.1 {status_line}\r\n\r\n"
        connectionSocket.sendall(error_response.encode())
            

# NOTE: Do NOT delete the code below
if __name__ == "__main__":
        
    args = setupArgumentParser()
    args.func(args)
