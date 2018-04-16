# simple script to extract frames from the original gifs

Get-ChildItem . -Filter *.gif | 
Foreach-Object {
    $name = $_.BaseName
    Write-Output $name
    mkdir $name
    convert -coalesce "$name.gif" "$name/%02d.png"
}
