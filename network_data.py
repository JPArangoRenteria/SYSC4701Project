import os
import time
import csv
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController  # Changed from default Controller
from mininet.cli import CLI
from mininet.util import dumpNodeConnections

class SimpleTopo(Topo):
    def build(self):
        # Create two hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        # Create a switch
        s1 = self.addSwitch('s1')
        
        # Add links between the switch and the hosts
        self.addLink(h1, s1)
        self.addLink(h2, s1)

def start_packet_capture(net):
    """Start packet capture using tcpdump on host interfaces."""
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Capture traffic on the interfaces of h1 and h2
    os.system(f"sudo tcpdump -i {h1.name}-eth0 -w /tmp/h1_traffic.pcap &")
    os.system(f"sudo tcpdump -i {h2.name}-eth0 -w /tmp/h2_traffic.pcap &")
    
def stop_packet_capture():
    """Stop tcpdump capture."""
    os.system("sudo pkill tcpdump")

def analyze_traffic_and_save_metrics():
    """Analyze the captured packets and generate some simple metrics, then save to CSV."""
    import pyshark
    # Path to captured pcap files for h1 and h2
    h1_pcap = '/tmp/h1_traffic.pcap'
    h2_pcap = '/tmp/h2_traffic.pcap'
    
    # Analyze the captured pcap files for h1 and h2 using pyshark
    h1_capture = pyshark.FileCapture(h1_pcap)
    h2_capture = pyshark.FileCapture(h2_pcap)
    
    # Metrics calculation: packet count and byte count
    h1_packet_count = len(list(h1_capture))
    h2_packet_count = len(list(h2_capture))
    
    h1_byte_count = sum([int(pkt.length) for pkt in h1_capture])
    h2_byte_count = sum([int(pkt.length) for pkt in h2_capture])
    
    # Create a CSV file and write the metrics
    with open('network_metrics.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Host', 'Packet Count', 'Byte Count'])
        
        # Write metrics for each host
        writer.writerow(['h1', h1_packet_count, h1_byte_count])
        writer.writerow(['h2', h2_packet_count, h2_byte_count])
    print("Metrics saved to 'network_metrics.csv'")

if __name__ == '__main__':
    # Create the network with the OVS controller
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=OVSController)
    
    # Start the network
    net.start()
    
    # Start capturing traffic
    start_packet_capture(net)
    
    # Run a simple test (ping)
    print("Starting network traffic...")
    time.sleep(2)
    net.get('h1').cmd("ping -c 4 10.0.0.2")  # Ping h2 from h1
    time.sleep(2)
    
    # Stop traffic capture
    stop_packet_capture()
    
    # Analyze the captured traffic and save the metrics to CSV
    analyze_traffic_and_save_metrics()
    
    # Launch the CLI for interaction
    CLI(net)
    
    # Stop the network
    net.stop()
