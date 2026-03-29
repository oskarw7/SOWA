// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "Serial.h"
#include <vector>
#include <boost/lexical_cast.hpp>

constexpr unsigned int kBaudRate = 115200;

using boost::lexical_cast;
using boost::bad_lexical_cast;

struct point_t {
  int x;
  int y;
} point;

std::string trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\n");
    size_t end = str.find_last_not_of(" \t\n");

    if (start == std::string::npos) {
        return "";  // String is all whitespace
    }

    return str.substr(start, end - start + 1);
}

int main() {
  std::vector<point_t> coordinates = {
    {953, 336},
    {-1000, 0},
    {0, -400},
    {1000, 0}
  };

  const float h_scaling = 116.0/1920.0; 
  const float v_scaling = 65.0/1080.0; 


  Serial serial("/dev/ttyACM0", kBaudRate);
  ba::streambuf buf;

  sleep(2);

  serial.write("reset_pos");
  sleep(1);

  for (auto p : coordinates) {
    std::cout << "move "+ lexical_cast<std::string>(p.x * h_scaling) + " right\n" << std::endl;
    std::cout << "move "+ lexical_cast<std::string>(p.y * v_scaling) + " up\n" << std::endl;
    
    serial.write("move "+ lexical_cast<std::string>(p.y * v_scaling) + " up\n");
    serial.write("move "+ lexical_cast<std::string>(p.x * h_scaling) + " right\n");
    sleep(1);
  }

  serial.write("stop both");

  return 0;
}