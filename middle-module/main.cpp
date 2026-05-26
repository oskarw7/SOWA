// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <cpr/cpr.h>
#include <fcntl.h>
#include <unistd.h>

#include <boost/lexical_cast.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>

#include "sowa-lib/Controller.hpp"
#include "sowa-lib/Serial.hpp"

constexpr unsigned int kBaudRate = 115200;

using boost::lexical_cast;
using std::chrono::steady_clock;

int main() {
  // Controller controller("/dev/ttyGS0", kBaudRate, true);
  Controller controller("/tmp/virt2", kBaudRate,true);

  std::this_thread::sleep_for(std::chrono::seconds(2));  // wait for parser init

  

  if (!controller.init_device()) {
    std::cout << "Failed to init device!\n";
    return 1;
  }

  std::this_thread::sleep_for(
      std::chrono::milliseconds(20000));  // wait for gniazdo init

  int x, y;

  bool using_gps = false;
  cpr::Response response;

  auto last_detection = steady_clock::now();
  int fd = open("/tmp/rura", O_RDONLY | O_NONBLOCK);
  FILE* file = fdopen(fd, "r");

  int cntr = 0;

  while (true) {
    // TESTING PURPOSES ONLY
    cntr++;
    if (cntr == 3554889) {
      controller.new_detection(1900, 0);
      std::this_thread::sleep_for(std::chrono::milliseconds(3000));
    }

    int ret = fscanf(file, "%d %d", &x, &y);

    if (ret == 2 && (y != (-1))) {
      controller.new_detection(x, y);

      last_detection = steady_clock::now();
      using_gps = false;
    } else {
      clearerr(file);
      auto now = steady_clock::now();

      if (now - last_detection >= std::chrono::seconds(5) && !using_gps) {
        std::cout << "Switching to GPS" << std::endl;

        using_gps = true;
        last_detection = now;
      }
    }
    if (using_gps) {
      std::this_thread::sleep_for(std::chrono::milliseconds(1000));
      response = cpr::Get(cpr::Url{"http://127.0.0.1:8080"});

      if (response.status_code == 200) {
        float lat = lexical_cast<float>(response.text.substr(14, 2)) +
                    lexical_cast<float>(response.text.substr(16, 7)) / 60.0;
        if (response.text.substr(24, 1) == "S") {
          lat *= -1.0;
        }

        float lon = lexical_cast<float>(response.text.substr(26, 3)) +
                    lexical_cast<float>(response.text.substr(29, 7)) / 60.0;
        if (response.text.substr(37, 1) == "W") {
          lon *= -1.0;
        }

        controller.new_gps_data(
            lat, lon, lexical_cast<float>(response.text.substr(47, 5)));
      }
    }
  }

  fclose(file);
  return 0;
}
