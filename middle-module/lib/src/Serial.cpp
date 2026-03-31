// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <string>
#include <iostream>
#include <boost/asio.hpp>
#include "Serial.h"

namespace ba = boost::asio;
using std::string;
using std::cout;

Serial::Serial(string portName, unsigned int baudRate)
  : io()
  , port(io, portName) {
  this->port.set_option(ba::serial_port_base::baud_rate(baudRate));
  this->port.set_option(ba::serial_port_base::character_size(8));

  sleep(1);  // wait for init
}

void Serial::write(string s) {
  this->port.write_some(ba::buffer(s.c_str(), s.size()));
  sleep(0.5);
}

void Serial::read() {
  char data[50];
  this->port.read_some(ba::buffer(data, 50));
  cout << "I have read this: ";
  cout.write(data, 50);
  cout << std::endl;
}

string Serial::readUntil(char c) {
  ba::streambuf sb;
  std::size_t n = ba::read_until(this->port, sb, c);
  string ret(
    ba::buffers_begin(sb.data()),
    ba::buffers_begin(sb.data()) + n);
  return ret;
}

