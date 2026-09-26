# Galahad Agent — Mobile Repair Skill
# Comprehensive mobile device repair, diagnostics, and maintenance

name: galahad-mobile-repair
version: "1.0.0"
description: "Mobile repair toolkit — Android/iOS diagnostics, flashing, unlocking, data recovery, and microsoldering guidance"
category: hardware
tags: [mobile-repair, android, ios, adb, fastboot, flashing, unlocking, data-recovery, microsoldering]

author: "Galahad Agent Team"
license: MIT

# Required tools (auto-checked)
requires_tools: ["mobile_repair"]

# Configuration
config:
  default_platform: "android"  # android, ios
  safety_confirmations: true
  backup_before_flash: true
  log_level: "info"

# Knowledge base structure
knowledge_base:
  android:
    partitions:
      - name: "boot"
        description: "Kernel + ramdisk"
        flashable: true
        critical: true
      - name: "dtbo"
        description: "Device tree blob overlay"
        flashable: true
        critical: false
      - name: "vbmeta"
        description: "Verified boot metadata"
        flashable: true
        critical: true
      - name: "system"
        description: "System partition (A/B)"
        flashable: true
        critical: true
      - name: "vendor"
        description: "Vendor partition"
        flashable: true
        critical: true
      - name: "recovery"
        description: "Recovery partition"
        flashable: true
        critical: false
      - name: "userdata"
        description: "User data (NOT flashable normally)"
        flashable: false
        critical: true

    modes:
      - name: "normal"
        entry: "adb reboot"
        description: "Normal Android OS"
      - name: "fastboot"
        entry: "adb reboot bootloader"
        description: "Bootloader interface for flashing"
      - name: "recovery"
        entry: "adb reboot recovery"
        description: "Recovery mode (stock/custom)"
      - name: "edl"
        entry: "Hardware key combo or test points"
        description: "Emergency Download (Qualcomm)"
      - name: "download"
        entry: "Volume Down + Power (Samsung)"
        description: "Odin/Download mode"

    tools:
      - "adb"
      - "fastboot"
      - "odin"
      - "heimdall"
      - "sp-flash-tool"
      - "mi-flash"
      - "qfil"
      - "edl-tools"
      - "mtk-bypass"
      - "avb-tool"

    common_issues:
      - symptom: "Bootloop"
        causes: ["corrupt boot", "bad magisk module", "failed OTA", "incompatible kernel"]
        diagnosis: ["adb logcat", "fastboot getvar all", "check vbmeta"]
        solutions: ["flash stock boot", "disable modules in recovery", "reflash vbmeta", "factory reset"]
      - symptom: "Brick (hard/soft)"
        causes: ["wrong firmware", "interrupted flash", "bootloader lock", "partition corruption"]
        diagnosis: ["fastboot devices", "edl mode detection", "check partition table"]
        solutions: ["EDL flash stock ROM", "JTAG", "authorized service center"]
      - symptom: "FRP Lock"
        causes: ["factory reset without account removal"]
        diagnosis: ["check Google account in settings"]
        solutions: ["FRP bypass tools", "combination firmware", "Samsung FRP tools"]

  ios:
    partitions:
      - name: "rootfs"
        description: "System root filesystem (signed)"
        flashable: false
        critical: true
      - name: "data"
        description: "User data partition"
        flashable: false
        critical: true

    modes:
      - name: "normal"
        entry: "Normal boot"
        description: "iOS OS"
      - name: "dfu"
        entry: "Hardware sequence (model dependent)"
        description: "Device Firmware Update — lowest level"
      - name: "recovery"
        entry: "Force restart + connect to computer"
        description: "iTunes/Finder restore mode"

    tools:
      - "idevice_id"
      - "ideviceinfo"
      - "ideviceinstaller"
      - "idevicebackup2"
      - "idevicesyslog"
      - "idevicediagnostics"
      - "libirecovery"
      - "futurerestore"
      - "tsschecker"
      - "checkra1n"
      - "palera1n"

    common_issues:
      - symptom: "Bootloop / Apple logo stuck"
        causes: ["failed update", "jailbreak issue", "hardware failure"]
        diagnosis: ["ideviceinfo", "check DFU entry", "syslog analysis"]
        solutions: ["force restart", "recovery restore", "futurerestore with blobs", "hardware check"]
      - symptom: "iCloud Activation Lock"
        causes: ["Find My not disabled before reset"]
        diagnosis: ["check activation status via GSX/GSMA"]
        solutions: ["original proof of purchase", "Apple support", "not bypassable legitimately"]

