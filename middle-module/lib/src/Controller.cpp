// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include <memory>
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point_xy.hpp>
#include <boost/lexical_cast.hpp>
#include "sowa-lib/Controller.hpp"
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/helpers.hpp"
#include <boost/random/linear_congruential.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <boost/generator_iterator.hpp>

constexpr float h_scaling = 116.0/1920.0;
constexpr float v_scaling = 65.0/1080.0;

constexpr double kMoveThreshold = 0.05;

typedef boost::minstd_rand base_generator_type;

using boost::geometry::model::d2::point_xy;
using boost::lexical_cast;
using std::string;
using std::vector;
using std::endl;
using std::cout;


Controller::Controller(std::string dev, const unsigned int baudRate)
  : serial(std::make_unique<Serial>(dev, baudRate))
  , previous_point(0, 0)
  , testing_mode(false) {}

Controller::Controller(bool t) : previous_point(0, 0), testing_mode(t) {}


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
  cout << "received " << p.name << endl;
  if (check_checksum(p) && p.name == name::esp_ok) {
    cout << "Esp is ready !" << endl;
    return true;
  }
  return false;
}

void Controller::new_move(int x, int y) {
  point_xy<int> new_point(x, y);
  point_xy<int> target_vec(abs(x - this->previous_point.x()),
                      abs(y - this->previous_point.y()));

  float target_steps_x = static_cast<float>(target_vec.x() * h_scaling);
  float target_steps_y = static_cast<float>(target_vec.y() * v_scaling);

  if (std::pow(target_steps_x, 2) +
      std::pow(target_steps_y, 2) < kMoveThreshold) {
    return;
  }

  bool h_dir = target_vec.x() > 0;
  bool v_dir = target_vec.y() > 0;

  if (!testing_mode) {
    packet_t h_pack {
      kHeader,
      name::move,
      h_dir ? direction::right : direction::left,
      0,
      target_steps_x
    };

    packet_t v_pack {
      kHeader,
      name::move,
      v_dir ? direction::up : direction::down,
      0,
      target_steps_y
    };

    calculate_checksum(&h_pack);
    calculate_checksum(&v_pack);

    serial->send(h_pack);
    serial->send(v_pack);

    cout << "packets sent!" << endl;
  } else {
    string h_command =
      string(h_dir ? "right " : "left ") + lexical_cast<string>(target_steps_x);

    string v_command =
      string(v_dir ? "up " : "down ") + lexical_cast<string>(target_steps_y);

    cout << h_command << endl;
    cout << v_command << endl;
  }

  this->previous_point = new_point;
}
