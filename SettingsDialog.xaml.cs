using System;
using System.Diagnostics;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using PolyTerminal.Services;

namespace PolyTerminal
{
    public sealed partial class SettingsDialog : ContentDialog
    {
        private Window _mainWindow;

        public SettingsDialog(Window mainWindow)
        {
            this.InitializeComponent();
            _mainWindow = mainWindow;

            // load saved settings states
            AutoSudoToggle.IsOn = TerminalSettingsService.IsAutoSudoEnabled;
            AutoScrollToggle.IsOn = TerminalSettingsService.IsAutoScrollEnabled;
            ScrollSpeedSlider.Value = TerminalSettingsService.ScrollSpeed;
            SpeedLabel.Text = TerminalSettingsService.ScrollSpeed.ToString("F0");

            PromptStyleCombo.SelectedIndex = TerminalSettingsService.PromptStyleIndex;
            BackdropCombo.SelectedIndex = TerminalSettingsService.BackdropIndex;

            // map font size back to index (idk why i did this but i did so deal wid it)
            if (TerminalSettingsService.FontSize == 11) FontSizeCombo.SelectedIndex = 0;
            else if (TerminalSettingsService.FontSize == 13) FontSizeCombo.SelectedIndex = 1;
            else if (TerminalSettingsService.FontSize == 15) FontSizeCombo.SelectedIndex = 2;
            else if (TerminalSettingsService.FontSize == 18) FontSizeCombo.SelectedIndex = 3;
            else if (TerminalSettingsService.FontSize == 20) FontSizeCombo.SelectedIndex = 4;
        }

        private void AutoSudoToggle_Toggled(object sender, RoutedEventArgs e)
        {
            TerminalSettingsService.IsAutoSudoEnabled = AutoSudoToggle.IsOn;
            if (AutoSudoToggle.IsOn)
            {
                // relaunch app elevated as administrator
                try
                {
                    string exePath = Process.GetCurrentProcess().MainModule.FileName;
                    ProcessStartInfo psi = new ProcessStartInfo
                    {
                        FileName = exePath,
                        UseShellExecute = true,
                        Verb = "runas"
                    };
                    Process.Start(psi);
                    Application.Current.Exit();
                }
                catch { }
            }
        }

        private void AutoScrollToggle_Toggled(object sender, RoutedEventArgs e)
        {
            TerminalSettingsService.IsAutoScrollEnabled = AutoScrollToggle.IsOn;
            TerminalSettingsService.NotifySettingsChanged();
        }

        private void ScrollSpeedSlider_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            TerminalSettingsService.ScrollSpeed = e.NewValue;
            if (SpeedLabel != null)
            {
                SpeedLabel.Text = e.NewValue.ToString("F0");
            }
            TerminalSettingsService.NotifySettingsChanged();
        }

        private void TextColorCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (TextColorCombo == null) return;
            string hex = "#E6EDF3";
            switch (TextColorCombo.SelectedIndex)
            {
                case 0: hex = "#E6EDF3"; break; //  white
                case 1: hex = "#3FB950"; break; //  green
                case 2: hex = "#58A6FF"; break; //  blue
                case 3: hex = "#FF7B72"; break; //  red
                case 4: hex = "#D2A8FF"; break; //  violet
                case 5: hex = "#FFA657"; break; //  gold
            }
            TerminalSettingsService.TextColorHex = hex;
            TerminalSettingsService.NotifySettingsChanged();
        }

        private void FontSizeCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (FontSizeCombo == null) return;
            double size = 13.0;
            switch (FontSizeCombo.SelectedIndex)
            {
                case 0: size = 11.0; break;
                case 1: size = 13.0; break;
                case 2: size = 15.0; break;
                case 3: size = 18.0; break;
                case 4: size = 20.0; break;
            }
            TerminalSettingsService.FontSize = size;
            TerminalSettingsService.NotifySettingsChanged();
        }

        private void PromptStyleCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (PromptStyleCombo == null) return;
            TerminalSettingsService.PromptStyleIndex = PromptStyleCombo.SelectedIndex;
            TerminalSettingsService.NotifySettingsChanged();
        }

        private void BackdropCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_mainWindow == null || BackdropCombo == null) return;

            TerminalSettingsService.BackdropIndex = BackdropCombo.SelectedIndex;

            if (BackdropCombo.SelectedIndex == 0)
            {
                _mainWindow.SystemBackdrop = new Microsoft.UI.Xaml.Media.MicaBackdrop { Kind = Microsoft.UI.Composition.SystemBackdrops.MicaKind.Base };
            }
            else if (BackdropCombo.SelectedIndex == 1)
            {
                _mainWindow.SystemBackdrop = new Microsoft.UI.Xaml.Media.DesktopAcrylicBackdrop();
            }
            else if (BackdropCombo.SelectedIndex == 2)
            {
                _mainWindow.SystemBackdrop = null;
            }
        }
    }
}
