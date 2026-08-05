using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace PolyTerminal.Services
{
    public static class PythonCommandService
    {
        public static string SearchCommandsDirectory()
        {
            string baseDir = AppContext.BaseDirectory;
            
            // check output directory
            string path1 = Path.Combine(baseDir, "commands");
            if (Directory.Exists(path1)) return Path.GetFullPath(path1);

            // check parent folder paths
            string path2 = Path.Combine(baseDir, "..", "..", "..", "..", "poly", "poly", "commands");
            if (Directory.Exists(path2)) return Path.GetFullPath(path2);

            string path3 = Path.Combine(baseDir, "..", "poly", "commands");
            if (Directory.Exists(path3)) return Path.GetFullPath(path3);

            return null;
        }

        public static bool IsPythonCommand(string cmdName)
        {
            if (string.IsNullOrWhiteSpace(cmdName)) return false;

            string cmdsDir = SearchCommandsDirectory();
            if (cmdsDir == null) return false;

            string pyFile = Path.Combine(cmdsDir, cmdName.ToLower() + ".py");
            return File.Exists(pyFile);
        }

        public static async Task RunPythonCommandAsync(string fullCommand, string currentDirectory, Action<string> onOutputReceived, string sudoPassword = null)
        {
            string[] parts = fullCommand.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length == 0) return;

            string cmdName = parts[0].ToLower();
            string cmdsDir = SearchCommandsDirectory();
            if (cmdsDir == null)
            {
                onOutputReceived?.Invoke("[Error] Could not locate 'commands' directory.\n");
                return;
            }

            string scriptPath = Path.Combine(cmdsDir, cmdName + ".py");
            if (!File.Exists(scriptPath))
            {
                onOutputReceived?.Invoke($"[Error] Python command file '{cmdName}.py' not found.\n");
                return;
            }

            string runnerPath = Path.Combine(cmdsDir, "_runner.py");
            string argsList = parts.Length > 1 ? string.Join(" ", parts, 1, parts.Length - 1) : "";

            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{runnerPath}\" {cmdName} {argsList}",
                WorkingDirectory = currentDirectory,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";

            if (!string.IsNullOrEmpty(sudoPassword))
            {
                psi.EnvironmentVariables["SUDO_PASSWORD"] = sudoPassword;
            }

            try
            {
                using (Process proc = new Process { StartInfo = psi })
                {
                    proc.OutputDataReceived += (s, e) =>
                    {
                        if (e.Data != null) onOutputReceived?.Invoke(e.Data + "\n");
                    };
                    proc.ErrorDataReceived += (s, e) =>
                    {
                        if (e.Data != null) onOutputReceived?.Invoke(e.Data + "\n");
                    };

                    proc.Start();
                    proc.BeginOutputReadLine();
                    proc.BeginErrorReadLine();

                    await proc.WaitForExitAsync();
                }
            }
            catch (Exception ex)
            {
                onOutputReceived?.Invoke($"[Python Execution Exception] {ex.Message}\n");
            }
        }
    }
}
