from register import RegistrationForm
from tkinter import Tk

def main():
    root = tk.Tk()
    app = RegistrationForm(root)
    root.mainloop()

if __name__ == "__main__":
    main()