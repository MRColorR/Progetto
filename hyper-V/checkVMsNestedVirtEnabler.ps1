# Get all virtual machines on the Hyper-V host
$vms = Get-VM

# Loop through each virtual machine
foreach ($vm in $vms) {
    $vmName = $vm.Name

    # Get the processor information for the virtual machine
    $processor = Get-VMProcessor -VMName $vmName

    # Check if nested virtualization is enabled
    if (-not $processor.ExposeVirtualizationExtensions) {

        # Prompt to enable nested virtualization
        $promptMessage = "Nested virtualization is currently disabled for virtual machine $vmName. Do you want to enable it? (Y/N)"
        $response = Read-Host -Prompt $promptMessage

        if ($response -eq "Y") {

            # Enable nested virtualization for the virtual machine
            Set-VMProcessor -VMName $vmName -ExposeVirtualizationExtensions $true
            Write-Output "Nested virtualization has been enabled for virtual machine $vmName."
        }
    }
    else {
        Write-Output "Nested virtualization is already enabled for virtual machine $vmName."
    }
}
