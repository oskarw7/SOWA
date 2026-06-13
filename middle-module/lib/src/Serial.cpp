// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "sowa-lib/Serial.hpp"

#include <boost/asio/io_context.hpp>
#include <boost/asio/read.hpp>
#include <boost/asio/serial_port.hpp>
#include <iostream>
#include <string>

#include "sowa-lib/helpers.hpp"

namespace ba = boost::asio;
using std::cout;
using std::endl;
using std::string;

Serial::Serial(string portName, unsigned int baudRate)
    : io(), port(io, portName) {
  this->port.set_option(ba::serial_port_base::baud_rate(baudRate));
  this->port.set_option(ba::serial_port_base::character_size(8));

  cout << "Serial is open, init the device!" << endl;
}

Serial::~Serial() { this->port.close(); }

void Serial::send(packet_t p) {
  calculate_checksum(&p);
  this->port.write_some(ba::buffer(&p, sizeof(packet_t)));
}

void Serial::receive(packet_t* p) {
  uint8_t sync_byte = 0;

  while (true) {
    boost::asio::read(this->port, ba::buffer(&sync_byte, 1));

    if (sync_byte == kHeader) {
      p->header = sync_byte;
      break;
    }
  }

  boost::asio::read(this->port, ba::buffer(reinterpret_cast<uint8_t*>(p) + 1,
                                           sizeof(packet_t) - 1));
}