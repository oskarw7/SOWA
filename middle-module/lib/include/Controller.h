// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <memory>
#include <string>
#include "Serial.h"
#include <boost/geometry/geometries/point_xy.hpp>
#include <boost/geometry.hpp>

using boost::geometry::model::d2::point_xy;

class Controller {
 private:
  std::unique_ptr<Serial> serial;
  point_xy<int> previous_point;
  bool testing_mode;

 public:
  Controller(std::string dev, const unsigned int baudRate);
  explicit Controller(bool t);

  void new_move(int x, int y);
};
