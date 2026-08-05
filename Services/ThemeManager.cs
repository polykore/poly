using System;
using System.Linq;
using Microsoft.UI.Xaml;

namespace PolyTerminal.Services
{
    public enum PolyTheme
    {
        Default,
        Win7Aero,
        WinXPLuna
    }

    public static class ThemeManager
    {
        public static PolyTheme CurrentTheme { get; private set; } = PolyTheme.Default;

        public static void SetTheme(PolyTheme theme)
        {
            CurrentTheme = theme;
            var resources = Application.Current.Resources;
            var merged = resources.MergedDictionaries;

            // remove existing theme dictionaries
            var existingThemes = merged.Where(d => 
                d.Source != null && 
                (d.Source.ToString().Contains("Win7Aero.xaml") || d.Source.ToString().Contains("WinXPLuna.xaml"))
            ).ToList();

            foreach (var dict in existingThemes)
            {
                merged.Remove(dict);
            }

            // apply selected theme
            Uri themeUri = null;
            switch (theme)
            {
                case PolyTheme.Win7Aero:
                    themeUri = new Uri("ms-appx:///Themes/Win7Aero.xaml", UriKind.Absolute);
                    break;
                case PolyTheme.WinXPLuna:
                    themeUri = new Uri("ms-appx:///Themes/WinXPLuna.xaml", UriKind.Absolute);
                    break;
                case PolyTheme.Default:
                default:
                    // go back to standard WinUI theme
                    return;
            }

            if (themeUri != null)
            {
                var newThemeDict = new ResourceDictionary { Source = themeUri };
                merged.Add(newThemeDict);
            }
        }
    }
}
