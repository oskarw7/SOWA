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
constexpr float kHSpeed = 5000.0;
constexpr float kHAccel = 1000.0;
constexpr uint16_t kHStepsPerFullSpin = 6400;

constexpr uint8_t kVDirPin = 12;
constexpr uint8_t kVPulPin = 13;
constexpr float kVSpeed = 5000.0;
constexpr float kVAccel = 1000.0;
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
  StepperHandler(FastAccelStepperEngine &eng, uint8_t stepPin,
                float microsteps, float gearRatio) {
    stepper = eng.stepperConnectToPin(stepPin);
    stepsPerDegree = microsteps * gearRatio/ FULL_SPIN_DEG;
  }

  void init(float speed, float acceleration, uint8_t dirPin) {
    stepper->setDirectionPin(dirPin, false);
    stepper->setSpeedInHz(speed);
    stepper->setAcceleration(acceleration);
  }

  bool canMove(float direction) {
    if (stepper->getStepPin() == kVPulPin) {
      float VPosDeg = stepper->getCurrentPosition() / stepsPerDegree;

      if ((direction < 0 && VPosDeg <= kMaxDegreesDown) ||
          (direction > 0 && VPosDeg >= kMaxDegreesUp)) {
        return false;
      }
    }

    return true;
  }

  void move(float degrees, bool blocking = false) {
    if (!canMove(degrees)) {
      return;
    }

    stepper->move(static_cast<int32_t>(degrees * stepsPerDegree),
                        blocking);
  }

  float getStepsPerDegree() {
    return stepsPerDegree;
  }

  void stopMove() {
    stepper->stopMove();
  }

  int32_t getCurrentPosition() {
    return stepper->getCurrentPosition();
  }

  uint32_t stepsToStop() {
    return stepper->stepsToStop();
  }

  bool isRunning() {
    return stepper->isRunning();
  }

  int8_t getMovementDirection() {
    int32_t speed = stepper->getCurrentSpeedInUs();

    if (speed == 0) {
      return 0;
    }
    return speed > 0 ? 1 : -1;
  }

  bool isStopping() {
    return stepper->isStopping();
  }

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

enum name {
  move,
  stop,
  reset_pos,
  restart_esp,
  esp_ok,
  used
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
};

FastAccelStepperEngine g_engine = FastAccelStepperEngine();

StepperHandler* g_horizontal_motor = nullptr;
StepperHandler* g_vertical_motor = nullptr;

packet_t packet;

void checkMovementConstraints() {
  int32_t VStopPos =
      (g_vertical_motor->getCurrentPosition() +
      (g_vertical_motor->getMovementDirection() *
      g_vertical_motor->stepsToStop()));

  int8_t movementDir = g_vertical_motor->getMovementDirection();
  float vert_SPD = g_vertical_motor->getStepsPerDegree();

  if (g_vertical_motor->isRunning() && !g_vertical_motor->isStopping()) {
    if (VStopPos <= kMaxDegreesDown * vert_SPD && movementDir == (-1)) {
      g_vertical_motor->stopMove();
    } else if (VStopPos >= kMaxDegreesUp * vert_SPD && movementDir == 1) {
      g_vertical_motor->stopMove();
    }
  }
}

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

  // Serial.write((byte*)&packet, sizeof(packet_t));
}


void loop() {
  checkMovementConstraints();

  if (Serial.available() >= sizeof(packet_t)) {
    Serial.readBytes((byte*)&packet, sizeof(packet_t));
  }

  
  if (packet.name != name::used && check_checksum(packet) && packet.header == kHeader) {
    switch (packet.name)
    {
      case name::move:
        switch (packet.additional)
        {
          case direction::right:
            g_horizontal_motor->move(packet.value);
            break;
          case direction::left:
            g_horizontal_motor->move(packet.value * (-1));
            break;
          case direction::up:
            g_vertical_motor->move(packet.value);
            break;
          case direction::down:
            g_vertical_motor->move(packet.value * (-1));
            break;
        }
        break;
      case name::stop:
        switch (packet.additional)
        {
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
