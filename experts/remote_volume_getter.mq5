//+------------------------------------------------------------------+
//|                                               volume_request.mq5 |
//|                                                     Trinity Tech |
//|                                             https://trinity.tech |
//+------------------------------------------------------------------+
#include <JAson.mqh>

#property copyright "Trinity Tech"
#property link      "https://trinity.tech"
#property version   "1.00"

//--- input parameters
input string   URL = "http://127.0.0.1/volume";
input string   SECURITY_TOKEN = "";
input int      PERIOD = 15;
input string   TV_SYMBOL = "NDX";
input int      TIMEZONE_OFFSET = 3;

//--- variables
const string GLOBAL_VOLUME_VARNAME = "_g_volume";
datetime lastBarTime = 0;
int lastRequestSecond = -1; // For tracking last second when a request was done

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- create timer
   EventSetTimer(1);

// Init the global volume variable
   GlobalVariableSet(GLOBAL_VOLUME_VARNAME, 0);

   Print("Period: ", _Period);
   Print("Getting volume from: ", URL);

//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert timer function                                            |
//+------------------------------------------------------------------+
void OnTimer(void)
  {
   MqlDateTime lastTimeStruct;
   TimeToStruct(TimeCurrent(), lastTimeStruct);
   int currentSecond = lastTimeStruct.sec;

   if (currentSecond % PERIOD == 0) {
      Print("OnTimer: ", TimeCurrent());
      CollectRemoteVolumeAndUpdateGlobalVariable();
   }
  }
//+------------------------------------------------------------------+
//| Collect the remote volume and update global variable             |
//+------------------------------------------------------------------+
void CollectRemoteVolumeAndUpdateGlobalVariable()
  {

   PrintPreviousCandleVolume();
   ResetVolumeAtEveryCandle();

   // Request parameters
   string method = "GET";    // Request HTTP method
   string headers = "";      // Request header
   char data[];              // Body of the request
   string jsonResponse;      // Response data received as a string

   // Make the request to remote source
   MqlDateTime now{};
   TimeCurrent(now);

   string _url = StringFormat("%s/%s/%i/%i?token=%s",
       URL, TV_SYMBOL, now.hour + TIMEZONE_OFFSET, now.min, SECURITY_TOKEN);
   Print("Request to: ", _url);

   int status_code = RequestVolume(method,_url,headers,data,jsonResponse);

   // Parse response as JSON accessible object
   CJAVal response;
   response.Deserialize(jsonResponse);
   // Print("Original response: ", jsonResponse);

   // Extract from JSON string the volume value
   double newVol = response["data"].ToDbl();

   // Accumulate the received volume with the previous one requested
   double previousVol = GlobalVariableGet(GLOBAL_VOLUME_VARNAME);
   GlobalVariableSet(GLOBAL_VOLUME_VARNAME, newVol);

   Print("RESPONSE: ", jsonResponse);
  }
//+------------------------------------------------------------------+
//| Request volume to remote URL
//+------------------------------------------------------------------+
int RequestVolume(const string method, const string url, const string headers, char &data[], string &resp)
  {
   string cookie = NULL;
   char result[];               // Data received as an array of type char
   string result_headers;       // String with response headers
   int timeout = 5000;
   int dataSize = ArraySize(data);

//--- Send a web request
   int res = WebRequest(method, url, cookie, headers, timeout, data, dataSize, result, result_headers);

//--- Check for errors
   if(res == -1)
     {
      Print("Web request failed, error: ", GetLastError());
     }
   else
     {
      resp = CharArrayToString(result);
     }

   return res;
  }
//+------------------------------------------------------------------+
//| Print the previous candle volume
//+------------------------------------------------------------------+
void PrintPreviousCandleVolume()
{
// Get current candle time
   static datetime currentBarTime = iTime(_Symbol, _Period, 0);

// Compare candle times
   if(currentBarTime != lastBarTime)
     {
      // New candle started: DO SOMETHING  WITH THAT!
      PrintFormat("Candle time: %s | Candle volume: %i",
          TimeToString(currentBarTime - _Period),
          GlobalVariableGet(GLOBAL_VOLUME_VARNAME));

      // Update time of last candle
      lastBarTime = currentBarTime;
     }
}
//+------------------------------------------------------------------+
//| Reset volume global variable at every new candle
//+------------------------------------------------------------------+
void ResetVolumeAtEveryCandle()
  {
// Reset volume at every new candle
   if(IsNewBar())
     {
      // Reset the volume global variable
      GlobalVariableSet(GLOBAL_VOLUME_VARNAME, 0);
     }
  }
//+------------------------------------------------------------------+
bool IsNewBar()
  {
// Memorize the time of opening of the last bar in the static variable
   static datetime _last_time = 0;

// Current time
   datetime lastbar_time = (datetime)SeriesInfoInteger(Symbol(), Period(), SERIES_LASTBAR_DATE);

// If it is the first call of the function
   if(_last_time == 0)
     {
      // Set the time and exit
      _last_time = lastbar_time;
      return(false);
     }

// If the time differs
   if(_last_time != lastbar_time)
     {
      // Memorize the time and return true
      _last_time = lastbar_time;
      return(true);
     }

// If we passed to this line, then the bar is not new
   return(false);
  }
//+------------------------------------------------------------------+