# Repair workflows
workflows:
  android_stock_restore:
    name: "Android Stock Firmware Restore"
    description: "Return device to factory state with official firmware"
    steps:
      - "Identify exact model + build number"
      - "Download official factory image"
      - "Extract images (boot, dtbo, vbmeta, system, vendor, etc.)"
      - "Unlock bootloader (if needed)"
      - "Flash all partitions via fastboot"
      - "Lock bootloader (optional)"
      - "Verify boot and functionality"
    warnings:
      - "Wipes all data"
      - "May void warranty"
      - "Bootloader unlock = data wipe"

  android_custom_recovery:
    name: "Install Custom Recovery (TWRP)"
    description: "Flash TWRP for backup, root, custom ROMs"
    steps:
      - "Download correct TWRP for device"
      - "Unlock bootloader"
      - "Boot TWRP temporarily: fastboot boot twrp.img"
      - "Flash TWRP permanently from within TWRP"
      - "Backup stock boot/recovery"
      - "Optional: Flash Magisk for root"
    warnings:
      - "Bootloader unlock required"
      - "AVB/vbmeta may need disabling"

  ios_restore:
    name: "iOS Restore / Update"
    description: "Clean restore or update via IPSW"
    steps:
      - "Download correct IPSW for device + iOS version"
      - "Enter Recovery or DFU mode"
      - "Restore via Finder/iTunes or futurerestore (unsigned)"
      - "Setup as new or restore backup"
    warnings:
      - "Unsigned IPSW needs SHSH blobs + futurerestore"
      - "Data loss without backup"

  data_recovery_android:
    name: "Android Data Recovery"
    description: "Recover data from broken/locked device"
    steps:
      - "Assess damage type (screen, logic board, software)"
      - "If screen broken: USB debugging + VNC/scrcpy"
      - "If software: custom recovery + backup partition"
      - "If hardware: JTAG/EDL + chip-off (advanced)"
      - "Extract: contacts, SMS, photos, app data"
    warnings:
      - "Encrypted data needs passcode"
      - "Chip-off is destructive"

  microsoldering_guide:
    name: "Microsoldering Reference"
    description: "Component-level board repair guidance"
    topics:
      - "Tools: microscope, hot air, soldering iron, multimeter, schematics"
      - "Common faults: charging IC, PMIC, audio IC, backlight, NAND"
      - "Schematic reading: block diagrams, voltage rails, signal tracing"
      - "BGA reballing: stencil, solder balls, reflow profile"
      - "Jumper wires: schematics-based trace repair"
    safety:
      - "ESD protection mandatory"
      - "Temperature control critical"
      - "Practice on donor boards first"

# Diagnostic procedures
diagnostics:
  android_health_check:
    - "adb_devices: verify connection"
    - "adb_shell: getprop ro.build.fingerprint (model/version)"
    - "adb_shell: dumpsys battery (health, capacity, temp)"
    - "adb_shell: df /data (storage)"
    - "adb_shell: cat /proc/meminfo (RAM)"
    - "adb_logcat: *:E (recent errors)"
    - "fastboot_getvar: all (bootloader status, unlock, slot)"

  ios_health_check:
    - "idevice_list: verify connection"
    - "idevice_info: model, iOS version, serial, battery, storage"
    - "idevice_diagnostics: run diagnostics suite"
    - "idevice_syslog: recent crashes/errors"

# Safety rules
safety_rules:
  - "ALWAYS backup before flashing"
  - "Verify firmware matches EXACT model + region"
  - "Never flash wrong partition (brick risk)"
  - "Bootloader unlock = data wipe — warn user"
  - "iOS: never downgrade without SHSH blobs"
  - "EDL/JTAG: last resort, can hard brick"
  - "Microsoldering: ESD safety, temperature limits"
  - "FRP/iCloud locks: only with proof of ownership"

# Integration with tutor skill
tutor_integration:
  learning_paths:
    - "android-basics → adb/fastboot → flashing → custom ROMs → root → EDL"
    - "ios-basics → dfu/recovery → restore → futurerestore → checkra1n/palera1n"
    - "microsoldering-basics → schematics → component test → BGA rework → jumper repair"
  hands_on_exercises:
    - "Flash stock firmware on test device"
    - "Install TWRP + Magisk"
    - "Extract boot.img, patch, reflash"
    - "Create/restore backup via TWRP"
    - "iOS DFU entry + restore"
    - "Read schematic, trace voltage rail"