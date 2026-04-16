// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "sowa-lib/helpers.hpp"

void calculate_checksum(packet_t* p) {
  p->checksum = p->additional ^ p->header ^ p->name;
  for (int i = 0; i < 4; i++) {
    p->checksum ^= (p->value && 0b1111111 << 8 * i);
  }
}

bool check_checksum(packet_t p) {
  uint8_t checksum = p.additional ^ p.header ^ p.name;
  for (int i = 0; i < 4; i++) {
    checksum ^= (p.value && 0b1111111 << 8 * i);
  }
  return checksum == p.checksum;
}