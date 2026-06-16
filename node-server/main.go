package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	nodeID = flag.String("id", "node1", "Node ID")
	grpcPort = flag.String("grpc-port", "50051", "gRPC port")
	metricsPort = flag.String("metrics-port", "9090", "Prometheus metrics port")

	fsyncDuration = prometheus.NewHistogram(prometheus.HistogramOpts{
		Name:    "fsync_duration_ns",
		Help:    "Duration of fsync calls in nanoseconds",
		Buckets: prometheus.ExponentialBuckets(1000, 2, 20),
	})
)

func init() {
	prometheus.MustRegister(fsyncDuration)
}

func simulateFsync() {
	start := time.Now()
	// Simulate writing to WAL (tmpfs)
	f, err := os.CreateTemp("/wal", "wal-*")
	if err != nil {
		log.Printf("WAL write error: %v", err)
		return
	}
	defer os.Remove(f.Name())
	f.WriteString("raft-log-entry")
	f.Sync() // This is the actual fsync
	f.Close()
	fsyncDuration.Observe(float64(time.Since(start).Nanoseconds()))
}

func main() {
	flag.Parse()
	log.Printf("Starting node %s | gRPC: %s | Metrics: %s", *nodeID, *grpcPort, *metricsPort)

	// Simulate periodic WAL writes (stand-in for real Raft appends)
	go func() {
		for {
			simulateFsync()
			time.Sleep(100 * time.Millisecond)
		}
	}()

	// Expose Prometheus metrics at /metrics
	http.Handle("/metrics", promhttp.Handler())
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "ok")
	})

	addr := fmt.Sprintf(":%s", *metricsPort)
	log.Printf("Metrics available at http://localhost%s/metrics", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}