// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <iostream>
#include <fstream>
#include <chrono>
#include <thread>
#include <fcntl.h>
#include <unistd.h>
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/Controller.hpp"

constexpr unsigned int kBaudRate = 115200;


int main() {
  Controller cc("/dev/ttyGS0", kBaudRate, true);
  // Controller cc("/tmp/virt2", kBaudRate, true);

  if (!cc.init_device()) {
    std::cout << "Failed to init device!\n";
    return 1;
  }

  int x, y;
  auto last_detection = std::chrono::steady_clock::now();
  int fd = open("/tmp/rura", O_RDONLY | O_NONBLOCK);
  FILE* file = fdopen(fd, "r");

  while (true) {
    int ret = fscanf(file, "%d %d", &x, &y);

    if (ret == 2) {
      cc.new_detection(x, y);
      last_detection = std::chrono::steady_clock::now();
    }
    else {
      clearerr(file);
      auto now = std::chrono::steady_clock::now();
      
      if (now - last_detection >= std::chrono::seconds(5)) {
        std::cout << "No detections for 5 seconds" << std::endl;
        std::cout << "Switching to GPS" << std::endl;
        last_detection = now;
        }
    }
  }

  fclose(file);
  return 0;
}
