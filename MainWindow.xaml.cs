using System;
using System.IO;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using PolyTerminal.Controls;

namespace PolyTerminal
{
    public sealed partial class MainWindow : Window
    {
        private int _tabCounter = 1;

        public MainWindow()
        {
            this.InitializeComponent();
            
            // set window & taskbar icon
            try
            {
                string iconPath = Path.Combine(AppContext.BaseDirectory, "app_icon.ico");
                if (File.Exists(iconPath))
                {
                    this.AppWindow.SetIcon(iconPath);
                }
            }
            catch { }

            // set mica backdrop safely
            try
            {
                this.SystemBackdrop = new MicaBackdrop { Kind = Microsoft.UI.Composition.SystemBackdrops.MicaKind.Base };
            }
            catch { }

            // extend content into title bar natively   
            try
            {
                this.ExtendsContentIntoTitleBar = true;
            }
            catch { }

            // hook window level keyboard shortcuts (ctrl + alt + s for settings)
            try
            {
                if (this.Content is FrameworkElement rootElement)
                {
                    rootElement.KeyDown += MainWindow_KeyDown;
                }
            }
            catch { }

            // create initial terminal tab
            AddNewTerminalTab("Terminal 1");
        }

        private void MainWindow_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            // shortcut: ctrl + alt + s -> open settings
            bool isCtrlPressed = Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(Windows.System.VirtualKey.Control).HasFlag(Windows.UI.Core.CoreVirtualKeyStates.Down);
            bool isAltPressed = Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(Windows.System.VirtualKey.Menu).HasFlag(Windows.UI.Core.CoreVirtualKeyStates.Down);

            if (e.Key == Windows.System.VirtualKey.S && isCtrlPressed && isAltPressed)
            {
                OpenSettingsDialog();
                e.Handled = true;
            }
        }

        private void SettingsButton_Click(object sender, RoutedEventArgs e)
        {
            OpenSettingsDialog();
        }

        private async void OpenSettingsDialog()
        {
            try
            {
                if (this.Content is FrameworkElement root && root.XamlRoot != null)
                {
                    var dialog = new SettingsDialog(this)
                    {
                        XamlRoot = root.XamlRoot
                    };
                    await dialog.ShowAsync();
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Settings dialog error: {ex.Message}");
            }
        }

        private void MainTabView_AddTabButtonClick(TabView sender, object args)
        {
            _tabCounter++;
            AddNewTerminalTab($"Terminal {_tabCounter}");
        }

        private void AddNewTerminalTab(string headerTitle)
        {
            var terminalControl = new TerminalControl();
            var tabItem = new TabViewItem
            {
                Header = headerTitle,
                IconSource = new FontIconSource { Glyph = "\uE756" }, // terminal icon
                Content = terminalControl
            };

            MainTabView.TabItems.Add(tabItem);
            MainTabView.SelectedItem = tabItem;
        }

        private void MainTabView_TabCloseRequested(TabView sender, TabViewTabCloseRequestedEventArgs args)
        {
            if (args.Item is TabViewItem tabItem)
            {
                if (tabItem.Content is TerminalControl terminalControl)
                {
                    terminalControl.TerminateSession();
                }
                MainTabView.TabItems.Remove(tabItem);
            }

            // ensure at least one tab remains open
            if (MainTabView.TabItems.Count == 0)
            {
                _tabCounter = 1;
                AddNewTerminalTab("Terminal 1");
            }
        }
    }
}


// if ur wondering yes i 3d rendered the logo/icon and no my pc didnt like it since there was like 5 million fucking polygons 
// im not even playin i might actually add the .blend to a random release or even the main branch so yall can see lmao