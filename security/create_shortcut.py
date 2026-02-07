import os
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut(target_path, shortcut_name="Quantum Spacetime System"):
    """Creates a shortcut on the user's desktop."""
    try:
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{shortcut_name}.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()
        print(f"Shortcut created at: {path}")
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False

if __name__ == "__main__":
    # In a real scenario, this would point to the installed executable
    target = os.path.abspath("install_quantum_spacetime.py") 
    create_desktop_shortcut(target)
