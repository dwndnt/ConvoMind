from pywinauto import Desktop
import time

desktop = Desktop(backend="uia")
teams = [w for w in desktop.windows() if "Microsoft Teams" in w.window_text()]
if teams:
    win = teams[0]
    target_pane = next((c for c in win.children() if c.element_info.name), None)
    doc = target_pane.descendants(control_type="Document")[0]
    ml_list = [g for g in doc.descendants(control_type="Group") if g.element_info.name == "Message List"]
    if ml_list:
        ml = ml_list[0]
        print("Testing ml.scroll(direction='up', amount='page')...")
        try:
            ml.scroll(direction="up", amount="page")
            print("ml.scroll succeeded!")
        except Exception as e:
            print("ml.scroll error:", e)

        time.sleep(1)
        groups = [c for c in ml.descendants(control_type="Group") if c.element_info.automation_id and "message-body-" in c.element_info.automation_id]
        print(f"Count after scroll: {len(groups)}")
        if groups:
            print("First ID:", groups[0].element_info.automation_id)
            print("Last ID:", groups[-1].element_info.automation_id)
