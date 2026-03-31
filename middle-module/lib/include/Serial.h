// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <string>
#include <boost/asio.hpp>

using std::string;

class Serial {
 private:
  boost::asio::io_context io;
  boost::asio::serial_port port;

 public:
  Serial(string portName, unsigned int baudRate);

  void write(string s);
  void read();
  string readUntil(char c);
};
