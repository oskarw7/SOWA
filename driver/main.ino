#include <AccelStepper.h>

#define FULL_SPIN_DEG 360

// Horizontal motor
#define HDirPin 10
#define HPulPin 11
#define HMaxSpeed 4000.0
#define HAccel 1000.0

// Vertical motor
#define VDirPin 12
#define VPulPin 13
#define VMaxSpeed 4000.0
#define VAccel 1000.0

// Gear ratios calculation
#define belt_height 6

#define smaller_belt_drive_radius 10.097
#define horizontal_bigger_belt_drive_radius 21.5   
#define vertical_bigger_belt_drive_radius 35.748

#define HRatio (horizontal_bigger_belt_drive_radius + belt_height/2) / (smaller_belt_drive_radius + belt_height/2) 
#define VRatio (vertical_bigger_belt_drive_radius + belt_height/2) / (smaller_belt_drive_radius + belt_height/2) 


// Serial input 
// ex. "move right 25.3",
// "stop horizontal"
#define MAX_MESSAGE_SUBSTRINGS 10
#define ACTION_IDX 0
#define DIRECTION_IDX 1
#define SELECTION_IDX 1
#define ANGLE_IDX 2


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

    void stop() {
    	stepper.stop();
    }
};


// Placeholder for future implementation
int string_split(String inputString, char delimiter, String outputString[]){
	int subStringCount = 0;
	int previousCutoff = 0;

	for(int i = 0; i < inputString.length(); ++i) {
		if (inputString[i] == delimiter) {
			outputString[subStringCount++] = inputString.substring(previousCutoff, i);

            previousCutoff = i+1;
		}
	}
    // take the last one
    outputString[subStringCount++] = inputString.substring(previousCutoff, inputString.length());

	return subStringCount;
}


StepperHandler horizontalMotor(HPulPin, HDirPin, 800, HRatio);
StepperHandler verticalMotor(VDirPin, VPulPin, 400, VRatio);

String message[MAX_MESSAGE_SUBSTRINGS];


void setup() {
  Serial.begin(115200);

  horizontalMotor.init(HMaxSpeed, HAccel); 
  verticalMotor.init(VMaxSpeed, VAccel);
}


void loop() {
    horizontalMotor.run();
    verticalMotor.run();

	if (Serial.available() > 0) {
        String serialInput = Serial.readStringUntil('\n');
	
		// Clear previous message
		for(int i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i){
            if(message[i].equals("")) break;

			message[i] = "";
		}

		string_split(serialInput, ' ', message);

        // Sanitize input
        for(int i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i){
			if(message[i].equals("")) break;

            message[i].trim();
            message[i].toLowerCase();
		}
	}

	
	String act = message[ACTION_IDX];
	if (act.equals("move")){
		float angle = message[ANGLE_IDX].toFloat();
		String dir = message[DIRECTION_IDX];
		
					 
		if ((dir.equals("right") || dir.equals("left"))) {
            angle *= (dir.equals("right") ? 1 : (-1));
			horizontalMotor.moveRelative(angle);
            
            Serial.println("Moving hor: ");
            Serial.println(angle);
		}
		
		if ((dir.equals("up") || dir.equals("down"))) {
			angle *= (dir.equals("down") ? 1 : (-1));
            verticalMotor.moveRelative(angle);
            
            Serial.println("Moving ver: ");
            Serial.println(angle);
		}
					
		delay(100); // Temporary 
	} else if (act.equals("stop")) {
		String sel = message[SELECTION_IDX];
        
        if (sel.equals("horizontal")){
			horizontalMotor.stop();
			Serial.println("Stopping hor");
		} else if (sel.equals("vertical")) {
			verticalMotor.stop();
            Serial.println("Stopping ver");
		} else if ((sel.equals("both"))) {
			horizontalMotor.stop();
			verticalMotor.stop();
            Serial.println("Stopping both");
		}
		
	} else if (act.equals("showcase")) {
		// For showcase of full range of motion
		Serial.println("Showcase not implemented yet");
	}

    message[ACTION_IDX] = "";
}
