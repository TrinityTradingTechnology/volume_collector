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
const string GLOBAL_VOLUME_VARNAME = "_g_volume";
int lastRequestSecond = -1; // For tracking last second when a request was done
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers mapping
   SetIndexBuffer(0,VolumeBuffer,INDICATOR_DATA);
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

   if (GlobalVariableCheck(GLOBAL_VOLUME_VARNAME)) {
      VolumeBuffer[0] = GlobalVariableGet(GLOBAL_VOLUME_VARNAME);
   }

   return(rates_total);
  }
//+------------------------------------------------------------------+
