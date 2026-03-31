// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <vector>
#include <iostream>
#include <string>
#include "Serial.h"
#include "MiddleModule.h"


int main() {
  //Serial serial("test", 9600);
  //MiddleModule mm(serial);
  MiddleModule mm;
  mm.test_path();

  return 0;
}
