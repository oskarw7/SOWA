// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <iostream>
#include <fstream>
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/Controller.hpp"

constexpr unsigned int kBaudRate = 115200;

std::ifstream zupa("/tmp/rura");

int main() {
  // Controller cc("/dev/ttyACM0", kBaudRate);
  // Controller cc("/tmp/virt2", kBaudRate);
  Controller cc(true);
  std::cout << "zupa" << std::endl;

  int x{0}, y{0};
  int counter =0 ;
  while (true){
  while (zupa >> x >> y) {
    //zupa >> x >> y;
    cc.new_move(x, y);
    std::cout << "MOve: " <<counter++ << std::endl;
  }
  }
  // if (cc.init_device()) {
  //   cc.new_move(123, 123);
  //   cc.new_move(126, 124);
  //   cc.new_move(-123, 0);
  // } else {
  //   std::cout << "Failed to init the device!" << std::endl;
  // }

  return 0;
}
