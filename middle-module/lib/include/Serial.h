// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <string>
#include <boost/asio.hpp>
#include "Helpers.h"

using std::string;

class Serial {
 private:
  boost::asio::io_context io;
  boost::asio::serial_port port;

 public:
  Serial(string portName, unsigned int baudRate);
  ~Serial();

  void send(packet p);
  void send(string s);

  void receive(packet* p);
  string readUntil(char c);
};
