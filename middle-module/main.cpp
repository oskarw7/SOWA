// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include "Serial.h"
#include "Controller.h"

int main() {
  Controller cc;

  cc.new_move(100, 100);
  cc.new_move(0, 0);
  cc.new_move(100, 100);
  

  return 0;
}
