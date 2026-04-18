// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "sowa-lib/helpers.hpp"

void calculate_checksum(packet_t* p) {
  p->checksum = p->additional ^ p->header ^ p->name;
  for (int i = 0; i < 4; i++) {
    p->checksum ^= (p->value >> (8 * i) & 0b11111111);
  }
}

bool check_checksum(packet_t p) {
  uint8_t checksum = p.additional ^ p.header ^ p.name;
  for (int i = 0; i < 4; i++) {
    checksum ^= (p.value >> (8 * i) & 0b11111111);
  }
  return checksum == p.checksum;
}