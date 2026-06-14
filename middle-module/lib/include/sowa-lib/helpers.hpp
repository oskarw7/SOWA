// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include <cstdint>

constexpr uint8_t kHeader = 0b01010101;

typedef struct __attribute__((packed)) {
  uint8_t header;
  uint8_t name;
  uint8_t additional;
  uint8_t checksum = 0;
  float value;
} packet_t;

enum name : uint8_t {
  move,
  stop,
  reset_pos,
  restart_esp,
  esp_ok,
  used,
  get_current_pos,
  current_pos
};

enum direction { left, right, up, down };

enum axis { hor, vert, both };

void calculate_checksum(packet_t* p);

bool check_checksum(packet_t p);
