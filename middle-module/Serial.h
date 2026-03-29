// ============================================================================
// Copyright 2026 SOWA
// ============================================================================

#ifndef SERIAL_H_
#define SERIAL_H_

#include <string>
#include <iostream>
#include <boost/asio.hpp>


namespace ba = boost::asio;

class Serial {
 public:
  Serial(std::string portName, unsigned int baudRate) : io(), port(io, portName) {
    port.set_option(ba::serial_port_base::baud_rate(baudRate));
    port.set_option(ba::serial_port_base::character_size(8));
  }

  void write(std::string s) {
    port.write_some(ba::buffer(s.c_str(), s.size()));
  }

  void read() {
    char data[50];
    port.read_some(ba::buffer(data, 50));
    std::cout << "I have read this: "; 
    std::cout.write(data, 50);
    std::cout << std::endl;
  }

  std::string readUntil(char c) {
    ba::streambuf sb;
    std::size_t n = ba::read_until(port, sb, c);
    std::string ret(
      ba::buffers_begin(sb.data()),
      ba::buffers_begin(sb.data()) + n);
    return ret;
  }

 private:
  ba::io_context io;
  ba::serial_port port;
};

#endif  // SERIAL_H_
