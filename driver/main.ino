#include "FastAccelStepper.h"

#define FULL_SPIN_DEG 360

// Horizontal motor
#define HDirPin 10
#define HPulPin 11
#define HSpeed 5000.0       // steps / s
#define HAccel 1000.0        // steps / s^2
#define HStepsPerSpin 6400

// Vertical motor
#define VDirPin 12
#define VPulPin 13
#define VSpeed 5000.0
#define VAccel 1000.0
#define VStepsPerSpin 6400
#define MaxDegreesDown -20
#define MaxDegreesUp 80

// Gear ratios calculation
#define HRatio 1.39
#define VRatio 2.15

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
        if(stepper) {
            stepper->setDirectionPin(dirPin, false);
            stepper->setSpeedInHz(speed);               // Max ~200kHz, steps/second
            stepper->setAcceleration(acceleration);

            Serial.println("Initialization of motor succesful");
        }
    }

    void moveRelative(float degrees, bool blocking=false) {
        stepper->move((long)(degrees * stepsPerDegree), blocking);
    }

    void moveToAngle(float degrees) {
        stepper->moveTo((long)(degrees * stepsPerDegree));
    }

    MoveResultCode moveByAcceleration(int32_t acceleration, bool allow_reverse = true) {
        return stepper->moveByAcceleration(acceleration, allow_reverse);
    }

    float getStepsPerDegree(){
        return stepsPerDegree;
    }

    void stopMove() {
    	stepper->stopMove();
    }

    void forceStop() {
    	stepper->forceStop();
    }

    int32_t getCurrentPosition(){
        return stepper->getCurrentPosition();
    }

    uint32_t stepsToStop(){
        return stepper->stepsToStop();
    }

    bool isRunning() {
      return stepper->isRunning();
    }

    int8_t getMovementDirection() {
        if(stepper->getCurrentSpeedInUs() == 0) return 0;
        return stepper->getCurrentSpeedInUs() > 0 ? 1 : -1;
    }

    bool isStopping(){
        return stepper->isStopping();
    }

    void setCurrentPosition(int32_t newPos){
        stepper->setCurrentPosition(newPos);
    }
};

FastAccelStepperEngine engine = FastAccelStepperEngine();  

StepperHandler* horizontalMotor = nullptr;
StepperHandler* verticalMotor = nullptr;
float VStepsPerDegree = 0.0;

String message[MAX_MESSAGE_SUBSTRINGS];


