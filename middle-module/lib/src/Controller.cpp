// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <iostream>
#include <string>
#include <cmath>
#include <memory>
#include <numbers>
#include <boost/geometry.hpp>
#include "sowa-lib/Controller.hpp"
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/helpers.hpp"

constexpr float rad2deg = (180.0)/std::numbers::pi;

constexpr float h_scaling = (1920.0/8192.0 * 360.0) / 1920.0;
constexpr float v_scaling = (1080.0/4096.0 * 180.0)/1080.0;

constexpr float kMoveThreshold = 0.2;

using boost::geometry::model::d2::point_xy;
using std::string;


Controller::Controller(std::string dev, const unsigned int baudRate)
  : serial(std::make_unique<Serial>(dev, baudRate))
  , testing_mode(false)
  , device_coordinates({0, 0, 0}) {}

Controller::Controller(std::string dev, const unsigned int baudRate, bool t)
  : serial(std::make_unique<Serial>(dev, baudRate))
  , testing_mode(t)
  , device_coordinates({0, 0, 0}) {}


bool Controller::init_device() const {
  if (testing_mode) {
    return true;
  }

  packet_t p {
    kHeader,
    name::restart_esp,
    0,
    0,
    0.0
  };

  calculate_checksum(&p);
  serial->send(p);

  serial->receive(&p);                // wait for a response

  if (check_checksum(p) && p.name == name::esp_ok) {
    std::cout << "Esp is ready !" << std::endl;
    return true;
  }
  return false;
}

void Controller::new_move(direction dir, float deg) const {
  packet_t pack {
    kHeader,
    name::move,
    dir,
    0,
    deg
  };

  calculate_checksum(&pack);

  serial->send(pack);
}

void Controller::new_detection(int x, int y) {
  float degrees_x = abs(static_cast<float>(x * h_scaling));
  float degrees_y = abs(static_cast<float>(y * v_scaling));

  if (std::sqrt(degrees_x * degrees_x +
    degrees_y * degrees_y) < kMoveThreshold) {
    return;
  }

  new_move(x > 0 ? direction::right : direction::left, degrees_x);
  new_move(y > 0 ? direction::up : direction::down, degrees_y);
}

void Controller::new_gps_data(float lat, float lon, float alt) const {
  float dX = lat - this->device_coordinates.a[0];
  float dY = lon - this->device_coordinates.a[1];
  float dZ = alt - this->device_coordinates.a[2];

  float yaw = std::atan2(dX, dZ) * rad2deg;
  float pitch = std::atan2(dY, std::sqrt(dZ * dZ + dX * dX)) * rad2deg;

  new_move(dX > 0 ? direction::right : direction::left, yaw);
  new_move(dY > 0 ? direction::up : direction::down, pitch);
}