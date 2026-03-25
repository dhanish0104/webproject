$maps = @{
    "media__1774074801899.jpg" = "trans_traffic.jpg"
    "media__1774074906021.jpg" = "trans_signal.jpg"
    "media__1774074962247.jpg" = "trans_road.jpg"
    "media__1774075005097.jpg" = "trans_bus.jpg"
    "media__1774075160728.jpg" = "housing_collapse.jpg"
    "media__1774075213941.jpg" = "housing_slum.jpg"
    "media__1774075310158.jpg" = "housing_dilapidated.jpg"
    "media__1774075385598.jpg" = "housing_encroachment.jpg"
    "media__1774075472965.jpg" = "edu_infrastructure.jpg"
    "media__1774075544219.png" = "edu_teacher.jpg"
    "media__1774075740806.png" = "elec_outage.jpg"
    "media__1774075779954.png" = "elec_voltage.jpg"
    "media__1774075821271.jpg" = "elec_transformer.jpg"
    "media__1774075845209.png" = "elec_meter.jpg"
    "media__1774075954482.png" = "elec_streetlight.jpg"
    "media__1774076786872.png" = "water_shortage.jpg"
    "media__1774076900615.png" = "water_dirty.jpg"
    "media__1774076948386.jpg" = "water_tanker.jpg"
    "media__1774076977025.jpg" = "water_leak.jpg"
    "media__1774077006951.png" = "water_drain.jpg"
    "media__1774077069458.jpg" = "water_overflow.jpg"
    "media__1774077143691.jpg" = "water_riverflow.jpg"
    "media__1774077953533.jpg" = "infra_pothole.jpg"
    "media__1774078027514.jpg" = "infra_highway.jpg"
    "media__1774078116554.jpg" = "infra_bridge.jpg"
    "media__1774078149815.png" = "infra_incomplete.jpg"
    "media__1774078183463.jpg" = "infra_flooded.jpg"
    "media__1774078450292.png" = "infra_streetlight.jpg"
    "media__1774078617933.jpg" = "infra_footpath.jpg"
    "media__1774078745618.jpg" = "infra_flyover.jpg"
    "media__1774078846831.jpg" = "infra_encroachment.jpg"
    "media__1774078995574.jpg" = "health_crowd.jpg"
    "media__1774079019903.png" = "health_ambulance.jpg"
    "media__1774079062263.jpg" = "health_beds.jpg"
    "media__1774079183575.jpg" = "waste_burning.jpg"
}

$srcDir = "C:\Users\dhani\.gemini\antigravity\brain\40dbfb65-2101-467a-8f0c-7c1cd56f97d9"
$destDir = "c:\webproject\static\images"

foreach ($key in $maps.Keys) {
    $srcFile = Join-Path $srcDir $key
    $destFile = Join-Path $destDir $maps[$key]
    if (Test-Path $srcFile) {
        Copy-Item -Path $srcFile -Destination $destFile -Force
    } 
}
