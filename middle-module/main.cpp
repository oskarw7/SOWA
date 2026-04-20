// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <iostream>
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/Controller.hpp"

constexpr unsigned int kBaudRate = 115200;

int main() {
  // Controller cc("/dev/ttyACM0", kBaudRate);
  // Controller cc("/tmp/virt", kBaudRate);
  Controller cc(true);

  if (cc.init_device()) {
    cc.new_move(123, 123);
    cc.new_move(126, 124);
    cc.new_move(-123, 0);
  } else {
    std::cout << "Failed to init the device!" << std::endl;
  }

  return 0;
}
