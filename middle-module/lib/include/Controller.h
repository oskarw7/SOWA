// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include "Serial.h"
#include <boost/geometry/geometries/point_xy.hpp>
#include <boost/geometry.hpp>

using boost::geometry::model::d2::point_xy;

class Controller {
 private:
  Serial serial;
  point_xy<int> previous_point;

 public:
  Controller();

  void new_move(int x, int y);
};
