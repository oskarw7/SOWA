// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "Serial.h"
#include "Controller.h"

constexpr unsigned int kBaudRate = 115200;

int main() {
  // Controller cc("/dev/ttyUSB0", kBaudRate);
  Controller cc(true);

  cc.new_move(100, 100);
  cc.new_move(0, 0);
  cc.new_move(100, 100);


  return 0;
}
