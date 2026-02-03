package main

import (
	"fmt"
	"os"
	"time"
)

func main() {
	host, _ := os.Hostname()
	fmt.Printf("hello-go ✅ host=%s ts=%s\n", host, time.Now().Format(time.RFC3339Nano))
}
