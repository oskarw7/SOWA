// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <iostream>
#include <fstream>
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/Controller.hpp"

constexpr unsigned int kBaudRate = 115200;

std::ifstream pipeFromDetection("/tmp/rura");

int main() {
  Controller cc("/dev/ttyGS0", kBaudRate, true);
  // Controller cc("/tmp/virt2", kBaudRate, true);
  
  if (cc.init_device()) {
    int x, y;
    while (true) {
      pipeFromDetection >> x >> y;
      cc.new_detection(x, y);
    }
  } else {
    std::cout << "Failed to init the device!" << std::endl;
  }

  return 0;
}
