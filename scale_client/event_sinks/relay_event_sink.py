import socket
from scale_client.network.scale_network_manager import ScaleNetworkManager

import logging
import json

log = logging.getLogger(__name__)

from scale_client.event_sinks.event_sink import EventSink

import socket, asyncore

class AsyncoreClientUDP(asyncore.dispatcher):
    
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.buffer = ""
        
        # Network Connection Magic!
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind( ('', 0) ) # bind to all interfaces and a "random" free port.
        log.debug("Connecting to neighbor node...")
        
    # Once a "connection" is made do this stuff.
    def handle_connect(self):
        log.debug("Connected to neighbor node")
        
    # If a "connection" is closed do this stuff.
    def handle_close(self):
        self.close()
        
    # If a message has arrived, process it.
    def handle_read(self):
        data, addr = self.recv(2048)
        log.debug("Received data:" + data)
        
    # Actually sends the message if there was something in the buffer.
    def handle_write(self):
        if self.buffer != "":
            log.debug("Relay event: " + self.buffer)
            sent = self.sendto(self.buffer, (self.server, self.port))
            self.buffer = self.buffer[sent:]

class RelayEventSink(EventSink, ScaleNetworkManager):
    def __init__(self, broker, relay_port):
        EventSink.__init__(self, broker)
        
        ScaleNetworkManager.__init__(self, broker)

        self.__neighbors = self.get_neighbors()
        self.batman_interface = self.get_batman_interface()
        self.batman_ip = self.get_interface_ip_address(self.batman_interface)
        self.batman_mac = self.get_interface_mac_address(self.batman_interface)
        self.mesh_host_id = self.batman_ip + "_" + self.batman_mac

        #print self.mesh_host_id
        #self.display_neighbors()

        self.__relay_port = relay_port

        self.__neighbor_connections = {}
        self.create_connection_to_neighbors()

    def create_connection_to_neighbors(self):
        for index in self.__neighbors:
            neighbor_ip_address = self.neighbors[index].get_ip_address()
            if neighbor_ip_address:
                self.__neighbor_connections[neighbor_ip_address] = AsyncoreClientUDP(neighbor_ip_address, self.__relay_port)

    def on_start(self):
        # check to see if the current node has any neighbor
        return 
    
    def send(self, encoded_event):
        '''
        Instead of publishing sensed events to MQTT server like MqttEventSink,
        RelayEventSink checks current node's neighbors and forwards the events
        to neighbor nodes if it finds any
        '''

        relay_event = {}
        relay_event['source'] = self.mesh_host_id
        relay_event['event'] = encoded_event
        encoded_relay_event = json.dumps(relay_event)
        
        for index in self.__neighbors:
            neighbor_ip_address = self.neighbors[index].get_ip_address()
            if neighbor_ip_address:
                if self.__neighbor_connections[neighbor_ip_address]:
                    self.__neighbor_connections[neighbor_ip_address].buffer += encoded_relay_event
                    log.info("Forwarded sensed event to neighbor at ip address: " + neighbor_ip_address)

    def check_available(self, event):
        return True
