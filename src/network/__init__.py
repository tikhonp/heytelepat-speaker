"""
Provides network checking and wireless connection for raspberrypi

Connection to network with this instruction:
    https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

Network - Adding, deleting and connecting wireless network
check_connection_ping - Check connection with request to server
check_connection_get_request - Check connection with ping to server
"""

from network.network import Network, check_connection_ping, check_connection_get_request
