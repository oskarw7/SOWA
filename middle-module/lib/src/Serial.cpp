// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <string>
#include <iostream>
#include <boost/asio/io_context.hpp>
#include <boost/asio/serial_port.hpp>
#include "sowa-lib/Serial.hpp"
#include "sowa-lib/helpers.hpp"

namespace ba = boost::asio;
using std::string;
using std::cout;
using std::endl;

Serial::Serial(string portName, unsigned int baudRate)
  : io()
  , port(io, portName) {
  this->port.set_option(ba::serial_port_base::baud_rate(baudRate));
  this->port.set_option(ba::serial_port_base::character_size(8));

  cout << "Serial is open, init the device!" << endl;
}

Serial::~Serial() {
  this->port.close();
}

void Serial::send(packet_t p) {
  this->port.write_some(ba::buffer(&p, sizeof(packet_t)));
}

void Serial::receive(packet_t* p) {
  this->port.read_some(ba::buffer(p, sizeof(packet_t)));
}
