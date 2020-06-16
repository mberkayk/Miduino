const int num_of_keys = 39;
const long delay_timer = 30;
const int starting_pin = 14;

boolean keys[num_of_keys] = {true, true};
long unsigned int timer[num_of_keys];

void setup() {
  Serial.begin(57600);
  
  for(int i = 0; i < num_of_keys; i++){
    pinMode(i+starting_pin, INPUT_PULLUP);  
  }

}

void loop() {
  for(int i = 0; i < num_of_keys; i++){
    if(millis() - delay_timer > timer[i]){
      boolean val = digitalRead(i+starting_pin);
      
      if(keys[i] == true && val== false){//pressed
        Serial.println(i);
        timer[i] = millis();
      }else if(keys[i] == false && val == true){ //released
        Serial.println(i + num_of_keys);
        timer[i] = millis();
      }
      
      keys[i] = val;
    }
  }
}
