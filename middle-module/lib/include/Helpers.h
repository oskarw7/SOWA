// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <cstdint>

constexpr uint8_t kHeader = 0b01010101;

struct packet {
  float value;
  uint8_t header;
  uint8_t name;
  uint8_t additional;
  uint8_t checksum = 0;
};

enum name {
    move,
    stop,
    reset,
    magnetometer
};

enum direction {
    left,
    right,
    up,
    down
};

enum stop {
  hor,
  vert,
  both
}
