#define TINY_GSM_MODEM_SIM808
#include <TinyGsmClient.h>
#include <SoftwareSerial.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

//I2C LCD declaration
LiquidCrystal_I2C lcd(0x27, 16, 2);

String EC = "+918075065265";

char keys[4][3] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};

byte pin_rows[4] = {9, 8, 7, 6}; //connect to the row pinouts of the keypad
byte pin_column[3] = {5, 4, 3}; //connect to the column pinouts of the keypad

Keypad keypad = Keypad( makeKeymap(keys), pin_rows, pin_column, 4, 3 );

//Software Serial for GSM
SoftwareSerial SerialAT(10, 11); // RX, TX
TinyGsm modem(SerialAT);

String GPS_LOCATION_1_LAT  = "LAT : 8.499453";
String GPS_LOCATION_1_LONG = "LONG: 76.943891";
String GPS_LOCATION_2_LAT  = "LAT : 8.498424";
String GPS_LOCATION_2_LONG = "LONG: 76.948587";
String GPS_LOCATION_3_LAT  = "LAT : 8.499634";
String GPS_LOCATION_3_LONG = "LONG: 76.954402";

String getGPS()
{
  float lat = 0;
  float lng = 0;
  float Speed = 0;
  
  modem.getGPS(&lat, &lng);
  return "lat: "+ String(lat) + " lng: " + String(lng);
    
}

void lcdprint(String msg = "", bool clr = false, int x = 0, int y = 0)
{
  if(clr)
    lcd.clear();
  lcd.setCursor(x,y);
  lcd.print(msg);
  
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  SerialAT.begin(115200);
//  delay(3000);

  lcd.init();
  lcd.backlight();
  Serial.println("Initializing modem...");
  lcdprint("Intializing...", true);
  modem.restart();
//  delay(2000);
  lcdprint("Intialized...", true);
  delay(1000);
  lcdprint("Inmate Tracker", true);
}

void loop() {
  // put your main code here, to run repeatedly:
  char key = keypad.getKey();

  if (key)
  {
    Serial.println(key);
    switch(key)
    {
      case '1': Serial.print(GPS_LOCATION_1_LAT);
                Serial.println(GPS_LOCATION_1_LONG);
                lcdprint(GPS_LOCATION_1_LAT, true);
                lcdprint(GPS_LOCATION_1_LONG, false, 0, 1);
                delay(2000);
                Serial.println("Inmate inside jail");
                lcdprint("Inside Jail", true);
                delay(2000);
                lcdprint(GPS_LOCATION_1_LAT, true);
                lcdprint(GPS_LOCATION_1_LONG, false, 0, 1);
                break;
                
      case '2': Serial.print(GPS_LOCATION_2_LAT);
                Serial.println(GPS_LOCATION_2_LONG);
                lcdprint(GPS_LOCATION_2_LAT, true);
                lcdprint(GPS_LOCATION_2_LONG, false, 0, 1);
                delay(2000);
                Serial.println("Inmate inside jail");
                lcdprint("Inside Jail", true);
                delay(2000);
                lcdprint(GPS_LOCATION_1_LAT, true);
                lcdprint(GPS_LOCATION_1_LONG, false, 0, 1);
                break;
                
      case '3': Serial.print(GPS_LOCATION_3_LAT);
                Serial.println(GPS_LOCATION_3_LONG);
                lcdprint(GPS_LOCATION_3_LAT, true);
                lcdprint(GPS_LOCATION_3_LONG, false, 0, 1);
                delay(2000);
                Serial.println("Jail Break Detected!");
                Serial.println("Sending Alert Message to " + EC);
                lcdprint("Jail break!!!", true);
                delay(500);
                lcdprint("Sending SMS", false, 0, 1);
                delay(2000);
//                String msg = "JAIL BREAK" + GPS_LOCATION_3_LAT + GPS_LOCATION_3_LONG;
                modem.sendSMS(EC, "JAIL BREAK ");
                lcdprint(GPS_LOCATION_1_LAT, true);
                lcdprint(GPS_LOCATION_1_LONG, false, 0, 1);
                break;  
    }
  }
}
