# Prevent idle sleep while the flag file exists (SetThreadExecutionState; changes no Windows settings).
param([string]$Flag)
$sig = '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
$k = Add-Type -MemberDefinition $sig -Name Power -Namespace KeepAwake -PassThru
$ES_CONTINUOUS = [uint32]2147483648; $ES_SYSTEM_REQUIRED = [uint32]1
while (Test-Path -LiteralPath $Flag) {
    [void]$k::SetThreadExecutionState($ES_CONTINUOUS -bor $ES_SYSTEM_REQUIRED)
    Start-Sleep -Seconds 30
}
[void]$k::SetThreadExecutionState($ES_CONTINUOUS)
