from pywinauto import Desktop
import time

def debug_teams_structure():
    desktop = Desktop(backend="uia")
    teams_windows = [w for w in desktop.windows() if "Microsoft Teams" in w.window_text()]
    
    if not teams_windows:
        print("Microsoft Teams tidak ditemukan.")
        return

    window = teams_windows[0]
    print(f"Window Name: {window.window_text()}")
    
    print("\n--- MENCARI SEMUA LISTITEM ---")
    # Teams biasanya menggunakan 'ListItem' untuk daftar chat
    list_items = window.descendants(control_type="ListItem")
    
    for i, item in enumerate(list_items):
        print(f"{i}: Name='{item.element_info.name}'")

    print("\n--- MENCARI SEMUA TREEITEM (Alternatif) ---")
    tree_items = window.descendants(control_type="TreeItem")
    for i, item in enumerate(tree_items):
        print(f"{i}: Name='{item.element_info.name}'")

if __name__ == "__main__":
    debug_teams_structure()