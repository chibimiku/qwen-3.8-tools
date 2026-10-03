param(
    [string]$ServerHost = 'connect.westd.seetacloud.com',
    [int]$SshPort = 32204,
    [string]$SshUser = 'root',
    [int]$LocalPort = 18081,
    [int]$RemotePort = 8081
)
$forward = "127.0.0.1:${LocalPort}:127.0.0.1:${RemotePort}"
& ssh.exe -N -T -p $SshPort -L $forward -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 "${SshUser}@${ServerHost}"
