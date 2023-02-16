Get-VM | ForEach-Object {
    $vmName = $_.Name
    $processor = Get-VMProcessor -VMName $vmName
    $nested = $processor.ExposeVirtualizationExtensions
    [pscustomobject]@{
        VMName = $vmName
        NestedVirtualization = $nested
    }
}
