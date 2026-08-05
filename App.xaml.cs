using Microsoft.UI.Xaml;
using System;
using System.IO;

namespace PolyTerminal
{
    public partial class App : Application
    {
        private Window _mainWindow;

        public App()
        {
            this.InitializeComponent();
            this.UnhandledException += App_UnhandledException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
        }

        private void CurrentDomain_UnhandledException(object sender, System.UnhandledExceptionEventArgs e)
        {
            try
            {
                File.WriteAllText(Path.Combine(AppContext.BaseDirectory, "crash.log"), $"UnhandledDomainException: {e.ExceptionObject}");
            }
            catch { }
        }

        private void App_UnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
        {
            try
            {
                File.WriteAllText(Path.Combine(AppContext.BaseDirectory, "crash.log"), $"UnhandledException: {e.Message}\n{e.Exception}\n{e.Exception?.StackTrace}");
            }
            catch { }
            e.Handled = true;
        }

        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            try
            {
                _mainWindow = new MainWindow();
                _mainWindow.Activate();
            }
            catch (Exception ex)
            {
                File.WriteAllText(Path.Combine(AppContext.BaseDirectory, "crash.log"), $"OnLaunched Exception: {ex.Message}\n{ex.StackTrace}");
            }
        }
    }
}
