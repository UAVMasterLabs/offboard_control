#!/usr/bin/env sh
raspivid -o - -vf -hf -t 0 | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=greta.local port=5000
