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
    if (stepper) {
      stepper->setDirectionPin(dirPin, false);
      stepper->setSpeedInHz(speed);
      stepper->setAcceleration(acceleration);

      Serial.println("Initialization of motor succesful!");
    } else {
      Serial.println("Initialization of motor failed!");
    }
  }

  bool canMove(float direction) {
    if (stepper->getStepPin() == kVPulPin) {
      float VPosDeg = stepper->getCurrentPosition() / stepsPerDegree;

      if ((direction < 0 && VPosDeg <= kMaxDegreesDown) ||
          (direction > 0 && VPosDeg >= kMaxDegreesUp)) {
        Serial.println("Can't move to specified angle!");

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

  void moveByAcceleration(
      int32_t acceleration, bool allow_reverse = true) {
    if (!canMove(acceleration)) {
      return;
    }

    stepper->moveByAcceleration(acceleration, allow_reverse);
  }

  float getStepsPerDegree() {
    return stepsPerDegree;
  }

  void stopMove() {
    stepper->stopMove();
  }

  void forceStop() {
    stepper->forceStop();
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

FastAccelStepperEngine g_engine = FastAccelStepperEngine();

StepperHandler* g_horizontal_motor = nullptr;
StepperHandler* g_vertical_motor = nullptr;

String g_message[kMaxMessageSubstrings];


int stringSplit(String inputString, char delimiter, String outputString[]) {
  uint8_t subStringCount = 0;
  uint8_t previousCutoff = 0;
  uint8_t strLen = inputString.length();

  for (uint8_t i = 0; i < strLen; ++i) {
    if (inputString[i] == delimiter) {
      outputString[subStringCount++] =
          inputString.substring(previousCutoff, i);

      previousCutoff = i+1;
    }
  }
  // take the last one
  outputString[subStringCount++] =
      inputString.substring(previousCutoff, strLen);

  return subStringCount;
}

bool isNumber(String inputString) {
  for (uint8_t i = 0; i < inputString.length(); ++i) {
    if (!isDigit(inputString[i])) {
      return false;
    }
  }

  return true;
}

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

      Serial.println("Stopped at max down");
    } else if (VStopPos >= kMaxDegreesUp * vert_SPD && movementDir == 1) {
      g_vertical_motor->stopMove();

      Serial.println("Stopped at max up");
    }
  }
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
}


void loop() {
  checkMovementConstraints();

  if (Serial.available() > 0) {
    String serialInput = Serial.readStringUntil('\n');

    // Clear previous g_message
    for (uint8_t i = 0; i < kMaxMessageSubstrings; ++i) {
      if (g_message[i].equals("")) {
        break;
      }

      g_message[i] = "";
    }

    stringSplit(serialInput, ' ', g_message);

    // Sanitize input
    for (uint8_t i = 0; i < kMaxMessageSubstrings; ++i) {
      if (g_message[i].equals("")){
        break;
      }

      g_message[i].trim();
      g_message[i].toLowerCase();
    }
  }

  if (!g_message[ACTION_IDX].equals("")) {
    String act = g_message[ACTION_IDX];

    if (act.equals("move")) {
      float angle = g_message[ANGLE_IDX].toFloat();

      if (isNumber(g_message[ACCEL_IDX]) && isNumber(g_message[ANGLE_IDX])) {
        float accel = g_message[ACCEL_IDX].toFloat();
        int32_t accelHor = cos(angle * PI/180) * accel * (-1);
        int32_t accelVer = sin(angle * PI/180) * accel;

        g_horizontal_motor->moveByAcceleration(accelHor);
        g_vertical_motor->moveByAcceleration(accelVer);

        Serial.print("Moving the camera, angle: ");
        Serial.print(angle);
        Serial.print(" accel: ");
        Serial.println(accel);
      } else {
        String dir = g_message[DIRECTION_IDX];

        if (dir.equals("right") || dir.equals("left")) {
          angle *= (dir.equals("left") ? 1 : (-1));
          g_horizontal_motor->move(angle);

          Serial.print("Moving hor: ");
          Serial.println(angle);
        } else if (dir.equals("up") || dir.equals("down")) {
          angle *= (dir.equals("up") ? 1 : (-1));

          g_vertical_motor->move(angle);

          Serial.print("Moving ver: ");
          Serial.println(angle);
        }
      }
    } else if (act.equals("stop")) {
      String sel = g_message[SELECTION_IDX];

      if (sel.equals("horizontal")) {
        g_horizontal_motor->stopMove();

        Serial.println("Stopping hor");
      } else if (sel.equals("vertical")) {
        g_vertical_motor->stopMove();

        Serial.println("Stopping ver");
      } else if ((sel.equals("both"))) {
        g_horizontal_motor->stopMove();
        g_vertical_motor->stopMove();

        Serial.println("Stopping both");
      }
    } else if (act.equals("showcase")) {
      // For showcase of full range of motion
      g_horizontal_motor->move(FULL_SPIN_DEG, true);
      g_horizontal_motor->move(-FULL_SPIN_DEG, true);
      g_vertical_motor->move(FULL_SPIN_DEG);
      while (g_vertical_motor->isRunning()) {
        checkMovementConstraints();
        delay(50);
      }
      g_vertical_motor->move(-FULL_SPIN_DEG);
      while (g_vertical_motor->isRunning()) {
        checkMovementConstraints();
        delay(50);
      }

      g_horizontal_motor->move(-15);
      g_vertical_motor->move(180.0);
      while (g_vertical_motor->isRunning()) {
        checkMovementConstraints();
        delay(50);
      }
      g_horizontal_motor->move(30);
      g_vertical_motor->move(-180.0);
      while (g_vertical_motor->isRunning()) {
        checkMovementConstraints();
        delay(50);
      }

      g_horizontal_motor->move(-180);
      g_vertical_motor->move(45);
      while (g_vertical_motor->isRunning()) {
        checkMovementConstraints();
        delay(50);
      }
      g_vertical_motor->move(-60);
      while (g_vertical_motor->isRunning()) {
        checkMovementConstraints();
        delay(50);
      }
      g_horizontal_motor->move(90, true);
      g_horizontal_motor->stopMove();
      g_vertical_motor->stopMove();
    } else if (act.equals("reset pos")) {
      g_vertical_motor->setCurrentPosition(0);
      g_horizontal_motor->setCurrentPosition(0);

      Serial.println("Position reset");
    }
  }

  g_message[ACTION_IDX] = "";
}
