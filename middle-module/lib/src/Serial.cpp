// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <string>
#include <iostream>
#include <boost/asio.hpp>
#include "Serial.h"
#include "Helpers.h"

namespace ba = boost::asio;
using std::string;
using std::cout;
using std::endl;

Serial::Serial(string portName, unsigned int baudRate)
  : io()
  , port(io, portName) {
  this->port.set_option(ba::serial_port_base::baud_rate(baudRate));
  this->port.set_option(ba::serial_port_base::character_size(8));

  sleep(1);  // wait for init

  cout << "Serial is ready!" << std::endl;
}


Serial::~Serial() {
  this->port.close();
}

void Serial::send(packet p) {
  this->port.write_some(ba::buffer(&p, sizeof(packet)));
}

void Serial::send(string s) {
  this->port.write_some(ba::buffer(s.c_str(), s.size()));
}

void Serial::receive(packet* p) {
  this->port.read_some(ba::buffer(p, sizeof(packet)));
  cout << "Received name: " << (direction)(p->name) << endl;
}

string Serial::readUntil(char c) {
  ba::streambuf sb;
  std::size_t n = ba::read_until(this->port, sb, c);
  string ret(
    ba::buffers_begin(sb.data()),
    ba::buffers_begin(sb.data()) + n);
  return ret;
}

