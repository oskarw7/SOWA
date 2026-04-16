// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <string>
#include <boost/asio.hpp>
#include "sowa-lib/helpers.hpp"

using std::string;

class Serial {
 private:
  boost::asio::io_context io;
  boost::asio::serial_port port;

 public:
  Serial(string portName, unsigned int baudRate);
  ~Serial();

  void send(packet_t p);

  void receive(packet_t* p);
};
