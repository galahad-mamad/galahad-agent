from pathlib import Path


def test_windows_native_install_path_docs_match_installer() -> None:
    doc = Path("website/docs/user-guide/windows-native.md").read_text()
    install = Path("scripts/install.ps1").read_text()

    assert "%LOCALAPPDATA%\\galahad\\galahad-agent\\venv\\Scripts" in doc
    assert "Get-Command galahad        # should print C:\\Users\\<you>\\AppData\\Local\\galahad\\galahad-agent\\venv\\Scripts\\galahad.exe" in doc
    assert '$galahadBin = "$InstallDir\\venv\\Scripts"' in install
