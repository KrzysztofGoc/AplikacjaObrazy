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
        self.root.title("Przetwarzanie Obrazów")
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
        lab1_menu = tk.Menu(self.menu_bar, tearoff=0)
        lab1_menu.add_command(label="Oblicz histogram", command=self.tworz_histogram)
        lab1_menu.add_command(label="Utwórz tablicę LUT", command=self.tworz_LUT)
        self.menu_bar.add_cascade(label="Lab 1", menu=lab1_menu)

        # Zakładka Lab 2
        lab2_menu = tk.Menu(self.menu_bar, tearoff=0)
        lab2_menu.add_command(label="Negacja", command=self.negacja)
        lab2_menu.add_command(label="Redukcja poziomów szarości", command=self.redukcja_poziomow_szarości)
        lab2_menu.add_command(label="Progowanie binarne", command=self.progowanie_binarne)
        lab2_menu.add_command(label="Progowanie z zachowaniem poziomów", command=self.progowanie_z_poziomami)
        lab2_menu.add_command(label="Rozciąganie liniowe (bez przesycenia)", command=self.rozciaganie_histogramu)
        lab2_menu.add_command(label="Rozciąganie liniowe (z przesyceniem)",
                              command=self.rozciaganie_histogramu_z_przesyceniem)
        lab2_menu.add_command(label="Equalizacja histogramu", command=self.equalizacja_histogramu)
        self.menu_bar.add_cascade(label="Lab 2", menu=lab2_menu)

        # Zakładka View
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Full screen", command=self.pelny_ekran)
        view_menu.add_command(label="Original size", command=self.naturalna_rozdzielczosc)
        view_menu.add_command(label="Dopasuj do okna", command=self.dopasuj_do_okna)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Zakładka Help
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.pokaz_informacje)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def rozciaganie_histogramu(self):
        """Liniowe rozciąganie histogramu bez przesycenia"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        piksele = np.array(obraz)

        # Liniowe rozciąganie histogramu
        min_val = np.min(piksele)
        max_val = np.max(piksele)
        rozciagniete = (piksele - min_val) * (255 / (max_val - min_val))

        obraz_po_transformacji = Image.fromarray(rozciagniete.astype(np.uint8))
        self.dodaj_obraz_do_notebooka(obraz_po_transformacji, f"Rozciąganie histogramu")

    def rozciaganie_histogramu_z_przesyceniem(self):
        """Liniowe rozciąganie histogramu z przesyceniem (5% pikseli)"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')
        piksele = np.array(obraz)

        # Sortowanie pikseli i ustalenie progów dla 5% przesycenia
        piksele_flat = piksele.flatten()
        piksele_flat.sort()
        n = len(piksele_flat)
        low_cutoff = piksele_flat[int(n * 0.05)]
        high_cutoff = piksele_flat[int(n * 0.95)]

        # Liniowe rozciąganie histogramu z przesyceniem
        rozciagniete = np.clip(piksele, low_cutoff, high_cutoff)
        rozciagniete = (rozciagniete - low_cutoff) * (255 / (high_cutoff - low_cutoff))

        obraz_po_transformacji = Image.fromarray(rozciagniete.astype(np.uint8))
        self.dodaj_obraz_do_notebooka(obraz_po_transformacji, f"Rozciąganie z przesyceniem")

    def equalizacja_histogramu(self):
        """Equalizacja histogramu"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')
        piksele = np.array(obraz)

        # Equalizacja histogramu
        histogram, _ = np.histogram(piksele.flatten(), bins=256, range=(0, 255))
        cdf = histogram.cumsum()  # Obliczanie skumulowanej funkcji rozkładu (CDF)
        cdf_normalized = 255 * cdf / cdf[-1]  # Normalizacja CDF

        # Przekształcanie wartości pikseli przy użyciu znormalizowanej CDF
        equalized = np.interp(piksele.flatten(), range(256), cdf_normalized).reshape(piksele.shape)

        obraz_po_equalizacji = Image.fromarray(equalized.astype(np.uint8))
        self.dodaj_obraz_do_notebooka(obraz_po_equalizacji, f"Equalizacja histogramu")

    def pokaz_informacje(self):
        """Wyświetl okienko z informacjami o autorze i grupie"""
        messagebox.showinfo("Informacje o autorze",
                            "Autor: Krzysztof Goc\n"
                            "Nr indeksu: 20452\n"
                            "Grupa: IZ07IO2\n"
                            "Rok 2024/2025\n"
                            "Język: Python\n"
                            "Biblioteki: Tkinter (GUI), Pillow/Numpy (Operacje na obrazach), matplotlib (Wykresy)"
                            )

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

        def format_ticks(n, _):
            return f'{int(n)}'

        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        # Tworzenie nowego okna dla statystyk
        statystyki_okno = tk.Toplevel(self.root)
        statystyki_okno.title("Statystyki obrazu")
        statystyki_okno.geometry("400x400")

        # Tworzenie obszaru tekstowego do wyświetlania statystyk
        text_widget = tk.Text(statystyki_okno, wrap=tk.WORD, height=10, width=40)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dodanie paska przewijania do obszaru tekstowego
        scrollbar = tk.Scrollbar(statystyki_okno, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Sprawdzenie trybu obrazu (kolorowy RGB czy skala szarości L)
        if obraz.mode == 'L':  # Tryb skali szarości
            piksele = np.array(obraz)

            # Obliczanie statystyk
            liczba_pikseli = piksele.size
            mediana = np.median(piksele)
            srednia = np.mean(piksele)
            odchylenie_standardowe = np.std(piksele)

            # Wyświetlanie statystyk w nowym oknie
            statystyki = f"Liczba pikseli: {liczba_pikseli}\n" \
                         f"Mediana: {mediana}\n" \
                         f"Średnia: {srednia:.2f}\n" \
                         f"Odchylenie standardowe: {odchylenie_standardowe:.2f}\n"
            text_widget.insert(tk.END, statystyki)
            text_widget.config(state=tk.DISABLED)

            # Tworzenie wykresu histogramu z odpowiednim formatowaniem osi
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            ax.bar(range(256), obraz.histogram(), color='gray')
            ax.set_title("Histogram dla obrazu w skali szarości")
            ax.set_xlabel("Wartość piksela")
            ax.set_ylabel("Częstotliwość")
            ax.yaxis.set_major_formatter(FuncFormatter(format_ticks))
            ax.xaxis.set_major_formatter(FuncFormatter(format_ticks))

            # Wyświetlenie histogramu
            plt.tight_layout()
            plt.show()

        elif obraz.mode == 'RGB':  # Tryb kolorowy
            r, g, b = obraz.split()
            r_array, g_array, b_array = np.array(r), np.array(g), np.array(b)

            # Obliczanie statystyk dla każdego kanału
            statystyki_r = {
                'Liczba pikseli': r_array.size,
                'Mediana': np.median(r_array),
                'Średnia': np.mean(r_array),
                'Odchylenie standardowe': np.std(r_array)
            }

            statystyki_g = {
                'Liczba pikseli': g_array.size,
                'Mediana': np.median(g_array),
                'Średnia': np.mean(g_array),
                'Odchylenie standardowe': np.std(g_array)
            }

            statystyki_b = {
                'Liczba pikseli': b_array.size,
                'Mediana': np.median(b_array),
                'Średnia': np.mean(b_array),
                'Odchylenie standardowe': np.std(b_array)
            }

            # Wyświetlanie statystyk dla każdego kanału w nowym oknie
            statystyki = f"Statystyki dla kanału R:\n" \
                         f"Liczba pikseli: {statystyki_r['Liczba pikseli']}\n" \
                         f"Mediana: {statystyki_r['Mediana']}\n" \
                         f"Średnia: {statystyki_r['Średnia']:.2f}\n" \
                         f"Odchylenie standardowe: {statystyki_r['Odchylenie standardowe']:.2f}\n\n" \
                         f"Statystyki dla kanału G:\n" \
                         f"Liczba pikseli: {statystyki_g['Liczba pikseli']}\n" \
                         f"Mediana: {statystyki_g['Mediana']}\n" \
                         f"Średnia: {statystyki_g['Średnia']:.2f}\n" \
                         f"Odchylenie standardowe: {statystyki_g['Odchylenie standardowe']:.2f}\n\n" \
                         f"Statystyki dla kanału B:\n" \
                         f"Liczba pikseli: {statystyki_b['Liczba pikseli']}\n" \
                         f"Mediana: {statystyki_b['Mediana']}\n" \
                         f"Średnia: {statystyki_b['Średnia']:.2f}\n" \
                         f"Odchylenie standardowe: {statystyki_b['Odchylenie standardowe']:.2f}"
            text_widget.insert(tk.END, statystyki)
            text_widget.config(state=tk.DISABLED)

            # Obliczanie histogramów
            histogram_r, histogram_g, histogram_b = r.histogram(), g.histogram(), b.histogram()

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

        # Tworzenie nowego okna do wyświetlania tablic LUT
        nowe_okno = tk.Toplevel(self.root)
        nowe_okno.title("Tablica LUT")

        # Dodanie widżetu Text do wyświetlania tablic LUT
        text_widget = tk.Text(nowe_okno, wrap=tk.NONE, height=30, width=60)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dodanie paska przewijania
        scrollbar = tk.Scrollbar(nowe_okno, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Sprawdzenie trybu obrazu (kolorowy RGB czy skala szarości L)
        if obraz.mode == 'L':  # Tryb skali szarości
            piksele = np.array(obraz)

            # Tworzenie tablicy LUT (histogramu) - zliczanie liczby pikseli dla każdej wartości od 0 do 255
            LUT, _ = np.histogram(piksele, bins=256, range=(0, 255))

            # Wypełnienie widżetu Text wartościami LUT
            text_widget.insert(tk.END, "Wartość pikseli | Częstotliwość\n")
            text_widget.insert(tk.END, "-" * 26 + "\n")
            for i in range(256):
                text_widget.insert(tk.END, f"{i:^15} | {LUT[i]:^12}\n")

        elif obraz.mode == 'RGB':  # Tryb kolorowy
            r, g, b = obraz.split()

            # Tworzenie tablic LUT dla każdego kanału
            LUT_r, _ = np.histogram(np.array(r), bins=256, range=(0, 255))
            LUT_g, _ = np.histogram(np.array(g), bins=256, range=(0, 255))
            LUT_b, _ = np.histogram(np.array(b), bins=256, range=(0, 255))

            # Wypełnienie widżetu Text wartościami LUT w formacie: R | G | B
            text_widget.insert(tk.END, "       R   |   G   |   B  \n")
            text_widget.insert(tk.END, "-" * 26 + "\n")
            for i in range(256):
                text_widget.insert(tk.END, f"[{i:^3}] {LUT_r[i]:4} | {LUT_g[i]:4} | {LUT_b[i]:4}\n")

        # Ustawienie widgetu jako niemodyfikowalnego
        text_widget.config(state=tk.DISABLED)

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
    root.geometry("800x600")
    app = AplikacjaObrazy(root)
    root.mainloop()
