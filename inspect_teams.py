
import logging
from pywinauto import Desktop

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

MAX_MESSAGES = 100

def get_teams_window():
    """Mencari jendela Teams secara dinamis."""
    desktop = Desktop(backend="uia")
    # Mencari jendela yang judulnya mengandung 'Microsoft Teams'
    teams_windows = [w for w in desktop.windows() if "Microsoft Teams" in w.window_text()]
    if not teams_windows:
        logger.error("Jendela Microsoft Teams tidak ditemukan.")
        return None
    return teams_windows[0]

def get_control_info(control):
    """Mengekstrak informasi kontrol dengan aman."""
    try:
        info = control.element_info
        return {
            "type": info.control_type,
            "name": info.name or "",
            "automation_id": info.automation_id or "",
        }
    except Exception as e:
        return {"type": "ERROR", "name": str(e), "automation_id": ""}

def print_structure(control, depth=0, max_depth=3):
    """Mencetak struktur kontrol secara rekursif."""
    if depth > max_depth:
        return
    
    info = get_control_info(control)
    indent = "  " * depth
    print(f"{indent}[{info['type']}] ID={info['automation_id']!r}, Name={info['name']!r}")

    try:
        for child in control.children():
            print_structure(child, depth + 1, max_depth)
    except Exception:
        pass

def inspect_teams():
    window = get_teams_window()
    if not window:
        return

    # CariPane yang benar (yang punya nama)
    target_pane = next((c for c in window.children() if c.element_info.name), None)
    
    if target_pane:
        print(f"\n--- Menggunakan target pane: {get_control_info(target_pane)} ---")
        # Cari Document di dalam pane tersebut
        document = target_pane.descendants(control_type="Document")
        if document:
            document = document[0]
            print("Document berhasil ditemukan!")
        else:
            logger.error("Document tidak ditemukan di dalam pane.")
            return
    else:
        logger.error("Target pane tidak ditemukan.")
        return
    
    # Gunakan fungsi filter Python untuk automation_id karena UIA tidak mendukung regex langsung di build_condition
    all_groups = document.descendants(control_type="Group")
    messages = [
        c for c in all_groups 
        if c.element_info.automation_id and "message-body-" in c.element_info.automation_id
    ]
    
    logger.info(f"Ditemukan {len(messages)} pesan.")

    for i, msg in enumerate(messages[:MAX_MESSAGES], 1):
        print(f"\n{'='*20} MESSAGE {i} {'='*20}")
        print_structure(msg)

if __name__ == "__main__":
    inspect_teams()
