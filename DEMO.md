# Live Demo

Port forwards:

```bash
kubectl apply -f /root/microservices-demo/release/

kubectl port-forward pod/alertmanager-main-1 -n monitoring 9093:9093
kubectl port-forward pod/prometheus-k8s-0 -n monitoring 9090:9090
kubectl port-forward svc/locust 8089:8089
kubectl port-forward svc/frontend 8080:80

```

Links:
- [AlertManager](http://localhost:9093/#/alerts?silenced=false&inhibited=false&active=true&filter=%7Bnamespace%3D%22monitoring%22%7D)
- [Prometheus Alerts](http://localhost:9090/alerts)
- [Prometheus Graph](http://localhost:9090/graph?g0.expr=probe_duration_seconds&g0.tab=0&g0.stacked=0&g0.range_input=5m)
- [Locust](http://localhost:8089/)
- [Demo page](http://localhost:8080/)

```bash
# Login
ssh 192.168.0.235

# @192.168.0.235
tc qdisc add dev eth0 root handle 1: prio
tc qdisc add dev eth0 parent 1:3 handle 30: netem delay 50ms
tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst 192.168.0.234 flowid 1:3

# @192.168.0.235, reset
tc qdisc del dev eth0 parent 1:3
tc qdisc del dev eth0 root

```

Cleanup:

```bash
kubectl delete -f /root/microservices-demo/release
```