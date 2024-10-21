import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

class AplikacjaObrazy:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.obrazy = []  # Lista przechowująca oryginalne obrazy
        self.tk_obrazy = []  # Lista przechowująca obrazy do wyświetlenia na zakładkach

        # Tworzenie widgetu Notebook do obsługi zakładek
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Utworzenie paska narzędziowego
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Zakładka File
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Wczytaj obraz", command=self.wczytaj_obraz)
        file_menu.add_command(label="Zapisz obraz", command=self.zapisz_obraz)
        file_menu.add_command(label="Duplikuj obraz", command=self.duplikuj_obraz)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Zakładka Lab 1
        lab_menu = tk.Menu(self.menu_bar, tearoff=0)
        lab_menu.add_command(label="Oblicz histogram", command=self.tworz_histogram)
        lab_menu.add_command(label="Utwórz tablicę LUT", command=self.tworz_LUT)
        self.menu_bar.add_cascade(label="Lab 1", menu=lab_menu)

        # Zakładka Lab 2
        operation_menu = tk.Menu(self.menu_bar, tearoff=0)
        operation_menu.add_command(label="Negacja", command=self.negacja)
        operation_menu.add_command(label="Redukcja poziomów szarości", command=self.redukcja_poziomow_szarości)
        operation_menu.add_command(label="Progowanie binarne", command=self.progowanie_binarne)
        operation_menu.add_command(label="Progowanie z zachowaniem poziomów", command=self.progowanie_z_poziomami)
        self.menu_bar.add_cascade(label="Lab 2", menu=operation_menu)

        # Zakładka View
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Full screen", command=self.pelny_ekran)
        view_menu.add_command(label="Original size", command=self.naturalna_rozdzielczosc)
        view_menu.add_command(label="Dopasuj do okna", command=self.dopasuj_do_okna)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

    def wczytaj_obraz(self):
        """Wczytaj obraz z pliku i dodaj jako nową zakładkę"""
        plik_obraz = filedialog.askopenfilename(
            title="Wybierz obraz",
            filetypes=[("Pliki obrazów", "*.bmp;*.tif;*.png;*.jpg")]
        )
        if plik_obraz:
            obraz = Image.open(plik_obraz)
            self.dodaj_obraz_do_notebooka(obraz, f"Obraz {len(self.obrazy) + 1}")

    def zapisz_obraz(self):
        """Zapisz aktualnie wybrany obraz z zakładki"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        zapisz_plik = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")],
            title="Zapisz obraz"
        )
        if zapisz_plik:
            obraz.save(zapisz_plik)
            messagebox.showinfo("Obraz zapisany", f"Obraz został zapisany jako {zapisz_plik}")

    def duplikuj_obraz(self):
        """Duplikuj aktualny obraz i dodaj jako nową zakładkę"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        oryginalny_obraz = self.obrazy[aktualna_zakladka]
        duplikat = oryginalny_obraz.copy()

        self.dodaj_obraz_do_notebooka(duplikat, f"Obraz {len(self.obrazy) + 1} (Kopia)")

    def dodaj_obraz_do_notebooka(self, obraz, tytul):
        """Dodaj nową zakładkę z obrazem do notebooka"""
        self.obrazy.append(obraz)

        # Utwórz nową zakładkę z ramką
        ramka = tk.Frame(self.notebook)
        ramka.pack(fill=tk.BOTH, expand=True)

        # Dodaj płótno do ramki
        canvas = tk.Canvas(ramka, bg='white')
        canvas.pack(fill=tk.BOTH, expand=True)

        # Zmień rozmiar obrazu do dopasowania do zakładki
        szerokosc = self.notebook.winfo_width() or 800
        wysokosc = self.notebook.winfo_height() or 600
        obraz_dopasowany = obraz.resize((szerokosc, wysokosc), Image.LANCZOS)

        # Wyświetl obraz na płótnie
        tk_obraz = ImageTk.PhotoImage(obraz_dopasowany)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_obraz)

        # Przechowuj referencję do obrazu, aby uniknąć usunięcia z pamięci
        self.tk_obrazy.append((canvas, tk_obraz))

        # Dodaj zakładkę do notebooka
        self.notebook.add(ramka, text=tytul)
        self.notebook.select(ramka)  # Automatyczne przełączenie na nową zakładkę

    def pelny_ekran(self):
        """Wyświetl obraz z aktualnie wybranej zakładki w trybie pełnoekranowym"""
        self.zmien_rozmiar_obrazka("pelny_ekran")

    def naturalna_rozdzielczosc(self):
        """Wyświetlenie obrazu z aktualnie wybranej zakładki w jego naturalnej rozdzielczości"""
        self.zmien_rozmiar_obrazka("naturalna_rozdzielczosc")

    def dopasuj_do_okna(self):
        """Dostosuj obraz do aktualnych wymiarów okienka zakładki"""
        self.zmien_rozmiar_obrazka("dopasuj_do_okna")

    def zmien_rozmiar_obrazka(self, tryb):
        """Zmienia rozmiar obrazka na zakładce"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        if tryb == "pelny_ekran":
            self.root.attributes("-fullscreen", True)
            szerokosc = self.root.winfo_screenwidth()
            wysokosc = self.root.winfo_screenheight()
            obraz_dopasowany = obraz.resize((szerokosc, wysokosc), Image.LANCZOS)
        elif tryb == "naturalna_rozdzielczosc":
            self.root.attributes("-fullscreen", False)  # Wyłącz tryb pełnoekranowy
            szerokosc, wysokosc = obraz.size
            obraz_dopasowany = obraz
        elif tryb == "dopasuj_do_okna":
            szerokosc = self.notebook.winfo_width()
            wysokosc = self.notebook.winfo_height()
            obraz_dopasowany = obraz.resize((szerokosc, wysokosc), Image.LANCZOS)

        # Aktualizuj obraz na bieżącej zakładce
        canvas, _ = self.tk_obrazy[aktualna_zakladka]
        tk_obraz = ImageTk.PhotoImage(obraz_dopasowany)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_obraz)

        # Przechowaj nowy obraz
        self.tk_obrazy[aktualna_zakladka] = (canvas, tk_obraz)

    def tworz_histogram(self):
        """Oblicz histogram obrazu z aktualnie wybranej zakładki"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        # Sprawdzenie trybu obrazu (kolorowy RGB czy skala szarości L)
        if obraz.mode == 'L':  # Tryb skali szarości
            histogram = obraz.histogram()

            # Wyświetlanie histogramu jako diagramu słupkowego
            plt.figure()
            plt.bar(range(256), histogram, color='gray')
            plt.title("Histogram dla obrazu w skali szarości")
            plt.xlabel("Wartość piksela")
            plt.ylabel("Częstotliwość")
            plt.show()
        elif obraz.mode == 'RGB':  # Tryb kolorowy
            # Rozdzielenie obrazu na kanały R, G, B
            r, g, b = obraz.split()

            # Obliczenie histogramów dla każdego z kanałów
            histogram_r = r.histogram()
            histogram_g = g.histogram()
            histogram_b = b.histogram()

            # Funkcja do formatowania osi Y,X na liczby całkowite
            def format_ticks(n, _):
                return f'{int(n)}'

            # Wyświetlanie histogramów jako oddzielne diagramy słupkowe
            fig, axs = plt.subplots(3, 1, figsize=(10, 8))
            fig.suptitle("Histogram RGB")

            # Histogram dla kanału czerwonego (Red)
            axs[0].bar(range(256), histogram_r, color='red')
            axs[0].set_title("Red")
            axs[0].set_xlabel("Wartość piksela")
            axs[0].set_ylabel("Częstotliwość")
            axs[0].yaxis.set_major_formatter(FuncFormatter(format_ticks))
            axs[0].xaxis.set_major_formatter(FuncFormatter(format_ticks))

            # Histogram dla kanału zielonego (Green)
            axs[1].bar(range(256), histogram_g, color='green')
            axs[1].set_title("Green")
            axs[1].set_xlabel("Wartość piksela")
            axs[1].set_ylabel("Częstotliwość")
            axs[1].yaxis.set_major_formatter(FuncFormatter(format_ticks))
            axs[1].xaxis.set_major_formatter(FuncFormatter(format_ticks))

            # Histogram dla kanału niebieskiego (Blue)
            axs[2].bar(range(256), histogram_b, color='blue')
            axs[2].set_title("Blue")
            axs[2].set_xlabel("Wartość piksela")
            axs[2].set_ylabel("Częstotliwość")
            axs[2].yaxis.set_major_formatter(FuncFormatter(format_ticks))
            axs[2].xaxis.set_major_formatter(FuncFormatter(format_ticks))

            # Wyświetlenie wykresów
            plt.tight_layout()
            plt.show()

    def tworz_LUT(self):
        """Tworzenie tablicy LUT, która liczy piksele o danej wartości jasności"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        # Rozdzielenie obrazu na kanały R, G, B
        r, g, b = obraz.split()

        # Tworzenie tablic LUT dla każdego kanału
        LUT_r, _ = np.histogram(np.array(r), bins=256, range=(0, 255))
        LUT_g, _ = np.histogram(np.array(g), bins=256, range=(0, 255))
        LUT_b, _ = np.histogram(np.array(b), bins=256, range=(0, 255))

        # Tworzenie nowego okna do wyświetlania tablic LUT
        nowe_okno = tk.Toplevel(self.root)
        nowe_okno.title("Tablice LUT dla kanałów RGB")

        # Dodanie widżetu Text do wyświetlania tablic LUT
        text_widget = tk.Text(nowe_okno, wrap=tk.NONE, height=30, width=60)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dodanie paska przewijania
        scrollbar = tk.Scrollbar(nowe_okno, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Wypełnienie widżetu Text wartościami LUT w formacie: R | G | B
        text_widget.insert(tk.END, "       R   |   G   |   B  \n")
        text_widget.insert(tk.END, "-" * 26 + "\n")
        for i in range(256):
            text_widget.insert(tk.END, f"[{i:^3}] {LUT_r[i]:4} | {LUT_g[i]:4} | {LUT_b[i]:4}\n")

    def negacja(self):
        """Negacja obrazu w odcieniach szarości"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        piksele = np.array(obraz)
        negatyw = 255 - piksele  # Negacja pikseli
        obraz_negatyw = Image.fromarray(negatyw)

        self.dodaj_obraz_do_notebooka(obraz_negatyw, f"Negacja obrazu {len(self.obrazy)}")

    def redukcja_poziomow_szarości(self):
        """Redukcja poziomów szarości"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        liczba_poziomow = simpledialog.askinteger("Redukcja poziomów szarości", "Podaj liczbę poziomów szarości:",
                                                  minvalue=2, maxvalue=256)

        if liczba_poziomow:
            piksele = np.array(obraz)
            kwantyzacja = np.floor(piksele / (256 / liczba_poziomow)) * (256 / liczba_poziomow)
            obraz_zredukowany = Image.fromarray(kwantyzacja.astype(np.uint8))

            self.dodaj_obraz_do_notebooka(obraz_zredukowany, f"Redukcja szarości {liczba_poziomow} poziomów")

    def progowanie_binarne(self):
        """Progowanie binarne"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        prog = simpledialog.askinteger("Progowanie binarne", "Podaj próg (0-255):", minvalue=0, maxvalue=255)

        if prog is not None:
            piksele = np.array(obraz)
            progowanie = np.where(piksele < prog, 0, 255)  # Binarne progowanie
            obraz_progowanie = Image.fromarray(progowanie.astype(np.uint8))

            self.dodaj_obraz_do_notebooka(obraz_progowanie, f"Progowanie binarne {prog}")

    def progowanie_z_poziomami(self):
        """Progowanie z zachowaniem poziomów szarości"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        prog = simpledialog.askinteger("Progowanie z zachowaniem poziomów", "Podaj próg (0-255):", minvalue=0,
                                       maxvalue=255)

        if prog is not None:
            piksele = np.array(obraz)
            progowanie = np.where(piksele < prog, 0, piksele)  # Progowanie z zachowaniem poziomów
            obraz_progowanie = Image.fromarray(progowanie.astype(np.uint8))

            self.dodaj_obraz_do_notebooka(obraz_progowanie, f"Progowanie z poziomami {prog}")

# Uruchomienie aplikacji
if __name__ == "__main__":
    root = tk.Tk()
    app = AplikacjaObrazy(root)
    root.mainloop()