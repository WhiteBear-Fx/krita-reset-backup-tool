from tkinter import messagebox
from json_manage import language_manager


def run():

    try:
        import main_ui
        main_ui.developer = '白熊Fx'
        main_ui.version = '0.0.1'
        main_ui.RootWindow()
    except Exception as e:
        messagebox.showerror(title=language_manager.get_static().get('error'), message=str(e))

if __name__ == '__main__':
    run()