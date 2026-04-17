$dll = "C:\Program Files\TrustedLibs\Student\Student.dll"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class Native {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern IntPtr LoadLibrary(string lpFileName);
}
"@

[Native]::LoadLibrary($dll)