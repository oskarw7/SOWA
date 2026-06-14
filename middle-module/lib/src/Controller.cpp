// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "sowa-lib/Controller.hpp"

#include <boost/geometry.hpp>
#include <cmath>
#include <iostream>
#include <memory>
#include <numbers>
#include <string>

#include "sowa-lib/Serial.hpp"
#include "sowa-lib/helpers.hpp"

constexpr float kHScaling = 44.0/3840; // (1920.0 / 8192.0 * 360.0) / 1920.0;
constexpr float KVScaling = 25.0/2160; // (1080.0 / (4096.0 - 1080) * 180.0) / 1080.0;

constexpr float kHMoveThreshold = 0.5;
constexpr float kVMoveThreshold = 1.5;

constexpr float kRad2deg = 180.0 / std::numbers::pi;
constexpr float kDeg2rad = std::numbers::pi / 180.0;

using boost::geometry::model::d2::point_xy;
using std::string;

Controller::Controller(std::string dev, const unsigned int baudRate)
    : serial(std::make_unique<Serial>(dev, baudRate)),
      testing_mode(false),
      device_coordinates({51, 51, 0}) {}

Controller::Controller(std::string dev, const unsigned int baudRate, bool t)
    : serial(std::make_unique<Serial>(dev, baudRate)),
      testing_mode(t),
      device_coordinates({54.412778, 18.604617, 0}) {}

bool Controller::init_device() const {
  if (testing_mode) {
    return true;
  }

  packet_t p{kHeader, name::restart_esp, 0, 0, 0.0};
  serial->send(p);

  serial->receive(&p);  // wait for a response

  if (check_checksum(p) && p.name == name::esp_ok) {
    std::cout << "Esp is ready !" << std::endl;
    return true;
  }
  return false;
}

void Controller::new_move(direction dir, float deg) const {
  if (((dir == direction::up || dir == direction::down) &&
       deg <= kVMoveThreshold) ||
      ((dir == direction::right || dir == direction::left) &&
       deg <= kHMoveThreshold)) {
    return;
  }
  std::cout << "ruszam sie" << std::endl;

  packet_t pack{kHeader, name::move, dir, 0, deg};
  serial->send(pack);
}

void Controller::new_detection(int x, int y) const {
  float degrees_x = abs(static_cast<float>(x * kHScaling));
  float degrees_y = abs(static_cast<float>(y * KVScaling));

  new_move(x > 0 ? direction::right : direction::left, degrees_x);
  new_move(y > 0 ? direction::up : direction::down, degrees_y);
}

void Controller::new_gps_data(float lat, float lon, float alt) const {
  float dX = (lat - this->device_coordinates.a[0]) * 111139.0;
  float dY = (lon - this->device_coordinates.a[1]) * 111320.0 *
             std::cos(lat * kDeg2rad);
  float dZ = alt - this->device_coordinates.a[2];

  packet_t pack{kHeader, name::get_current_pos, axis::both, 0, 0};
  serial->send(pack);

  packet_t response[2];
  serial->receive(&response[0]);
  serial->receive(&response[1]);

  float yaw = std::atan2(dY, dX) * kRad2deg - response[0].value;
  float pitch = std::atan2(dZ, std::sqrt(dX * dX + dY * dY)) * kRad2deg -
                response[1].value;

  new_move(yaw > 0 ? direction::right : direction::left, std::abs(yaw));
  new_move(pitch > 0 ? direction::up : direction::down, std::abs(pitch));
}
