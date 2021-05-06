# Simulations

Using [netem (via tc)](https://wiki.linuxfoundation.org/networking/netem) to do network faliure simulations.

Every simulation scenario has a reset:

```
$> tc qdisc | grep eth0
qdisc mq 0: dev eth0 root
qdisc pfifo_fast 0: dev eth0 parent :8 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :7 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :6 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :5 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :4 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :3 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :2 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
qdisc pfifo_fast 0: dev eth0 parent :1 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
```

## Cluster Status

192.168.0.232 - 192.168.0.236
- 2 Prometheus (232, 233)
- 3 AlertManager (232, 233, 234)

## Single Route Faliures

### Non-Prometheus Node

192.168.0.235 -> 192.168.0.234 high latency (~50ms):

```bash
# @192.168.0.235
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem delay 50ms
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.235, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Result:
- NodeOutLatencyCount: 2 alerts 
    - 192.168.0.234 - 1
    - 192.168.0.235 - 1
- NodeInLatencyCount: 2 alerts
    - 192.168.0.234 - 1
    - 192.168.0.235 - 1
- RouteLatency: 2 alerts 
    - 192.168.0.234 -> 192.168.0.235
    - 192.168.0.235 -> 192.168.0.234
> Can detect & alert

192.168.0.235 -> 192.168.0.234 high loss (~25%):

```bash
# @192.168.0.235
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 25%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.235, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Result:
- NodeOutLatencyCount: 1 alerts 
    - 192.168.0.235 - 1
- NodeInLatencyCount: 1 alerts
    - 192.168.0.235 - 1
- NodeOutLatencyAvg: 1 alerts 
    - 192.168.0.235 - 33.81ms 
- NodeInLatencyAvg: 1 alerts
    - 192.168.0.234 - 33.73ms 
- RouteLatency: 1 alerts 
    - 192.168.0.234 -> 192.168.0.235 - 100.6ms
> Can detect & alert

### Prometheus Node

192.168.0.233 -> 192.168.0.234 high latency (~50ms):

```bash
# @192.168.0.233
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem delay 50ms
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.233, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Result:
- NodeOutLatencyCount: 2 alerts 
    - 192.168.0.234 - 1
    - 192.168.0.233 - 1
- NodeInLatencyCount: 2 alerts
    - 192.168.0.234 - 1
    - 192.168.0.233 - 1
- RouteLatency: 2 alerts 
    - 192.168.0.234 -> 192.168.0.233 - 50.39ms 
    - 192.168.0.233 -> 192.168.0.234 - 50.43ms 
> Can detect & alert

192.168.0.233 -> 192.168.0.234 high loss (~25%):

```bash
# @192.168.0.233
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 25%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.233, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Result:
- ProbeLatencyAvg: 12.11ms
- NodeOutLatencyCount: 2 alerts 
    - 192.168.0.233 - 1
    - 192.168.0.234 - 1
- NodeInLatencyCount: 1 alerts
    - 192.168.0.233 - 1
    - 192.168.0.234 - 1
- NodeOutLatencyAvg: 1 alerts 
    - 192.168.0.233 - 33.73ms 
    - 192.168.0.234 - 42.05ms 
- NodeInLatencyAvg: 1 alerts
    - 192.168.0.234 - 33.75ms
    - 192.168.0.233 - 42.05ms 
- RouteLatency: 1 alerts 
    - 192.168.0.234 -> 192.168.0.233 - 222.7ms 
    - 192.168.0.233 -> 192.168.0.234 - 150.3ms
> Still can detect, with increased percived route latency

## Single Node Faliures

### Non-Prometheus Node

192.168.0.235 high latency (~50ms):

```bash
# @192.168.0.235
tc qdisc add dev eth0 root netem delay 50ms

# @192.168.0.235, reset
tc qdisc del dev eth0 root

```

Result:
- ProbeLatencyAvg: 14.27ms
- ProbeLatencyCount: 27.78%
- NodeOutLatencyCount: 6 alerts 
    - 192.168.0.235 - 5
    - 192.168.0.*** - 1
- NodeInLatencyCount: 2 alerts
    - 192.168.0.235 - 5
    - 192.168.0.*** - 1
- NodeOutLatencyAvg: 1 alerts
    - 42.12ms 
- NodeInLatencyAvg: 1 alerts
    - 42.13ms 
- RouteLatency: 10 alerts 
    - 192.168.0.*** -> 192.168.0.235 - ~200ms
    - 192.168.0.235 -> 192.168.0.*** - ~50ms
> Can detect & alert

192.168.0.235 -> 192.168.0.234 high loss (~25%):

```bash
# @192.168.0.235
tc qdisc add dev eth0 root netem loss 25%

# @192.168.0.235, reset
tc qdisc del dev eth0 root

```

Result:
- ProbeFailed: 8.333%
- ProbeLatencyAvg: 14.27ms
- ProbeLatencyCount: 27.78%
- NodeOutLatencyCount: 6 alerts 
    - 192.168.0.235 - 5
    - 192.168.0.*** - 1
- NodeInLatencyCount: 6 alerts
    - 192.168.0.235 - 5
    - 192.168.0.*** - 1
- NodeOutLatencyAvg: 6 alerts
    - 192.168.0.235 103.2ms 
    - 192.168.0.*** 17.03ms
- NodeInLatencyAvg: 6 alerts
    - 192.168.0.235 112.5ms  
    - 192.168.0.*** 25.35ms
- RouteLatency: 10 alerts 
    - 192.168.0.*** -> 192.168.0.235 - ~200ms
    - 192.168.0.235 -> 192.168.0.*** - ~50ms
> Can detect & alert

### Prometheus Node

192.168.0.233 high latency (~50ms):

```bash
# @192.168.0.233
tc qdisc add dev eth0 root netem delay 50ms

# @192.168.0.233, reset
tc qdisc del dev eth0 root

```

Result:
- ProbeLatencyAvg: 14.26ms
- ProbeLatencyCount: 27.78%
- NodeOutLatencyCount: 6 alerts 
    - 192.168.0.233 - 5
    - 192.168.0.*** - 1
- NodeInLatencyCount: 2 alerts
    - 192.168.0.233 - 5
    - 192.168.0.*** - 1
- NodeOutLatencyAvg: 1 alerts
    - 42.05ms  
- NodeInLatencyAvg: 1 alerts
    - 42.04ms  
- RouteLatency: 10 alerts 
    - 192.168.0.*** -> 192.168.0.233 - ~200ms
    - 192.168.0.233 -> 192.168.0.*** - ~50ms
> Can detect & alert

192.168.0.233 -> 192.168.0.234 high loss (~25%):

```bash
# @192.168.0.233
tc qdisc add dev eth0 root netem loss 25%

# @192.168.0.233, reset
tc qdisc del dev eth0 root

```

Result:
- ProbeFailed: 5.556%
- ProbeLatencyAvg: 44.20ms
- ProbeLatencyCount: 27.78%
- NodeOutLatencyCount: 6 alerts 
    - 192.168.0.233 - 5
    - 192.168.0.*** - 1
- NodeInLatencyCount: 6 alerts
    - 192.168.0.233 - 5
    - 192.168.0.*** - 1
- NodeOutLatencyAvg: 6 alerts
    - 192.168.0.233 142.1ms  
    - 192.168.0.*** 17.03ms
- NodeInLatencyAvg: 6 alerts
    - 192.168.0.233 102.2ms   
    - 192.168.0.*** 17.11ms
- RouteLatency: 10 alerts 
    - 192.168.0.*** -> 192.168.0.233 - ~200ms
    - 192.168.0.233 -> 192.168.0.*** - ~50ms
> Can detect & alert

## Network Partition

### Single Link Partition, Non-Prometheus Node

192.168.0.235 <-> 192.168.0.234 partition (100% loss):

```bash
# @192.168.0.235
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.235, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

- ProbeFailed: 5.556%
- ProbeLatencyAvg: 28.16ms
- NodeProbeFailed: 2 alerts
    - 192.168.0.235 - 1
    - 192.168.0.234 - 1
- RouteLatency: 2 alerts
    - 192.168.0.234 -> 192.168.0.235 - 500.6ms (timeout)
    - 192.168.0.235 -> 192.168.0.234 - 500.5ms (timeout)
- NodeInLatencyAvg: 2 alerts
- NodeInLatencyCount: 2 alerts
- NodeOutLatencyAvg: 2 alerts
- NodeOutLatencyCount: 2 alerts
> Can detect & alert

### Single Link Partition, Prometheus Node

192.168.0.233 <-> 192.168.0.234 partition (100% loss):

```bash
# @192.168.0.233
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.233, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

- ProbeFailed: 5.556%
- ProbeLatencyAvg: 17.05ms
- ProbeTargetDown: 16.67%
- NodeProbeFailed: 2 alerts
    - 192.168.0.233 - 1
    - 192.168.0.234 - 1
- RouteLatency: 2 alerts
    - 192.168.0.234 -> 192.168.0.233 - 500.8ms (timeout)
    - 192.168.0.233 -> 192.168.0.234 - 500.3ms (timeout)
- NodeInLatencyAvg: 2 alerts
- NodeInLatencyCount: 2 alerts
- NodeOutLatencyAvg: 2 alerts
- NodeOutLatencyCount: 2 alerts
> Detect

### Complete Network Partition, Prometheus Available in Partition

Partition: 232, 234, 236 | 233, 235

100% Loss Routes:
- 233-232, 233-234, 233-236
- 235-232, 235-234, 235-236

```bash
# @192.168.0.233
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.232 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.236 flowid 1:3

# @192.168.0.235
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.232 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.236 flowid 1:3

# @192.168.0.233, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

# @192.168.0.235, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Result: (AlertManager@192.168.0.233)
- AlertManager not synchornized
- ProbeTargetDown: 50%
- ProbeFailed: 33.33%
- NodeProbeFailed:
    - 192.168.0.232 - 2
    - 192.168.0.234 - 2
    - 192.168.0.236 - 2
> Clearly shows network partition

### Complete Network Partition, Prometheus Not Available in Partition

Partition: 232, 233, 234 | 235, 236

100% Loss Routes:
- 235-232, 235-233, 235-234
- 236-232, 236-233, 236-234

```bash
# @192.168.0.235
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.232 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.233 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.236
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.232 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.233 flowid 1:3
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.235, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

# @192.168.0.236, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Result: (AlertManager@192.168.0.233)
- ProbeTargetDown: 16.67%
- ProbeFailed: 6.667%
- NodeProbeFailed:
    - 192.168.0.235 - 3
    - 192.168.0.236 - 3
> Clearly shows network partition
