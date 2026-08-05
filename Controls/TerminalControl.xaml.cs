using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Windows.UI;
using PolyTerminal.Services;

namespace PolyTerminal.Controls
{
    public sealed partial class TerminalControl : UserControl
    {
        private string _currentCwd;
        private bool _isScrollPending = false;
        private const int MaxBufferLength = 200000;
        private bool _isAwaitingSudoPassword = false;
        private string _pendingSudoCommand = "";

        // command history support/CMH (up / down arrows)
        private List<string> _commandHistory = new List<string>();
        private int _historyIndex = -1;

        public TerminalControl()
        {
            this.InitializeComponent();
            _currentCwd = Environment.CurrentDirectory;
            
            // apply live settings
            ApplySettings();
            TerminalSettingsService.SettingsChanged += TerminalSettingsService_SettingsChanged;

            AppendOutputText($"poly terminal v5.0\ntype 'help' for commands or run any system command\n\n");

            this.Loaded += (s, e) =>
            {
                FocusInput();
            };

            this.Unloaded += (s, e) =>
            {
                TerminalSettingsService.SettingsChanged -= TerminalSettingsService_SettingsChanged;
            };
        }

        private void TerminalSettingsService_SettingsChanged()
        {
            this.DispatcherQueue.TryEnqueue(DispatcherQueuePriority.Normal, () =>
            {
                ApplySettings();
            });
        }

        private void ApplySettings()
        {
            // apply font size
            OutputTextBlock.FontSize = TerminalSettingsService.FontSize;
            PromptLabel.FontSize = TerminalSettingsService.FontSize;
            InputTextBox.FontSize = TerminalSettingsService.FontSize;
            InputPasswordBox.FontSize = TerminalSettingsService.FontSize;

            // apply font color
            try
            {
                Color color = HexToColor(TerminalSettingsService.TextColorHex);
                OutputTextBlock.Foreground = new SolidColorBrush(color);
                InputTextBox.Foreground = new SolidColorBrush(color);
                InputPasswordBox.Foreground = new SolidColorBrush(color);
            }
            catch { }

            // update prompt style
            UpdatePromptLabel();
        }

        private Color HexToColor(string hex)
        {
            hex = hex.Replace("#", "");
            byte a = 255;
            byte r = Convert.ToByte(hex.Substring(0, 2), 16);
            byte g = Convert.ToByte(hex.Substring(2, 2), 16);
            byte b = Convert.ToByte(hex.Substring(4, 2), 16);
            return Color.FromArgb(a, r, g, b);
        }

        private void UserControl_PointerPressed(object sender, PointerRoutedEventArgs e)
        {
            FocusInput();
        }

        private void FocusInput()
        {
            try
            {
                if (InputPasswordBox.Visibility == Visibility.Visible)
                {
                    InputPasswordBox.Focus(FocusState.Programmatic);
                }
                else
                {
                    InputTextBox.Focus(FocusState.Programmatic);
                }
            }
            catch { }
        }

        private void UpdatePromptLabel()
        {
            string folderName = Path.GetFileName(_currentCwd);
            if (string.IsNullOrEmpty(folderName)) folderName = _currentCwd;

            string username = Environment.UserName;

            switch (TerminalSettingsService.PromptStyleIndex)
            {
                case 1: // minimal
                    PromptLabel.Text = $"➜ ~/{folderName} ";
                    break;
                case 2: // powerline
                    PromptLabel.Text = $"⚡ {username}@poly:~/{folderName} ❯ ";
                    break;
                case 3: // linux terminal
                    PromptLabel.Text = $"[poly-engine:~/{folderName}]:$ ";
                    break;
                default: // default
                    PromptLabel.Text = $"{username}@terminal:~/{folderName} ❯ ";
                    break;
            }
        }

