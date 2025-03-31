//+------------------------------------------------------------------+
//|                                                     real_vol.mq5 |
//|                                                     Trinity Tech |
//|                                             https://trinity.tech |
//+------------------------------------------------------------------+
#property copyright "Trinity Tech"
#property link      "https://trinity.tech"
#property version   "1.00"
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

//--- plot Volume
#property indicator_label1  "Volume"
#property indicator_type1   DRAW_HISTOGRAM
#property indicator_color1  clrRed
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1

//--- indicator buffers
double         VolumeBuffer[];

//--- variables
const string CURRENT_VOLUME = "_g_volume";
const string LAST_VOLUME = "_g_last_volume";

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers mapping
   SetIndexBuffer(0,VolumeBuffer,INDICATOR_DATA);
   IndicatorSetString(INDICATOR_SHORTNAME, StringFormat("Remote %s Volume: ", _Symbol));
   IndicatorSetInteger(INDICATOR_DIGITS, 0); // Set display digits to 0

   ArraySetAsSeries(VolumeBuffer, true);
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
//---
   
   static int bufferResetCount = 0;

// Avoid some garbage data that sometimes populate empty arrays
   if(bufferResetCount == 0)
   {
      bufferResetCount = 1;
      ArrayInitialize(VolumeBuffer, 0);
   }


   if (GlobalVariableCheck(CURRENT_VOLUME)) {
      VolumeBuffer[0] = GlobalVariableGet(CURRENT_VOLUME);
      double temp = GlobalVariableGet(LAST_VOLUME);
      if (VolumeBuffer[1] != temp)
         VolumeBuffer[1] = temp;
   }

   return(rates_total);
  }

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
