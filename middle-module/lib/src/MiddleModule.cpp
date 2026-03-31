// ============================================================================
// Copyright 2026 SOWA
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point_xy.hpp>
#include <boost/lexical_cast.hpp>
#include "MiddleModule.h"
#include <boost/random/linear_congruential.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <boost/generator_iterator.hpp>

typedef boost::minstd_rand base_generator_type;

using boost::geometry::model::d2::point_xy;
using boost::lexical_cast;
using boost::bad_lexical_cast;
using std::string;
using std::vector;
using std::endl;
using std::cout;

constexpr unsigned int kBaudRate = 115200;
constexpr float h_scaling = 116.0/1920.0;
constexpr float v_scaling = 65.0/1080.0;

MiddleModule::MiddleModule(Serial* serial) : serial(serial) {}
MiddleModule::MiddleModule() : serial(NULL) {}

void MiddleModule::test_path() const {
  base_generator_type generator(42);
  boost::uniform_real<> uni_dist(50, 67); //15-20 fps
  boost::variate_generator<base_generator_type&, boost::uniform_real<>> delay_generator(generator, uni_dist);

  vector<point_xy<int>> coordinates = {
    {1000, 1000},
    {800, 800},
    {700, 800},
    {700, 700},
    {700, 200}
  };

  cout << coordinates.front().x() << endl;

  point_xy<int> prev(0, 0);

  float fps_counter;
  int fps_cntr2 = 0;

  for (auto p : coordinates) {
    point_xy<int> target(p.x() - prev.x(), p.y() - prev.y());

    cout << "move " + lexical_cast<string>(target.x() * h_scaling) + " right" << endl;
    cout << "move " + lexical_cast<string>(target.y() * v_scaling) + " up" << endl;

    prev = p;

    double sleeper = delay_generator() / 1000.0;
    fps_counter += sleeper;
    fps_cntr2++;
    cout << "current_fps = " << fps_cntr2 / fps_counter << std::endl << std::endl;
    sleep(sleeper);
  }
}
