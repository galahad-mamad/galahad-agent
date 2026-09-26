#!/usr/bin/env python3
"""
Galahad Agent — Mobile Repair Tools
Tools for Android/iOS device diagnostics, flashing, repair via ADB/Fastboot/idevice tools.
"""
import json
import os
import subprocess
import shlex
from typing import Dict, Any, List, Optional
from tools.registry import registry


def check_adb() -> bool:
    """Check if ADB is available."""
    try:
        subprocess.run(["adb", "version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def check_fastboot() -> bool:
    """Check if Fastboot is available."""
    try:
        subprocess.run(["fastboot", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def check_idevice() -> bool:
    """Check if libimobiledevice tools are available."""
    try:
        subprocess.run(["idevice_id", "-l"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def run_cmd(cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
    """Run a command and return structured result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Command timed out", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


# ==================== ANDROID TOOLS ====================

def adb_devices(args: dict, **kw) -> str:
    """List connected Android devices via ADB."""
    result = run_cmd(["adb", "devices", "-l"])
    if not result["success"]:
        return json.dumps({"error": "ADB not available or failed", "details": result["stderr"]})

    lines = result["stdout"].strip().split("\n")
    devices = []
    for line in lines[1:]:  # Skip header
        if line.strip() and "device" in line:
            parts = line.split()
            devices.append({
                "serial": parts[0],
                "status": parts[1] if len(parts) > 1 else "unknown",
                "model": " ".join([p for p in parts[2:] if not p.startswith("transport_id:")])
            })
    return json.dumps({"devices": devices, "count": len(devices)})


def adb_shell(args: dict, **kw) -> str:
    """Execute shell command on Android device."""
    serial = args.get("serial", "")
    command = args.get("command", "")
    if not command:
        return json.dumps({"error": "command parameter required"})

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["shell", command])

    result = run_cmd(cmd, timeout=60)
    return json.dumps(result)


def adb_install(args: dict, **kw) -> str:
    """Install APK on Android device."""
    serial = args.get("serial", "")
    apk_path = args.get("apk_path", "")
    if not apk_path or not os.path.exists(apk_path):
        return json.dumps({"error": "apk_path required and must exist"})

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["install", "-r", apk_path])

    result = run_cmd(cmd, timeout=120)
    return json.dumps(result)


def adb_uninstall(args: dict, **kw) -> str:
    """Uninstall package from Android device."""
    serial = args.get("serial", "")
    package = args.get("package", "")
    if not package:
        return json.dumps({"error": "package parameter required"})

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["uninstall", package])

    result = run_cmd(cmd, timeout=30)
    return json.dumps(result)


def adb_logcat(args: dict, **kw) -> str:
    """Get logcat from Android device."""
    serial = args.get("serial", "")
    filter_spec = args.get("filter", "*:E")  # Default: errors only
    lines = args.get("lines", 100)

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["logcat", "-d", "-t", str(lines), filter_spec])

    result = run_cmd(cmd, timeout=30)
    return json.dumps(result)


def adb_pull(args: dict, **kw) -> str:
    """Pull file from Android device."""
    serial = args.get("serial", "")
    remote = args.get("remote", "")
    local = args.get("local", "")
    if not remote or not local:
        return json.dumps({"error": "remote and local parameters required"})

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["pull", remote, local])

    result = run_cmd(cmd, timeout=60)
    return json.dumps(result)


def adb_push(args: dict, **kw) -> str:
    """Push file to Android device."""
    serial = args.get("serial", "")
    local = args.get("local", "")
    remote = args.get("remote", "")
    if not local or not remote or not os.path.exists(local):
        return json.dumps({"error": "local and remote required, local must exist"})

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["push", local, remote])

    result = run_cmd(cmd, timeout=60)
    return json.dumps(result)


def adb_reboot(args: dict, **kw) -> str:
    """Reboot Android device (normal, bootloader, recovery)."""
    serial = args.get("serial", "")
    mode = args.get("mode", "normal")  # normal, bootloader, recovery

    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    if mode != "normal":
        cmd.append("reboot")
        cmd.append(mode)
    else:
        cmd.append("reboot")

    result = run_cmd(cmd, timeout=30)
    return json.dumps(result)


def fastboot_devices(args: dict, **kw) -> str:
    """List devices in fastboot mode."""
    result = run_cmd(["fastboot", "devices"])
    if not result["success"]:
        return json.dumps({"error": "Fastboot not available", "details": result["stderr"]})

    devices = []
    for line in result["stdout"].strip().split("\n"):
        if line.strip():
            parts = line.split()
            devices.append({"serial": parts[0], "status": parts[1] if len(parts) > 1 else "fastboot"})
    return json.dumps({"devices": devices, "count": len(devices)})


def fastboot_flash(args: dict, **kw) -> str:
    """Flash partition via fastboot."""
    serial = args.get("serial", "")
    partition = args.get("partition", "")
    image = args.get("image", "")
    if not partition or not image or not os.path.exists(image):
        return json.dumps({"error": "partition and image (existing file) required"})

    cmd = ["fastboot"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["flash", partition, image])

    result = run_cmd(cmd, timeout=120)
    return json.dumps(result)


def fastboot_oem_unlock(args: dict, **kw) -> str:
    """Unlock OEM (bootloader)."""
    serial = args.get("serial", "")
    cmd = ["fastboot"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["oem", "unlock"])
    result = run_cmd(cmd, timeout=60)
    return json.dumps(result)


# ==================== iOS TOOLS ====================

def idevice_list(args: dict, **kw) -> str:
    """List connected iOS devices."""
    result = run_cmd(["idevice_id", "-l"])
    if not result["success"]:
        return json.dumps({"error": "idevice_id not available", "details": result["stderr"]})

    devices = [udid for udid in result["stdout"].strip().split("\n") if udid.strip()]
    return json.dumps({"devices": devices, "count": len(devices)})


def idevice_info(args: dict, **kw) -> str:
    """Get detailed iOS device info."""
    udid = args.get("udid", "")
    cmd = ["ideviceinfo"]
    if udid:
        cmd.extend(["-u", udid])
    result = run_cmd(cmd, timeout=30)
    if not result["success"]:
        return json.dumps(result)

    # Parse key-value output
    info = {}
    for line in result["stdout"].split("\n"):
        if ": " in line:
            k, v = line.split(": ", 1)
            info[k] = v
    return json.dumps({"success": True, "info": info})


def idevice_backup(args: dict, **kw) -> str:
    """Create iOS backup."""
    udid = args.get("udid", "")
    backup_dir = args.get("backup_dir", "")
    if not backup_dir:
        return json.dumps({"error": "backup_dir required"})

    os.makedirs(backup_dir, exist_ok=True)
    cmd = ["idevicebackup2"]
    if udid:
        cmd.extend(["-u", udid])
    cmd.extend(["backup", backup_dir])
    result = run_cmd(cmd, timeout=300)
    return json.dumps(result)


def idevice_restore(args: dict, **kw) -> str:
    """Restore iOS backup."""
    udid = args.get("udid", "")
    backup_dir = args.get("backup_dir", "")
    if not backup_dir or not os.path.exists(backup_dir):
        return json.dumps({"error": "backup_dir required and must exist"})

    cmd = ["idevicebackup2"]
    if udid:
        cmd.extend(["-u", udid])
    cmd.extend(["restore", backup_dir])
    result = run_cmd(cmd, timeout=300)
    return json.dumps(result)


def idevice_install(args: dict, **kw) -> str:
    """Install IPA on iOS device."""
    udid = args.get("udid", "")
    ipa_path = args.get("ipa_path", "")
    if not ipa_path or not os.path.exists(ipa_path):
        return json.dumps({"error": "ipa_path required and must exist"})

    cmd = ["ideviceinstaller"]
    if udid:
        cmd.extend(["-u", udid])
    cmd.extend(["-i", ipa_path])
    result = run_cmd(cmd, timeout=120)
    return json.dumps(result)


def idevice_syslog(args: dict, **kw) -> str:
    """Get iOS syslog."""
    udid = args.get("udid", "")
    cmd = ["idevicesyslog"]
    if udid:
        cmd.extend(["-u", udid])
    result = run_cmd(cmd, timeout=10)
    return json.dumps(result)


# ==================== DEVICE INFO / DIAGNOSTICS ====================

def device_battery(args: dict, **kw) -> str:
    """Get battery info (Android via ADB, iOS via idevice)."""
    platform = args.get("platform", "android")  # android, ios
    serial = args.get("serial", "")
    udid = args.get("udid", "")

    if platform == "android":
        cmd = ["adb"]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(["shell", "dumpsys", "battery"])
        result = run_cmd(cmd, timeout=30)
        if not result["success"]:
            return json.dumps(result)
        # Parse battery info
        info = {}
        for line in result["stdout"].split("\n"):
            if ": " in line:
                k, v = line.split(": ", 1)
                info[k.strip()] = v.strip()
        return json.dumps({"success": True, "platform": "android", "battery": info})
    else:
        cmd = ["ideviceinfo", "-u", udid] if udid else ["ideviceinfo"]
        cmd.extend(["-k", "BatteryCurrentCapacity", "-k", "BatteryIsCharging", "-k", "BatteryHealth"])
        result = run_cmd(cmd, timeout=30)
        return json.dumps(result)


def device_storage(args: dict, **kw) -> str:
    """Get storage info."""
    platform = args.get("platform", "android")
    serial = args.get("serial", "")
    udid = args.get("udid", "")

    if platform == "android":
        cmd = ["adb"]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(["shell", "df", "/data"])
        result = run_cmd(cmd, timeout=30)
        return json.dumps(result)
    else:
        # iOS storage via ideviceinfo
        cmd = ["ideviceinfo", "-k", "TotalDataCapacity", "-k", "TotalDataAvailable"]
        if udid:
            cmd.insert(1, "-u")
            cmd.insert(2, udid)
        result = run_cmd(cmd, timeout=30)
        return json.dumps(result)


def device_apps(args: dict, **kw) -> str:
    """List installed apps."""
    platform = args.get("platform", "android")
    serial = args.get("serial", "")
    udid = args.get("udid", "")
    system = args.get("system", False)

    if platform == "android":
        cmd = ["adb"]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(["shell", "pm", "list", "packages"])
        if not system:
            cmd.append("-3")  # third-party only
        result = run_cmd(cmd, timeout=30)
        if not result["success"]:
            return json.dumps(result)
        packages = [line.replace("package:", "").strip() for line in result["stdout"].split("\n") if line.startswith("package:")]
        return json.dumps({"success": True, "platform": "android", "packages": packages, "count": len(packages)})
    else:
        cmd = ["ideviceinstaller", "-l"]
        if udid:
            cmd.insert(1, "-u")
            cmd.insert(2, udid)
        result = run_cmd(cmd, timeout=30)
        return json.dumps(result)


# ==================== REGISTRATION ====================

# Android tools
registry.register(
    name="adb_devices",
    toolset="mobile_repair",
    schema={"name": "adb_devices", "description": "List connected Android devices via ADB", "parameters": {"type": "object", "properties": {}}},
    handler=adb_devices,
    check_fn=check_adb,
)

registry.register(
    name="adb_shell",
    toolset="mobile_repair",
    schema={"name": "adb_shell", "description": "Execute shell command on Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "command": {"type": "string"}}, "required": ["command"]}},
    handler=adb_shell,
    check_fn=check_adb,
)

registry.register(
    name="adb_install",
    toolset="mobile_repair",
    schema={"name": "adb_install", "description": "Install APK on Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "apk_path": {"type": "string"}}, "required": ["apk_path"]}},
    handler=adb_install,
    check_fn=check_adb,
)

registry.register(
    name="adb_uninstall",
    toolset="mobile_repair",
    schema={"name": "adb_uninstall", "description": "Uninstall package from Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "package": {"type": "string"}}, "required": ["package"]}},
    handler=adb_uninstall,
    check_fn=check_adb,
)

registry.register(
    name="adb_logcat",
    toolset="mobile_repair",
    schema={"name": "adb_logcat", "description": "Get logcat from Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "filter": {"type": "string", "default": "*:E"}, "lines": {"type": "integer", "default": 100}}}},
    handler=adb_logcat,
    check_fn=check_adb,
)

registry.register(
    name="adb_pull",
    toolset="mobile_repair",
    schema={"name": "adb_pull", "description": "Pull file from Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "remote": {"type": "string"}, "local": {"type": "string"}}, "required": ["remote", "local"]}},
    handler=adb_pull,
    check_fn=check_adb,
)

registry.register(
    name="adb_push",
    toolset="mobile_repair",
    schema={"name": "adb_push", "description": "Push file to Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "local": {"type": "string"}, "remote": {"type": "string"}}, "required": ["local", "remote"]}},
    handler=adb_push,
    check_fn=check_adb,
)

registry.register(
    name="adb_reboot",
    toolset="mobile_repair",
    schema={"name": "adb_reboot", "description": "Reboot Android device", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "mode": {"type": "string", "enum": ["normal", "bootloader", "recovery"], "default": "normal"}}}},
    handler=adb_reboot,
    check_fn=check_adb,
)

# Fastboot tools
registry.register(
    name="fastboot_devices",
    toolset="mobile_repair",
    schema={"name": "fastboot_devices", "description": "List devices in fastboot mode", "parameters": {"type": "object", "properties": {}}},
    handler=fastboot_devices,
    check_fn=check_fastboot,
)

registry.register(
    name="fastboot_flash",
    toolset="mobile_repair",
    schema={"name": "fastboot_flash", "description": "Flash partition via fastboot", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}, "partition": {"type": "string"}, "image": {"type": "string"}}, "required": ["partition", "image"]}},
    handler=fastboot_flash,
    check_fn=check_fastboot,
)

registry.register(
    name="fastboot_oem_unlock",
    toolset="mobile_repair",
    schema={"name": "fastboot_oem_unlock", "description": "Unlock OEM bootloader", "parameters": {"type": "object", "properties": {"serial": {"type": "string"}}}},
    handler=fastboot_oem_unlock,
    check_fn=check_fastboot,
)

# iOS tools
registry.register(
    name="idevice_list",
    toolset="mobile_repair",
    schema={"name": "idevice_list", "description": "List connected iOS devices", "parameters": {"type": "object", "properties": {}}},
    handler=idevice_list,
    check_fn=check_idevice,
)

registry.register(
    name="idevice_info",
    toolset="mobile_repair",
    schema={"name": "idevice_info", "description": "Get detailed iOS device info", "parameters": {"type": "object", "properties": {"udid": {"type": "string"}}}},
    handler=idevice_info,
    check_fn=check_idevice,
)

registry.register(
    name="idevice_backup",
    toolset="mobile_repair",
    schema={"name": "idevice_backup", "description": "Create iOS backup", "parameters": {"type": "object", "properties": {"udid": {"type": "string"}, "backup_dir": {"type": "string"}}, "required": ["backup_dir"]}},
    handler=idevice_backup,
    check_fn=check_idevice,
)

registry.register(
    name="idevice_restore",
    toolset="mobile_repair",
    schema={"name": "idevice_restore", "description": "Restore iOS backup", "parameters": {"type": "object", "properties": {"udid": {"type": "string"}, "backup_dir": {"type": "string"}}, "required": ["backup_dir"]}},
    handler=idevice_restore,
    check_fn=check_idevice,
)

registry.register(
    name="idevice_install",
    toolset="mobile_repair",
    schema={"name": "idevice_install", "description": "Install IPA on iOS device", "parameters": {"type": "object", "properties": {"udid": {"type": "string"}, "ipa_path": {"type": "string"}}, "required": ["ipa_path"]}},
    handler=idevice_install,
    check_fn=check_idevice,
)

registry.register(
    name="idevice_syslog",
    toolset="mobile_repair",
    schema={"name": "idevice_syslog", "description": "Get iOS syslog", "parameters": {"type": "object", "properties": {"udid": {"type": "string"}}}},
    handler=idevice_syslog,
    check_fn=check_idevice,
)

# Diagnostics
registry.register(
    name="device_battery",
    toolset="mobile_repair",
    schema={"name": "device_battery", "description": "Get battery info", "parameters": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["android", "ios"], "default": "android"}, "serial": {"type": "string"}, "udid": {"type": "string"}}}},
    handler=device_battery,
    check_fn=lambda: check_adb() or check_idevice(),
)

registry.register(
    name="device_storage",
    toolset="mobile_repair",
    schema={"name": "device_storage", "description": "Get storage info", "parameters": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["android", "ios"], "default": "android"}, "serial": {"type": "string"}, "udid": {"type": "string"}}}},
    handler=device_storage,
    check_fn=lambda: check_adb() or check_idevice(),
)

registry.register(
    name="device_apps",
    toolset="mobile_repair",
    schema={"name": "device_apps", "description": "List installed apps", "parameters": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["android", "ios"], "default": "android"}, "serial": {"type": "string"}, "udid": {"type": "string"}, "system": {"type": "boolean", "default": False}}}},
    handler=device_apps,
    check_fn=lambda: check_adb() or check_idevice(),
)