#define BLYNK_PRINT Serial

#define TINY_GSM_MODEM_SIM808

#define BLYNK_HEARTBEAT 8

#include <TinyGsmClient.h>
#include <BlynkSimpleTinyGSM.h>

//char auth[] = "INuDSNdD9Gb7DX3PjWMn-QfjW3SaYy3Q";
char auth[]  = "Z1vgcUNL8-MoM96w2Cx_4-KZdGxN8i_H";

// GPRS credentials
char apn[]  = "airtelgprs.com";
char user[] = "";
char pass[] = "";

// Define the phone number to which the alert message is to be send
String PhNo = "+919400056322";

#include <SoftwareSerial.h>
SoftwareSerial SerialAT(3, 2); // RX, TX

TinyGsm modem(SerialAT);
WidgetMap mymap(V0);

float CLAT = 8.489536530804937;
float CLNG = 76.96886048251929;

float GPS_LOCATION_LAT[] =  { 8.490088316878953,
                              8.488618654136234,
                              8.490995578815479
  };
float GPS_LOCATION_LONG[] = { 76.96865663463306,
                              76.9690053218159,
                              76.96963832313622
  };
  
int key = 0;
long int GPSprevMillis = 0;

const int inmateID = 1;
const int statusLED = 6;

#define Xpin A1
#define Ypin A2
#define Zpin A3


const int GPSintv = 10000;


const int radiusThresh = 2.5;

const int accThresh = 650;

const double DE2RA = 0.01745329252;
const double AVG_ERAD = 6371.0;


float lat = 0;
float lng = 0;

int X= 0, Y = 0, Z= 0;

void sendGPS(float lati, float lngi)
{
  Blynk.virtualWrite(V2, lati);
  Blynk.virtualWrite(V3, lngi);
  int index = (key == -1) ? 1 : 2;
  mymap.location(index, lati, lngi, String("Here!"));
}

void getGPS()
{
  if (key == -1)
  {       
    modem.getGPS(&lat, &lng);
  }
  else
  {       
    lat = GPS_LOCATION_LAT[key];
    lng = GPS_LOCATION_LONG[key];
  } 
}

BLYNK_CONNECTED() {
  digitalWrite(statusLED,HIGH);
}

void setup()
{
  pinMode(statusLED, OUTPUT);
  pinMode(Xpin, INPUT);
  pinMode(Ypin, INPUT);
  pinMode(Zpin, INPUT);
  
  Serial.begin(9600);
  delay(10);

  SerialAT.begin(9600);
  delay(3000);

  Serial.println("Initializing modem...");
  modem.restart();
  modem.enableGPS();
  delay(1500);


  Blynk.begin(auth, modem, apn, user, pass);
  GPSprevMillis = millis();
}

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
  
  X = analogRead(Xpin);
  Y = analogRead(Ypin);
  Z = analogRead(Zpin);

  Serial.print("X : ");
  Serial.print(X);
  Serial.print("Y: ");
  Serial.print(Y);
  Serial.print("Z : ");
  Serial.println(Z);

  if ((X > accThresh) || (Y > accThresh) || (Z > accThresh))
  {
    Serial.println("Jail Break Attempt"); 
    Blynk.notify("Jail Break Attempt by " + String(inmateID));
   }
     
  if ((millis() - GPSprevMillis) >= GPSintv)
  {
    getGPS();
    Serial.print("KEY: " + String(key));
    Serial.println(" LAT: " + String(lat) + " LNG: " + String(lng));

    sendGPS(lat,lng);
    if ((lat != 0) && (lng != 0))
    {
      double radius = GCDistance(CLAT, CLNG, lat, lng);
      Serial.println("Distance : " + String(radius));

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
    GPSprevMillis = millis();
  }
}
