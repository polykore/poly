using System;

namespace PolyTerminal.Services
{
    public static class TerminalSettingsService
    {
        public static bool IsAutoSudoEnabled { get; set; } = false;
        public static bool IsAutoScrollEnabled { get; set; } = true;
        public static double ScrollSpeed { get; set; } = 5.0; // 1 to 10 scale
        public static string TextColorHex { get; set; } = "#E6EDF3";
        public static double FontSize { get; set; } = 13.0;
        public static int PromptStyleIndex { get; set; } = 0; // 0: default, 1: minimal, 2: powerline, 3: linux
        public static int BackdropIndex { get; set; } = 0;

        public static event Action SettingsChanged;

        public static void NotifySettingsChanged()
        {
            SettingsChanged?.Invoke();
        }
    }
}