int string_split(String inputString, char delimiter, String outputString[]) {
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

bool isNumber(String inputString) {
    for(uint8_t i = 0; i < inputString.length(); ++i){
        if(!isDigit(inputString[i])) return false;
    }

    return true;
}

void checkMovementConstraints() {
    int32_t VStopPos = (verticalMotor->getCurrentPosition() + (verticalMotor->getMovementDirection() * verticalMotor->stepsToStop()));
    int8_t movementDir = verticalMotor->getMovementDirection();
    if(verticalMotor->isRunning() && !verticalMotor->isStopping()){
        if (VStopPos <= (MaxDegreesDown) * VStepsPerDegree && movementDir == (-1)) {
            verticalMotor->stopMove();
            Serial.println("Stopped at max down");
        } else if (VStopPos >= (MaxDegreesUp) * VStepsPerDegree && movementDir == 1) {
            verticalMotor->stopMove();
            Serial.println("Stopped at max up");
        }
    }
}

void setup() {
    Serial.begin(115200);

    engine.init();
    horizontalMotor = new StepperHandler(engine, HPulPin, HStepsPerSpin, HRatio);
    verticalMotor = new StepperHandler(engine, VPulPin, VStepsPerSpin, VRatio);
  
    horizontalMotor->init(HSpeed, HAccel, HDirPin); 
    verticalMotor->init(VSpeed, VAccel, VDirPin);

    VStepsPerDegree = verticalMotor->getStepsPerDegree();
}


void loop() {
    checkMovementConstraints();

	if (Serial.available() > 0) {
        String serialInput = Serial.readStringUntil('\n');
	
		// Clear previous message
		for(uint8_t i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i) {
            if(message[i].equals("")) break;

			message[i] = "";
		}
		string_split(serialInput, ' ', message);

        // Sanitize input
        for(uint8_t i = 0; i < MAX_MESSAGE_SUBSTRINGS; ++i) {
			if(message[i].equals("")) break;

            message[i].trim();
            message[i].toLowerCase();
		}
	}

	if(!message[ACTION_IDX].equals("")) {
        String act = message[ACTION_IDX];
        if (act.equals("move")) {
            float angle = message[ANGLE_IDX].toFloat();
            float VPosDeg = verticalMotor->getCurrentPosition() / VStepsPerDegree;

            if (isNumber(message[ACCEL_IDX]) && isNumber(message[ANGLE_IDX])) {
                float accel = message[ACCEL_IDX].toFloat();
                int32_t accelHor = cos(angle * PI/180) * accel * (-1);
                int32_t accelVer = sin(angle * PI/180) * accel;

                bool VCanMove = (!(accelVer < 0 && VPosDeg <= (MaxDegreesDown)) && !(accelVer > 0 && VPosDeg >= (MaxDegreesUp))); 

                horizontalMotor->moveByAcceleration(accelHor);

                if(VCanMove) verticalMotor->moveByAcceleration(accelVer);   
                else Serial.println("Change vert. movement direction");
                
                Serial.print("Moving the camera, angle: ");
                Serial.print(angle);
                Serial.print(" accel: ");
                Serial.println(accel);
            } else {
                String dir = message[DIRECTION_IDX];
                        
                if ((dir.equals("right") || dir.equals("left"))) {
                    angle *= (dir.equals("left") ? 1 : (-1));
                    horizontalMotor->moveRelative(angle);
                    
                    Serial.print("Moving hor: ");
                    Serial.println(angle);
                } else if ((dir.equals("up") || dir.equals("down"))) {
                    angle *= (dir.equals("up") ? 1 : (-1));
                    bool canMove = (!(angle < 0 && VPosDeg <= (MaxDegreesDown)) && !(angle > 0 && VPosDeg >= (MaxDegreesUp)));
                    if (canMove) verticalMotor->moveRelative(angle);
                    else Serial.println("Change movement direction");
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
            horizontalMotor->moveRelative(FULL_SPIN_DEG, true);
            horizontalMotor->moveRelative(-FULL_SPIN_DEG, true);
            verticalMotor->moveRelative(FULL_SPIN_DEG);
            while(verticalMotor->isRunning()) {
                checkMovementConstraints();
                delay(50);
            }
            verticalMotor->moveRelative(-FULL_SPIN_DEG);
            while(verticalMotor->isRunning()) {
                checkMovementConstraints();
                delay(50);
            }

            horizontalMotor->moveRelative(-15);
            verticalMotor->moveRelative(180.0);
            while(verticalMotor->isRunning()) {
                checkMovementConstraints();
                delay(50);
            }
            horizontalMotor->moveRelative(30);
            verticalMotor->moveRelative(-180.0);
            while(verticalMotor->isRunning()) {
                checkMovementConstraints();
                delay(50);
            }

            horizontalMotor->moveRelative(-180);
            verticalMotor->moveRelative(45);
            while(verticalMotor->isRunning()) {
                checkMovementConstraints();
                delay(50);
            }
            verticalMotor->moveRelative(-60);
            while(verticalMotor->isRunning()) {
                checkMovementConstraints();
                delay(50);
            }
            horizontalMotor->moveRelative(90, true);
            horizontalMotor->stopMove();
            verticalMotor->stopMove();
            

            Serial.println("Showcase not implemented yet");
        } else if (act.equals("reset_pos")){
            verticalMotor->setCurrentPosition(0);
            horizontalMotor->setCurrentPosition(0);  
        }
    }

    message[ACTION_IDX] = "";
}