        private void AppendOutputText(string text)
        {
            if (string.IsNullOrEmpty(text)) return;

            // keep buffer bounded to prevent UI thread hangs on fuckin big ass output
            if (OutputTextBlock.Text.Length > MaxBufferLength)
            {
                OutputTextBlock.Text = OutputTextBlock.Text.Substring(OutputTextBlock.Text.Length - 100000);
            }

            OutputTextBlock.Text += text;

            // smooth auto-scroll handler
            if (TerminalSettingsService.IsAutoScrollEnabled && !_isScrollPending)
            {
                _isScrollPending = true;

                // adjust priority based on speed slider
                DispatcherQueuePriority priority = TerminalSettingsService.ScrollSpeed > 5 ? DispatcherQueuePriority.Normal : DispatcherQueuePriority.Low;

                this.DispatcherQueue.TryEnqueue(priority, () =>
                {
                    _isScrollPending = false;
                    OutputScrollViewer.ChangeView(null, OutputScrollViewer.ScrollableHeight, null);
                });
            }
        }

        private async void InputPasswordBox_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            if (e.Key == Windows.System.VirtualKey.Enter)
            {
                string pass = InputPasswordBox.Password;
                InputPasswordBox.Password = string.Empty;
                InputPasswordBox.Visibility = Visibility.Collapsed;
                InputTextBox.Visibility = Visibility.Visible;

                if (_isAwaitingSudoPassword)
                {
                    _isAwaitingSudoPassword = false;
                    string sudoCmd = _pendingSudoCommand;
                    _pendingSudoCommand = "";

                    AppendOutputText($"[sudo] password for {Environment.UserName}: \n");
                    UpdatePromptLabel();
                    InputTextBox.Focus(FocusState.Programmatic);

                    await PythonCommandService.RunPythonCommandAsync(sudoCmd, _currentCwd, (output) =>
                    {
                        this.DispatcherQueue.TryEnqueue(DispatcherQueuePriority.Normal, () =>
                        {
                            AppendOutputText(output);
                        });
                    }, pass);
                }
                else
                {
                    UpdatePromptLabel();
                    InputTextBox.Focus(FocusState.Programmatic);
                }

                e.Handled = true;
            }
        }

