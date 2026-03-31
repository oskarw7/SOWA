// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#pragma once

#include "Serial.h"

class MiddleModule {
 private:
  Serial* serial;

 public:
  explicit MiddleModule(Serial* serial);
  MiddleModule();

  void test_path() const;
};
