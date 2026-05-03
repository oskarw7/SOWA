// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <memory>
#include <string>
#include "sowa-lib/Serial.hpp"
#include <boost/qvm/all.hpp>
#include <boost/geometry.hpp>

using boost::qvm::vec;


class Controller {
 private:
  std::unique_ptr<Serial> serial;
  bool testing_mode;
  vec<float, 3> device_coordinates;
  void new_move(direction dir, float deg) const;

 public:
  Controller(std::string dev, const unsigned int baudRate);
  Controller(std::string dev, const unsigned int baudRate, bool t);

  bool init_device() const;
  void new_detection(int x, int y);
  void new_gps_data(float lat, float lon, float alt) const;
};
