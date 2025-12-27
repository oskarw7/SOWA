#DEFINE DEFAULT_STEP_DEG 1.8 // 1 step is equal to 1.8 degrees
#DEFINE FULL_SPIN_DEG 360

// Horizontal motor
#DEFINE HDirPin 10
#DEFINE HPulPin 11
#DEFINE HRatio 1.53125
#DEFINE HEXP 0

// Vertical motor
#DEFINE VDirPin 12
#DEFINE VPulPin 13
#DEFINE VRatio 1.79675
#DEFINE VEXP 0

struct constraint_t {
	double low;
	double high;
};

class StepperMotor {
	private:
		byte directionPin;
		byte movePin;

		byte directionState; // idk yet

		long stepsCounter;

		double stepSize; // degrees
		
		constraint_t movementRange;

	public:
	  	StepperMotor(byte drP, byte mvP, int stepSizeExp, double gearRatio, double rLow = 0, double rHigh = 0) {
			directionState = HIGH;
			stepsCounter = 0;
			movementRange.low = rLow;
			movementRange.high = rHigh;
							

			stepSize = DEFAULT_STEP_DEG / (1L << stepSizeExp) * gearRatio;
			
	  		directionPin = drP;
	  		pinMode(directionPin, OUTPUT);
			digitalWrite(dirPin, directionState);		
			
			movePin = mvP
			pinMode(movePin, OUTPUT);
		}

	void checkMoveViable(){
		return;
	}

	void move() {
		digitalWrite(movePin, HIGH);
		delayMicroseconds(10);
		digitalWrite(movePin, LOW);
		stepsCounter += (directionState == HIGH ? 1 : -1);
	}

	void changeDirection() {
		directionState = (directionState == HIGH ? LOW : HIGH);
		digitalWrite(directionPin, directionState);
	}

	void spin360() {
		int totalSteps = FULL_SPIN_DEG/stepSize;
		for(int i = 0; i < totalSteps; ++i){
			this->move();
			delay(1); // wait for the motor to move
		}
	}
};


StepperMotor horizontalMotor(HDirPin, HPulPin, HEXP, HRatio);
StepperMotor verticalMotor(VDirPin, VPulPin, VEXP, VRatio);

void setup() {
  // Constructors handle setup
}

void loop() {
  // showcase
  
}