        private void InputTextBox_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            if (e.Key == Windows.System.VirtualKey.Enter)
            {
                ExecuteCommand();
                e.Handled = true;
            }
            else if (e.Key == Windows.System.VirtualKey.Up)
            {
                // command history navigation up
                if (_commandHistory.Count > 0)
                {
                    if (_historyIndex < _commandHistory.Count - 1)
                    {
                        _historyIndex++;
                        InputTextBox.Text = _commandHistory[_commandHistory.Count - 1 - _historyIndex];
                        InputTextBox.Select(InputTextBox.Text.Length, 0);
                    }
                }
                e.Handled = true;
            }
            else if (e.Key == Windows.System.VirtualKey.Down)
            {
                // command history navigation down
                if (_historyIndex > 0)
                {
                    _historyIndex--;
                    InputTextBox.Text = _commandHistory[_commandHistory.Count - 1 - _historyIndex];
                    InputTextBox.Select(InputTextBox.Text.Length, 0);
                }
                else if (_historyIndex == 0)
                {
                    _historyIndex = -1;
                    InputTextBox.Text = string.Empty;
                }
                e.Handled = true;
            }
        }

        private async void ExecuteCommand()
        {
            string command = InputTextBox.Text.Trim();
            if (string.IsNullOrWhiteSpace(command)) return;

            // add to command history
            _commandHistory.Add(command);
            _historyIndex = -1;

            InputTextBox.Text = string.Empty;

            string[] parts = command.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            string firstWord = parts.Length > 0 ? parts[0] : "";

            // auto-sudo check: if auto-sudo is enabled and command is not already sudo, prefix command with sudo
            if (TerminalSettingsService.IsAutoSudoEnabled && !firstWord.Equals("sudo", StringComparison.OrdinalIgnoreCase))
            {
                command = "sudo " + command;
                parts = command.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                firstWord = "sudo";
            }

            // handle sudo command inline linux style
            if (firstWord.Equals("sudo", StringComparison.OrdinalIgnoreCase))
            {
                if (parts.Length <= 1)
                {
                    AppendOutputText($"$ {command}\nUsage: sudo <command>\n");
                    return;
                }

                AppendOutputText($"$ {command}\n");
                _pendingSudoCommand = command;
                _isAwaitingSudoPassword = true;

                PromptLabel.Text = $"[sudo] password for {Environment.UserName}: ";
                InputTextBox.Visibility = Visibility.Collapsed;
                InputPasswordBox.Visibility = Visibility.Visible;
                InputPasswordBox.Password = string.Empty;
                InputPasswordBox.Focus(FocusState.Programmatic);
                return;
            }

            AppendOutputText($"$ {command}\n");

            // built-in directory navigation handling
            if (firstWord.Equals("cd", StringComparison.OrdinalIgnoreCase))
            {
                HandleCdCommand(parts);
                return;
            }

            if (firstWord.Equals("clear", StringComparison.OrdinalIgnoreCase) || firstWord.Equals("cls", StringComparison.OrdinalIgnoreCase))
            {
                OutputTextBlock.Text = string.Empty;
                return;
            }

            // custom python command check (sudo, newrun, curl, ls, cat, grep, etc.)
            if (PythonCommandService.IsPythonCommand(firstWord))
            {
                await PythonCommandService.RunPythonCommandAsync(command, _currentCwd, (output) =>
                {
                    this.DispatcherQueue.TryEnqueue(DispatcherQueuePriority.Normal, () =>
                    {
                        AppendOutputText(output);
                    });
                });
                return;
            }

            // system command fallback (cmd, powershell, npm, pip, git, whoami, ipconfig, etc.)
            await RunSystemCommandAsync(command);
        }

        private void HandleCdCommand(string[] parts)
        {
            string targetPath = parts.Length > 1 ? string.Join(" ", parts, 1, parts.Length - 1) : Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);

            if (targetPath == "~") targetPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);

            string fullPath = Path.IsPathRooted(targetPath) ? targetPath : Path.GetFullPath(Path.Combine(_currentCwd, targetPath));

            if (Directory.Exists(fullPath))
            {
                _currentCwd = fullPath;
                UpdatePromptLabel();
            }
            else
            {
                AppendOutputText($"cd: '{targetPath}' does not exist\n");
            }
        }

        private async Task RunSystemCommandAsync(string command)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                Arguments = $"/c {command}",
                WorkingDirectory = _currentCwd,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            try
            {
                using (Process proc = new Process { StartInfo = psi })
                {
                    proc.OutputDataReceived += (s, e) =>
                    {
                        if (e.Data != null)
                        {
                            this.DispatcherQueue.TryEnqueue(DispatcherQueuePriority.Normal, () =>
                            {
                                AppendOutputText(e.Data + "\n");
                            });
                        }
                    };
                    proc.ErrorDataReceived += (s, e) =>
                    {
                        if (e.Data != null)
                        {
                            this.DispatcherQueue.TryEnqueue(DispatcherQueuePriority.Normal, () =>
                            {
                                AppendOutputText(e.Data + "\n");
                            });
                        }
                    };

                    proc.Start();
                    proc.BeginOutputReadLine();
                    proc.BeginErrorReadLine();

                    await proc.WaitForExitAsync();
                }
            }
            catch (Exception ex)
            {
                AppendOutputText($"System execution error: {ex.Message}\n");
            }
        }

        public void TerminateSession()
        {
            // session cleanup handler
        }
    }
}


// i see you diggin into the code
// if you wanna contribute to fix anything since i know this code is probably sloppy
// go ahead, just fork the git project and send it thru and ill have a look and if its good ill use it and credit you (ofc)
// good luck :)