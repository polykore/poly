using System;
using System.Runtime.InteropServices;
using System.Text;

namespace PolyTerminal.NativeInterop
{
    public static class NativeMethods
    {
        private const string DllName = "poly_engine.dll";

        [UnmanagedFunctionPointer(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void OutputCallback([MarshalAs(UnmanagedType.LPStr)] string data, uint bytesRead);

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        public struct SystemInfo
        {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string osName;
            public uint dwBuildNumber;
            public uint dwMajorVersion;
            public uint dwMinorVersion;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)]
            public string cpuModel;
            public ulong totalRamMB;
            public ulong availRamMB;
            public ulong uptimeSeconds;
        }

        // process spawner P/Invokes
        [DllImport(DllName, CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Ansi, SetLastError = true)]
        public static extern IntPtr LaunchProcess(
            [MarshalAs(UnmanagedType.LPStr)] string command,
            [MarshalAs(UnmanagedType.Bool)] bool isElevated,
            [MarshalAs(UnmanagedType.LPStr)] string compatLayer,
            OutputCallback callback
        );

        [DllImport(DllName, CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Ansi, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool WriteProcessInput(
            IntPtr session,
            [MarshalAs(UnmanagedType.LPStr)] string inputData,
            uint length
        );

        [DllImport(DllName, CallingConvention = CallingConvention.StdCall, SetLastError = true)]
        public static extern void CloseProcessSession(IntPtr session);

        // native system fetch P/Invokes
        [DllImport(DllName, CallingConvention = CallingConvention.StdCall, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool GetSystemInfoData(out SystemInfo info);

        [DllImport(DllName, CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Ansi, SetLastError = true)]
        public static extern void FormatSystemInfoAscii(ref SystemInfo info, StringBuilder buffer, UIntPtr bufferSize);
    }
}
