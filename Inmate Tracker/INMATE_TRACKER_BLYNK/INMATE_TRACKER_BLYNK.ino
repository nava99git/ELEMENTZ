/* This the code for the Inmate Tracker Project*/
/* Comment this out to disable prints and save space */
#define BLYNK_PRINT Serial

// Define your modem:
#define TINY_GSM_MODEM_SIM808

// Default heartbeat interval for GSM is 60
// If you want override this value, uncomment and set this option:
#define BLYNK_HEARTBEAT 8

#include <TinyGsmClient.h>
#include <BlynkSimpleTinyGSM.h>

// Blynk AUTH Token
char auth[] = "INuDSNdD9Gb7DX3PjWMn-QfjW3SaYy3Q";

// GPRS credentials
char apn[]  = "airtelgprs.com";
char user[] = "";
char pass[] = "";

// Define the phone number to which the alert message is to be send
String PhNo = "+918075065265";

// Software Serial for the GSM module
#include <SoftwareSerial.h>
SoftwareSerial SerialAT(3, 2); // RX, TX

// Intialize the GSM library
TinyGsm modem(SerialAT);
// Define the Blynk map widget
WidgetMap mymap(V0);

// Centre coordinates of the jail
float CLAT = 8.489536530804937;
float CLNG = 76.96886048251929;
// Some test coordinates
float GPS_LOCATION_LAT[] =  { 8.490088316878953,
                              8.488618654136234,
                              8.490995578815479
  };
float GPS_LOCATION_LONG[] = { 76.96865663463306,
                              76.9690053218159,
                              76.96963832313622
  };
  
// variables for program to function
int key = 0;
long int prevMillis = 0;

//Define the inmate ID to who the tracker belongs to
const int inmateID = 1;
// Define the in-built LED pin for the E-Tracker module
const int statusLED = 6;
// Define the GPS interval
const int GPSintv = 10000;
// Define the perimeter radius
const int radiusThresh = 2.5;

// Variables needed for GCD calculation
const double DE2RA = 0.01745329252;
const double AVG_ERAD = 6371.0;

// variables used for latittude and longitude values
float lat = 0;
float lng = 0;

// Send the GPS coordinates the blynk app
void sendGPS(float lati, float lngi)
{
  Blynk.virtualWrite(V2, lati);
  Blynk.virtualWrite(V3, lngi);
  int index = (key == -1) ? 1 : 2;
  mymap.location(index, lati, lngi, String("Here!"));
}

// get the appropriate GPS coordinates
void getGPS()
{
  if (key == -1)
  {       
    // Get the live GPS coordinates
    modem.getGPS(&lat, &lng);
  }
  else
  {       
    // Use one of the test coordinates
    lat = GPS_LOCATION_LAT[key];
    lng = GPS_LOCATION_LONG[key];
  } 
}

// Function to run once the device connects to blynk
BLYNK_CONNECTED() {
  //Turn the status led ON once connected to blynk server
  digitalWrite(statusLED,HIGH);
}

void setup()
{
  // Set the status LED as Output
  pinMode(statusLED, OUTPUT);
  
  // Debug console
  Serial.begin(9600);
  delay(10);

  // Set GSM module baud rate
  SerialAT.begin(9600);
  delay(3000);

  //Intializing GSM Modem
  Serial.println("Initializing modem...");
  modem.restart();
  modem.enableGPS();
  delay(1500);

  // Connect to Blynk
  Blynk.begin(auth, modem, apn, user, pass);
  prevMillis = millis();
}

// Function to calculate the Great Circle Distance between two points
double GCDistance(double lat1, double lon1, double lat2, double lon2)
{
   lat1 *= DE2RA;
   lon1 *= DE2RA;
   lat2 *= DE2RA;
   lon2 *= DE2RA;
   double d = sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1 - lon2);
   return (AVG_ERAD * acos(d));
}

void loop()
{ 
  Blynk.run();

  //Check whether the time since last trigger reached set GPS interval
  if ((millis() - prevMillis) >= GPSintv)
  {
    // Get the GPS Coordinates
    getGPS();
    Serial.print("KEY: " + String(key));
    Serial.println(" LAT: " + String(lat) + " LNG: " + String(lng));
    // Send the obtained coordinates to Blynk
    sendGPS(lat,lng);
    if ((lat != 0) && (lng != 0))
    {
      // Find the current radius
      double radius = GCDistance(CLAT, CLNG, lat, lng);
      Serial.println("Distance : " + String(radius));

      // Check whether the test coordinated exceedes the set radius threshold
      if ((radius > radiusThresh) && (key != -1))
      {
        Serial.println("Jailbreak detected!!!");
        String msg = "Jailbreak by Inmate " + String(inmateID);
        Blynk.notify(msg);
        modem.sendSMS(PhNo, msg);
      }
      else
      {
        if (key == -1)
          Serial.println("Live Location!");
        else
          Serial.println("Inmate inside perimeter");  
      } 
    }
    
    key = (key == 2) || (key == -1) ? key=-1 : key +1;
    prevMillis = millis();
  }
}
