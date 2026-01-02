#include <AccelStepper.h>

#define FULL_SPIN_DEG 360

// Horizontal motor
#define HDirPin 10
#define HPulPin 11

// Vertical motor
#define VDirPin 12
#define VPulPin 13

// Gear ratios calculation
#define belt_height 6

#define smaller_belt_drive_radius 10.097
#define horizontal_bigger_belt_drive_radius 21.5   
#define vertical_bigger_belt_drive_radius 35.748

#define HRatio (horizontal_bigger_belt_drive_radius + belt_height/2) / (smaller_belt_drive_radius + belt_height/2) 
#define VRatio (vertical_bigger_belt_drive_radius + belt_height/2) / (smaller_belt_drive_radius + belt_height/2) 

// Serial input ex. "move right 200"
#define MAX_MESSAGE_SUBSTRINGS 10

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

// Placeholder for future implementation
int string_split(String inputString, char delimiter, String outputString[]){
	return;
}

void setup() {
  Serial.begin(115200);

  horizontalMotor.init(4000.0, 1000.0); 
  //verticalMotor.init(4000.0, 1000.0);
}
int i = 1;
String message[MAX_MESSAGE_SUBSTRINGS];
String serialInput = "";

void loop() {
	if(Serial.available() > 0) {
    serialInput = Serial.readStringUntil('\n');
	
		// Clear previous message
		for(int i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i){
			message[i] = "";
		}
	}

	if(serialInput.equals("test")) {
		// horizontalMotor.moveRelative(-100);	
    Serial.println("received test");
	}

    /*if(!horizontalMotor.run()){
      horizontalMotor.moveRelative(i);
      //i+=1;
      delay(10);
    }*/

    serialInput = "";
}
