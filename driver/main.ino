// ============================================================================
// Copyright 2026 SOWA
// ============================================================================
#include <FastAccelStepper.h>

// Variables helping avoid magic numbers
constexpr uint16_t FULL_SPIN_DEG = 360;

// In the variables below prefixes mean:
// k - const
// g - global
// H - horizontal
// V - vertical
// Notes:
// Speeds are expressed in stpes/s
// Accelerations are expressed in [steps/s^2]
constexpr uint8_t kHDirPin = 10;
constexpr uint8_t kHPulPin = 11;
constexpr float kHSpeed = 1480.0;
constexpr float kHAccel = 494.0;
constexpr uint16_t kHStepsPerFullSpin = 6400;

constexpr uint8_t kVDirPin = 12;
constexpr uint8_t kVPulPin = 13;
constexpr float kVSpeed = 2290.0;
constexpr float kVAccel = 764.0;
constexpr uint16_t kVStepsPerFullSpin = 6400;

// Movement constraints in degrees
constexpr int8_t kMaxDegreesDown = -20;
constexpr uint8_t kMaxDegreesUp = 80;

// Gear ratios
constexpr float kHRatio = 1.39;
constexpr float kVRatio = 2.15;

// Serial input
// ex. "move 25.3 right",
// "stop horizontal",
// "move 45 200"
constexpr uint8_t kMaxMessageSubstrings = 10;
constexpr uint8_t ACTION_IDX = 0;
constexpr uint8_t DIRECTION_IDX = 2;
constexpr uint8_t SELECTION_IDX = 1;
constexpr uint8_t ANGLE_IDX = 1;
constexpr uint8_t ACCEL_IDX = 2;

constexpr uint8_t kHeader = 0b01010101;

class StepperHandler {
 private:
  FastAccelStepper* stepper = nullptr;
  float stepsPerDegree;

 public:
  StepperHandler(FastAccelStepperEngine& eng, uint8_t stepPin, float microsteps,
                 float gearRatio) {
    stepper = eng.stepperConnectToPin(stepPin);
    stepsPerDegree = microsteps * gearRatio / FULL_SPIN_DEG;
  }

  void init(float speed, float acceleration, uint8_t dirPin) {
    stepper->setDirectionPin(dirPin, false);
    stepper->setSpeedInHz(speed);
    stepper->setAcceleration(acceleration);
  }

  void moveTo(float degrees, bool blocking = false) {
    stepper->moveTo(static_cast<int32_t>(degrees * stepsPerDegree), blocking);
  }

  void stopMove() { stepper->stopMove(); }

  int32_t getCurrentPosition() { return stepper->getCurrentPosition(); }

  float resolveCurrentAngle() { return getCurrentPosition() / stepsPerDegree; }

  void setCurrentPosition(int32_t newPos) {
    stepper->setCurrentPosition(newPos);
  }
};

typedef struct __attribute__((packed)) {
  uint8_t header;
  uint8_t name;
  uint8_t additional;
  uint8_t checksum = 0;
  float value;
} packet_t;

enum name { move, stop, reset_pos, restart_esp, esp_ok, used };

enum direction { left, right, up, down };

enum stop { hor, vert, both };

enum axis { h, v };

FastAccelStepperEngine g_engine = FastAccelStepperEngine();

StepperHandler* g_horizontal_motor = nullptr;
StepperHandler* g_vertical_motor = nullptr;

packet_t packet;
float targetOrientation[2]{0.0f, 0.0f};

void calculate_checksum(packet_t* p) {
  p->checksum = p->additional ^ p->header ^ p->name;
  for (int i = 0; i < 4; i++) {
    p->checksum ^= (std::bit_cast<uint32_t>(p->value) >> (8 * i) & 0b11111111);
  }
}

bool check_checksum(packet_t p) {
  uint8_t checksum = p.additional ^ p.header ^ p.name;
  for (int i = 0; i < 4; i++) {
    checksum ^= (std::bit_cast<uint32_t>(p.value) >> (8 * i) & 0b11111111);
  }
  return checksum == p.checksum;
}

void setup() {
  Serial.begin(115200);

  g_engine.init();
  g_horizontal_motor =
      new StepperHandler(g_engine, kHPulPin, kHStepsPerFullSpin, kHRatio);
  g_vertical_motor =
      new StepperHandler(g_engine, kVPulPin, kVStepsPerFullSpin, kVRatio);

  g_horizontal_motor->init(kHSpeed, kHAccel, kHDirPin);
  g_vertical_motor->init(kVSpeed, kVAccel, kVDirPin);

  packet.header = kHeader;
  packet.name = name::esp_ok;
  packet.additional = 0;
  packet.value = 0.0;
  calculate_checksum(&packet);

  Serial.write((byte*)&packet, sizeof(packet_t));
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.peek() == kHeader) {
      if (Serial.available() >= sizeof(packet_t)) {
        Serial.readBytes((byte*)&packet, sizeof(packet_t));
      }
    }
  }

  if (packet.name != name::used && check_checksum(packet) &&
      packet.header == kHeader) {
    switch (packet.name) {
      case name::move: {
        float move_degrees = packet.value;

        if (packet.additional == direction::right ||
            packet.additional == direction::left) {
          if (packet.additional == direction::left) {
            move_degrees *= -1.0f;
          }

          targetOrientation[axis::h] =
              g_horizontal_motor->resolveCurrentAngle() + move_degrees;

          g_horizontal_motor->moveTo(targetOrientation[axis::h]);
        } else if (packet.additional == direction::up ||
                   packet.additional == direction::down) {
          if (packet.additional == direction::down) {
            move_degrees *= -1.0f;
          }

          targetOrientation[axis::v] =
              g_vertical_motor->resolveCurrentAngle() + move_degrees;

          if (targetOrientation[axis::v] > kMaxDegreesUp) {
            targetOrientation[axis::v] = kMaxDegreesUp;
          }

          if (targetOrientation[axis::v] < kMaxDegreesDown) {
            targetOrientation[axis::v] = kMaxDegreesDown;
          }

          g_vertical_motor->moveTo(targetOrientation[axis::v]);
        }
        break;
      }

      case name::stop:
        switch (packet.additional) {
          case stop::hor:
            g_horizontal_motor->stopMove();
            break;
          case stop::vert:
            g_vertical_motor->stopMove();
            break;
          case stop::both:
            g_horizontal_motor->stopMove();
            g_vertical_motor->stopMove();
            break;
        }
        break;
      case name::reset_pos:
        g_vertical_motor->setCurrentPosition(0);
        g_horizontal_motor->setCurrentPosition(0);
        break;
      case name::restart_esp:
        ESP.restart();
        break;
    }

    packet.name = name::used;
  }
}