#!/usr/bin/env bash

base_port=61000
base_ip='10.18.242.'
start_ip=2
ports_length=254

egrep "^net.ipv4.ip_local_reserved_ports.*$base_port.*$((base_port + ports_length))" /etc/sysctl.conf 1>/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "system has reserve the ports $((base_port)),$((base_port + ports_length))"
else
  echo "the ports are not reserved, will fix this"
  sed '/^net.ipv4.ip_local_reserved_ports/{s/^/# &/;s/$/& # commented by lab_lxc_manager/}' /etc/sysctl.conf 1>/dev/null 2>&1 -i
  echo "net.ipv4.ip_local_reserved_ports = $base_port,$((base_port + ports_length))" >> /etc/sysctl.conf
  echo "system has not reserve the ports $base_port , $((base_port + ports_length)), i will try fix this"
fi
sudo sysctl -p

for ((i=0; i<ports_length; i++))
do
  iptables -t nat -I PREROUTING -p tcp --dport $((i + base_port)) -j DNAT --to $base_ip$((i + start_ip)):22
done
echo "done!"
