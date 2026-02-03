package main

import (
	"fmt"
	"os"
)

func help() {
	fmt.Println(`HEE — Human Execution Engine

Core:
  hee help        show this
  hee mark <msg>  write timestamped evidence mark
  hee sig         print node signature
  hee card <name> show a card

Principle:
  small, proven, compounding steps`)
}

func main() {
	if len(os.Args) == 1 || os.Args[1] == "help" {
		help()
		return
	}
	switch os.Args[1] {
	default:
		help()
	}
}
