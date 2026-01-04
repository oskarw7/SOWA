#include "FastAccelStepper.h"

#define FULL_SPIN_DEG 360

// Horizontal motor
#define HDirPin 10
#define HPulPin 11
#define HSpeed 1000.0       // steps / s
#define HAccel 1000.0        // steps / s^2
#define HStepsPerSpin 800

// Vertical motor
#define VDirPin 12
#define VPulPin 13
#define VSpeed 1000.0
#define VAccel 1000.0
#define VStepsPerSpin 400

// Gear ratios calculation
#define belt_height 6

#define smaller_belt_drive_radius 10.097
#define horizontal_bigger_belt_drive_radius 21.5   
#define vertical_bigger_belt_drive_radius 35.748

#define HRatio (horizontal_bigger_belt_drive_radius + belt_height/2) / (smaller_belt_drive_radius + belt_height/2) 
#define VRatio (vertical_bigger_belt_drive_radius + belt_height/2) / (smaller_belt_drive_radius + belt_height/2) 


// Serial input 
// ex. "move 25.3 right",
// "stop horizontal",
// "move 45 200"
#define MAX_MESSAGE_SUBSTRINGS 10
#define ACTION_IDX 0
#define DIRECTION_IDX 2
#define SELECTION_IDX 1
#define ANGLE_IDX 1
#define ACCEL_IDX 2

class StepperHandler {
    private:
        FastAccelStepper* stepper = NULL; 
        float stepsPerDegree; 

    public:
        StepperHandler(FastAccelStepperEngine &eng, uint8_t stepPin, uint16_t microsteps, float gearRatio) {
            stepper = eng.stepperConnectToPin(stepPin);
            
            int motorStepsPerRev = microsteps;
            float cameraStepsPerRev = motorStepsPerRev * gearRatio;

            stepsPerDegree = cameraStepsPerRev / FULL_SPIN_DEG;
        }

    void init(float speed, float acceleration, uint8_t dirPin) {
        if(stepper){
            stepper->setDirectionPin(dirPin);
            stepper->setSpeedInHz(speed);               // Max ~200kHz, steps/second
            stepper->setAcceleration(acceleration);

            Serial.println("Initialization of motor succesful");
        }
    }

    void moveRelative(float degrees) {
        stepper->move((long)(degrees * stepsPerDegree));
    }

    void moveToAngle(float degrees) {
        stepper->moveTo((long)(degrees * stepsPerDegree));
    }

    MoveResultCode moveByAcceleration(int32_t acceleration, bool allow_reverse = true){
        return stepper->moveByAcceleration(acceleration, allow_reverse);
    }

    void stopMove() {
    	stepper->stopMove();
    }

    void forceStop() {
    	stepper->forceStop();
    }
};


int string_split(String inputString, char delimiter, String outputString[]){
	uint8_t subStringCount = 0;
	uint8_t previousCutoff = 0;

	for(uint8_t i = 0; i < inputString.length(); ++i) {
		if (inputString[i] == delimiter) {
			outputString[subStringCount++] = inputString.substring(previousCutoff, i);

            previousCutoff = i+1;
		}
	}
    // take the last one
    outputString[subStringCount++] = inputString.substring(previousCutoff, inputString.length());

	return subStringCount;
}

bool isNumber(String inputString){
    for(uint8_t i = 0; i < inputString.length(); ++i){
        if(!isDigit(inputString[i])) return false;
    }

    return true;
}

FastAccelStepperEngine engine = FastAccelStepperEngine();  

StepperHandler* horizontalMotor = nullptr;
StepperHandler* verticalMotor = nullptr;

String message[MAX_MESSAGE_SUBSTRINGS];


void setup() {
    Serial.begin(115200);

    engine.init();
    horizontalMotor = new StepperHandler(engine, HPulPin, HStepsPerSpin, HRatio);
    verticalMotor = new StepperHandler(engine, VPulPin, VStepsPerSpin, VRatio);
  
    horizontalMotor->init(HSpeed, HAccel, HDirPin); 
    verticalMotor->init(VSpeed, VAccel, VDirPin);
}


void loop() {
	if (Serial.available() > 0) {
        String serialInput = Serial.readStringUntil('\n');
	
		// Clear previous message
		for(uint8_t i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i){
            if(message[i].equals("")) break;

			message[i] = "";
		}
		string_split(serialInput, ' ', message);

        // Sanitize input
        for(uint8_t i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i){
			if(message[i].equals("")) break;

            message[i].trim();
            message[i].toLowerCase();
		}
	}

	if(!message[ACTION_IDX].equals("")){
        String act = message[ACTION_IDX];
        if (act.equals("move")){
            float angle = message[ANGLE_IDX].toFloat();
            if (isNumber(message[ACCEL_IDX]) && isNumber(message[ANGLE_IDX])){
                float accel = message[ACCEL_IDX].toFloat();
                float accelHor = cos(angle * PI/180) * accel;
                float accelVer = sin(angle * PI/180) * accel;
                
                horizontalMotor->moveByAcceleration(accelHor);
                verticalMotor->moveByAcceleration(accelVer);

                Serial.print("Moving the camera, angle: ");
                Serial.print(angle);
                Serial.print(" accel: ");
                Serial.println(accel);
            } else {
                String dir = message[DIRECTION_IDX];
            
                        
                if ((dir.equals("right") || dir.equals("left"))) {
                    angle *= (dir.equals("right") ? 1 : (-1));
                    horizontalMotor->moveRelative(angle);
                    
                    Serial.print("Moving hor: ");
                    Serial.println(angle);
                } else if ((dir.equals("up") || dir.equals("down"))) {
                    angle *= (dir.equals("down") ? 1 : (-1));
                    verticalMotor->moveRelative(angle);
                    
                    Serial.print("Moving ver: ");
                    Serial.println(angle);
                }
            }
        } else if (act.equals("stop")) {
            String sel = message[SELECTION_IDX];
            
            if (sel.equals("horizontal")){
                horizontalMotor->stopMove();
                Serial.println("Stopping hor");
            } else if (sel.equals("vertical")) {
                verticalMotor->stopMove();
                Serial.println("Stopping ver");
            } else if ((sel.equals("both"))) {
                horizontalMotor->stopMove();
                verticalMotor->stopMove();
                Serial.println("Stopping both");
            }
            
        } else if (act.equals("showcase")) {
            // For showcase of full range of motion
            Serial.println("Showcase not implemented yet");
        }
    }

    delay(2000); // Temporary 
    message[ACTION_IDX] = "";
}
