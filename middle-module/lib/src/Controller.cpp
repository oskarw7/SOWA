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
#include "Controller.h"
#include "Serial.h"
#include "Helpers.h"
#include <boost/random/linear_congruential.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <boost/generator_iterator.hpp>

constexpr float h_scaling = 116.0/1920.0;
constexpr float v_scaling = 65.0/1080.0;

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

void calculate_checksum(packet* p) {
  p->checksum = p->additional ^ p->header ^ p->name;
  for (int i = 0; i < 4; i++) {
    p->checksum ^= (p->value && 0b1111111 << 8 * i);
  }
}

void Controller::new_move(int x, int y) {
  point_xy<int> new_point(x, y);

  point_xy<int> target_vec(abs(x - this->previous_point.x()),
                      abs(y - this->previous_point.y()));

  float target_steps_x = static_cast<float>(target_vec.x() * h_scaling);
  float target_steps_y = static_cast<float>(target_vec.y() * v_scaling);

  bool h_dir = target_vec.x() > 0;
  bool v_dir = target_vec.y() > 0;

  if (!testing_mode) {
    packet h_pack {
      target_steps_x,
      kHeader,
      name::move,
      h_dir ? direction::right : direction::left
    };

    packet v_pack {
      target_steps_y,
      kHeader,
      name::move,
      v_dir ? direction::up : direction::down
    };

    calculate_checksum(&h_pack);
    calculate_checksum(&v_pack);

    serial->send(h_pack);
    serial->send(v_pack);
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
