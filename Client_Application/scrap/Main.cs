using System;
using System.Threading;
using System.IO.Ports;
using OpenHardwareMonitor.Hardware;

class mainclass
{
    static void Main(string[] args)
    {
        // Putting this in scrap bin since there is no "clean" way 
        // of implementing ML with C#. (Ironpython will not run Numpy)
        // Thus we need two processes and it makes more sense just to use 
        // the official release of OHM instead of IPC. 
 

        /* GPU sensor arr
              0 : GPU Core Temp      1  : GPU Fan
              2 : GPU Core Clock     3  : GPU Memory Clock
              4 : Gpu Shader Clock   5  : Gpu Shader Clock
              6 : Gpu Core Load      7  : GPU Mem Crtl Load
              8 : GPU Video Load     9  : GPU Fan Control
             10 : GPU Memory Total  11 : GPU Memory Used
             12 : GPU Memory Free   13 : GPU Memory Load

         CPU sensors arr
             Load 0-3, Total 4
             Temp 5-8, Package 9
             Clock 10-13 
         */
        Computer computerObj = new Computer();
        while(true)
        {
            computerObj.Open();
            computerObj.CPUEnabled = true;
            computerObj.GPUEnabled = true;
            for (int i=5; i<9; i++)
            {
                Console.WriteLine(string.Concat("CPU Temp: ", computerObj.Hardware[0].Sensors[i].Value));
            }
            Console.WriteLine(string.Concat("CPU Load: ", computerObj.Hardware[0].Sensors[4].Value));
            Console.WriteLine(string.Concat("GPU Temp: ", computerObj.Hardware[1].Sensors[0].Value));
            Console.WriteLine(string.Concat("GPU Load: ", computerObj.Hardware[1].Sensors[5].Value));
            Console.Write('\n');
            Thread.Sleep(2000);
            computerObj.Close();
        }
        Console.ReadLine();

    }
}