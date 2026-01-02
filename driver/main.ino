#include <AccelStepper.h>

#define FULL_SPIN_DEG 360

#define HDirPin 10
#define HPulPin 11
#define HRatio 1.53125

#define VDirPin 12
#define VPulPin 13
#define VRatio 1.79675


class StepperHandler {
    private:
        AccelStepper stepper; 
        float stepsPerDegree; 

    public:
        StepperHandler(byte stepPin, byte dirPin, int microsteps, double gearRatio) : stepper(AccelStepper::DRIVER, stepPin, dirPin) {
            int motorStepsPerRev = microsteps;
            float cameraStepsPerRev = motorStepsPerRev * gearRatio;

            stepsPerDegree = cameraStepsPerRev / FULL_SPIN_DEG;
        }

    void init(float maxSpeed, float acceleration) {
        stepper.setMaxSpeed(maxSpeed);
        stepper.setAcceleration(acceleration);
    }

    void moveRelative(float degrees) {
        stepper.move((long)(degrees * stepsPerDegree));
    }

    void moveToAngle(float degrees) {
        stepper.moveTo((long)(degrees * stepsPerDegree));
    }

    bool run() {
      return stepper.run();
    }
};

StepperHandler horizontalMotor(HPulPin, HDirPin, 800, HRatio);
//StepperHandler verticalMotor(VDirPin, VPulPin, 400, VRatio);

void setup() {
  Serial.begin(115200);

  horizontalMotor.init(4000.0, 1000.0); 
  //verticalMotor.init(4000.0, 1000.0);
}
int i = 1;

void loop() {
    if(!horizontalMotor.run()){
      horizontalMotor.moveRelative(i);
      //i+=1;
      delay(10);
    }
}
