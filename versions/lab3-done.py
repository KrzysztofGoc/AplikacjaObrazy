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

        # Zakładka Lab 3
        lab3_menu = tk.Menu(self.menu_bar, tearoff=0)
        lab3_menu.add_command(label="Rozciąganie histogramu (zakres p1-p2 do q3-q4)",
                              command=self.rozciaganie_histogramu_zadany_zakres)
        lab3_menu.add_command(label="Dodawanie obrazów (z wysyceniem)",
                              command=lambda: self.dodawanie_obrazow_z_wyborem(wysycenie=True))
        lab3_menu.add_command(label="Dodawanie obrazów (bez wysycenia)",
                              command=lambda: self.dodawanie_obrazow_z_wyborem(wysycenie=False))
        lab3_menu.add_command(label="Dodawanie przez liczbę (z wysyceniem)",
                              command=lambda: self.operacja_arytmetyczna_liczba('dodawanie', wysycenie=True))
        lab3_menu.add_command(label="Dodawanie przez liczbę (bez wysycenia)",
                              command=lambda: self.operacja_arytmetyczna_liczba('dodawanie', wysycenie=False))
        lab3_menu.add_command(label="Mnożenie przez liczbę (z wysyceniem)",
                              command=lambda: self.operacja_arytmetyczna_liczba('mnożenie', wysycenie=True))
        lab3_menu.add_command(label="Mnożenie przez liczbę (bez wysycenia)",
                              command=lambda: self.operacja_arytmetyczna_liczba('mnożenie', wysycenie=False))
        lab3_menu.add_command(label="Dzielenie przez liczbę (z wysyceniem)",
                              command=lambda: self.operacja_arytmetyczna_liczba('dzielenie', wysycenie=True))
        lab3_menu.add_command(label="Dzielenie przez liczbę (bez wysycenia)",
                              command=lambda: self.operacja_arytmetyczna_liczba('dzielenie', wysycenie=False))
        lab3_menu.add_command(label="Różnica bezwzględna obrazów", command=self.roznica_bezwzgledna_obrazow_z_wyborem)
        self.menu_bar.add_cascade(label="Lab 3", menu=lab3_menu)

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

    def wybierz_obrazy_do_operacji(self, operacja):
        """Wyświetl dialog do wyboru dwóch obrazów i wykonaj operację (dodawanie, różnica bezwzględna)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Wybierz dwa obrazy")

        # Tworzenie etykiet i pól tekstowych do wprowadzania indeksów
        tk.Label(dialog, text="Indeks 1 obrazu (od 0):").grid(row=0, column=0, padx=10, pady=5)
        indeks1_entry = tk.Entry(dialog)
        indeks1_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Indeks 2 obrazu (od 0):").grid(row=1, column=0, padx=10, pady=5)
        indeks2_entry = tk.Entry(dialog)
        indeks2_entry.grid(row=1, column=1, padx=10, pady=5)

        # Funkcja do zatwierdzania indeksów
        def zatwierdz_indeksy():
            try:
                indeks1 = int(indeks1_entry.get())
                indeks2 = int(indeks2_entry.get())

                # Sprawdzamy, czy indeksy są w zakresie
                if indeks1 >= len(self.obrazy) or indeks2 >= len(self.obrazy) or indeks1 < 0 or indeks2 < 0:
                    messagebox.showwarning("Błąd", "Indeksy muszą być w zakresie istniejących obrazów.")
                    return

                # Zamknięcie okna dialogowego po zatwierdzeniu
                dialog.destroy()

                # Wywołanie odpowiedniej operacji na wybranych obrazach
                operacja(indeks1, indeks2)

            except ValueError:
                messagebox.showwarning("Błąd", "Podaj poprawne wartości indeksów.")

        # Przycisk do zatwierdzania
        tk.Button(dialog, text="Zatwierdź", command=zatwierdz_indeksy).grid(row=2, column=0, columnspan=2, pady=10)

    def roznica_bezwzgledna_obrazow_z_wyborem(self):
        """Różnica bezwzględna obrazów z dialogiem wyboru indeksów, wykorzystując wymiary z aktualnie wyświetlonych obrazów na Canvas"""
        if len(self.tk_obrazy) < 2:
            messagebox.showwarning("Błąd", "Potrzebujesz co najmniej 2 obrazów do wykonania tej operacji.")
            return

        # Funkcja, która będzie wykonywana po zatwierdzeniu indeksów
        def wykonaj_roznice(indeks1, indeks2):
            canvas1, tk_obraz1 = self.tk_obrazy[indeks1]
            canvas2, tk_obraz2 = self.tk_obrazy[indeks2]

            # Sprawdzenie, czy tryby obrazów są zgodne
            obraz1 = self.obrazy[indeks1]
            obraz2 = self.obrazy[indeks2]
            if obraz1.mode != obraz2.mode:
                messagebox.showwarning("Błąd",
                                       f"Obrazy muszą mieć ten sam tryb. Obraz 1: {obraz1.mode}, Obraz 2: {obraz2.mode}.")
                return

            # Pobieranie rzeczywistych wymiarów wyświetlonych obrazów (tk_obraz1 i tk_obraz2)
            szerokosc1, wysokosc1 = tk_obraz1.width(), tk_obraz1.height()
            szerokosc2, wysokosc2 = tk_obraz2.width(), tk_obraz2.height()

            if (szerokosc1, wysokosc1) != (szerokosc2, wysokosc2):
                messagebox.showwarning("Błąd", "Obrazy muszą mieć takie same wymiary na kanwie.")
                return

            # Konwersja obrazów na tablice pikseli z aktualnych rozmiarów na kanwie
            piksele1 = np.array(self.obrazy[indeks1].resize((szerokosc1, wysokosc1)))
            piksele2 = np.array(self.obrazy[indeks2].resize((szerokosc2, wysokosc2)))

            # Obliczanie różnicy bezwzględnej
            roznica = np.abs(piksele1 - piksele2)

            obraz_wynikowy = Image.fromarray(roznica.astype(np.uint8))
            self.dodaj_obraz_do_notebooka(obraz_wynikowy, f"Różnica bezwzględna obrazów (Indeksy {indeks1}, {indeks2})")

        # Wywołanie dialogu do wyboru obrazów i przekazanie funkcji do wykonania operacji
        self.wybierz_obrazy_do_operacji(wykonaj_roznice)

    def operacja_arytmetyczna_liczba(self, operacja, wysycenie=True):
        """Dodawanie, dzielenie, mnożenie obrazów przez liczbę z i bez wysycenia"""
        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        piksele = np.array(obraz)

        # Pytanie o wartość liczby całkowitej
        liczba = simpledialog.askinteger("Operacja z liczbą", "Podaj liczbę całkowitą:", minvalue=1)

        if liczba is None:
            return

        if wysycenie:
            if operacja == 'dodawanie':
                wynik = np.clip(piksele + liczba, 0, 255)
            elif operacja == 'mnożenie':
                wynik = np.clip(piksele * liczba, 0, 255)
            elif operacja == 'dzielenie':
                wynik = np.clip(piksele // liczba, 0, 255)
        else:
            # Operacje bez wysycenia (zakres 1-127)
            piksele = np.clip(piksele, 1, 127)
            if operacja == 'dodawanie':
                wynik = piksele + liczba
            elif operacja == 'mnożenie':
                wynik = piksele * liczba
            elif operacja == 'dzielenie':
                wynik = piksele // liczba

        obraz_wynikowy = Image.fromarray(np.clip(wynik, 0, 255).astype(np.uint8))
        self.dodaj_obraz_do_notebooka(obraz_wynikowy, f"{operacja.capitalize()} przez liczbę")

    def dodawanie_obrazow_z_wyborem(self, wysycenie=True):
        """Dodawanie obrazów z dialogiem wyboru indeksów, wykorzystując wymiary z aktualnie wyświetlonych obrazów na Canvas"""
        if len(self.tk_obrazy) < 2:
            messagebox.showwarning("Błąd", "Potrzebujesz co najmniej 2 obrazów do wykonania tej operacji.")
            return

        # Funkcja, która będzie wykonywana po zatwierdzeniu indeksów
        def wykonaj_dodawanie(indeks1, indeks2):
            canvas1, tk_obraz1 = self.tk_obrazy[indeks1]
            canvas2, tk_obraz2 = self.tk_obrazy[indeks2]

            # Sprawdzenie, czy tryby obrazów są zgodne
            obraz1 = self.obrazy[indeks1]
            obraz2 = self.obrazy[indeks2]
            if obraz1.mode != obraz2.mode:
                messagebox.showwarning("Błąd",
                                       f"Obrazy muszą mieć ten sam tryb. Obraz 1: {obraz1.mode}, Obraz 2: {obraz2.mode}.")
                return

            # Pobieranie rzeczywistych wymiarów wyświetlonych obrazów (tk_obraz1 i tk_obraz2)
            szerokosc1, wysokosc1 = tk_obraz1.width(), tk_obraz1.height()
            szerokosc2, wysokosc2 = tk_obraz2.width(), tk_obraz2.height()

            if (szerokosc1, wysokosc1) != (szerokosc2, wysokosc2):
                messagebox.showwarning("Błąd", "Obrazy muszą mieć takie same wymiary na kanwie.")
                return

            # Konwersja obrazów na tablice pikseli z aktualnych rozmiarów na kanwie
            piksele1 = np.array(self.obrazy[indeks1].resize((szerokosc1, wysokosc1)))
            piksele2 = np.array(self.obrazy[indeks2].resize((szerokosc2, wysokosc2)))

            if wysycenie:
                # Dodawanie z wysyceniem (clamping)
                suma = np.clip(piksele1 + piksele2, 0, 255)
            else:
                # Dodawanie bez wysycenia, ograniczamy poziom do 1-127
                piksele1 = np.clip(piksele1, 1, 127)
                piksele2 = np.clip(piksele2, 1, 127)
                suma = piksele1 + piksele2

            # Tworzenie nowego obrazu z wynikiem operacji
            obraz_wynikowy = Image.fromarray(suma.astype(np.uint8))
            self.dodaj_obraz_do_notebooka(obraz_wynikowy, f"Dodawanie obrazów (Indeksy {indeks1}, {indeks2})")

        # Wywołanie dialogu do wyboru obrazów i przekazanie funkcji do wykonania operacji
        self.wybierz_obrazy_do_operacji(wykonaj_dodawanie)

    def rozciaganie_histogramu_zadany_zakres(self):
        """Rozciąganie histogramu w zadanym zakresie p1-p2 do q3-q4"""
        # Tworzenie nowego okna dialogowego
        dialog = tk.Toplevel(self.root)
        dialog.title("Podaj zakresy p1, p2, q3, q4")

        # Tworzenie etykiet i pól tekstowych do wprowadzania wartości
        tk.Label(dialog, text="Zakres p1 (dolny próg dla obrazu źródłowego):").grid(row=0, column=0, padx=10, pady=5)
        p1_entry = tk.Entry(dialog)
        p1_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Zakres p2 (górny próg dla obrazu źródłowego):").grid(row=1, column=0, padx=10, pady=5)
        p2_entry = tk.Entry(dialog)
        p2_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Zakres q3 (dolny próg dla obrazu wynikowego):").grid(row=2, column=0, padx=10, pady=5)
        q3_entry = tk.Entry(dialog)
        q3_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Zakres q4 (górny próg dla obrazu wynikowego):").grid(row=3, column=0, padx=10, pady=5)
        q4_entry = tk.Entry(dialog)
        q4_entry.grid(row=3, column=1, padx=10, pady=5)

        # Funkcja, która będzie wywołana po zatwierdzeniu
        def zatwierdz_zakresy():
            try:
                p1 = int(p1_entry.get())
                p2 = int(p2_entry.get())
                q3 = int(q3_entry.get())
                q4 = int(q4_entry.get())

                # Sprawdzanie poprawności zakresów
                if p1 >= p2 or q3 >= q4:
                    messagebox.showwarning("Błąd", "Zakresy muszą spełniać warunek: p1 < p2 i q3 < q4.")
                    return

                # Zamknięcie okna dialogowego po zatwierdzeniu
                dialog.destroy()

                # Przetwarzanie obrazu zgodnie z podanymi wartościami
                self.rozciagnij_histogram(p1, p2, q3, q4)

            except ValueError:
                messagebox.showwarning("Błąd", "Wprowadź poprawne wartości liczbowe.")

        # Przycisk do zatwierdzania zakresów
        tk.Button(dialog, text="Zatwierdź", command=zatwierdz_zakresy).grid(row=4, column=0, columnspan=2, pady=10)

    def rozciagnij_histogram(self, p1, p2, q3, q4):
        """Przetwarzanie obrazu po rozciągnięciu histogramu w zadanym zakresie"""
        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka].convert('L')  # Konwersja do skali szarości
        piksele = np.array(obraz)

        # Rozciąganie histogramu w zadanym zakresie
        piksele = np.clip(piksele, p1, p2)  # Ograniczamy wartości do zakresu p1-p2
        rozciagniete = (piksele - p1) * ((q4 - q3) / (p2 - p1)) + q3  # Skalowanie do zakresu q3-q4

        obraz_po_transformacji = Image.fromarray(rozciagniete.astype(np.uint8))
        self.dodaj_obraz_do_notebooka(obraz_po_transformacji, f"Rozciąganie p1={p1}-p2={p2} do q3={q3}-q4={q4}")

    def rozciaganie_histogramu(self):
        """Liniowe rozciąganie histogramu bez przesycenia"""
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
        """Oblicz histogram obrazu z aktualnie wybranej zakładki bez użycia bibliotek do automatycznej generacji, z trzema osobnymi wykresami dla RGB lub jednym dla skali szarości"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        # Tworzenie okna dla histogramu
        histogram_okno = tk.Toplevel(self.root)
        histogram_okno.title("Histogram obrazu")

        # Tworzenie etykiety, która będzie wyświetlała wartości X i Y
        info_label = tk.Label(histogram_okno, text="X: -, Y: -")
        info_label.pack(side=tk.BOTTOM)

        # Obliczenie odpowiedniej szerokości kanwy
        slupki_szerokosc = 3  # Szerokość każdego słupka z odstępem
        canvas_width = 256 * slupki_szerokosc + 100  # 256 słupków + dodatkowa szerokość na marginesy
        canvas_height = 250 + 100  # Dla szarego obrazu jeden histogram zajmie 250 pikseli
        canvas = tk.Canvas(histogram_okno, width=canvas_width, height=canvas_height)
        canvas.pack()

        # Wymiary histogramu
        margin_left = 80  # Większy margines po lewej stronie na oś Y
        margin_bottom = 80  # Większy margines u dołu na oś X
        max_wysokosc = 225  # Dostępna wysokość na jeden histogram (dla każdego z kanałów)

        # Funkcja do dynamicznego ustalania kroku na osi Y
        def dynamiczny_krok_y(max_wartosc):
            """Funkcja wybierająca optymalny krok w zależności od wartości maksymalnej"""
            if max_wartosc <= 100:
                return 10
            elif max_wartosc <= 1000:
                return 100
            elif max_wartosc <= 10000:
                return 1000
            elif max_wartosc <= 50000:
                return 5000
            else:
                return 10000

        # Funkcja do rysowania osi X i Y
        def rysuj_osie(y_offset, max_wartosc, przesuniecie_os_y=0):
            # Oś Y (pionowa)
            canvas.create_line(margin_left + przesuniecie_os_y, canvas_height - margin_bottom - y_offset,
                               margin_left + przesuniecie_os_y, y_offset + 10, width=2)
            # Oś X (pozioma)
            canvas.create_line(margin_left + przesuniecie_os_y, canvas_height - margin_bottom - y_offset,
                               canvas_width - 10, canvas_height - margin_bottom - y_offset, width=2)

            # Dynamiczne znaczniki osi Y
            krok_y = dynamiczny_krok_y(max_wartosc)
            for i in range(0, int(max_wartosc) + krok_y, krok_y):
                y_pos = canvas_height - margin_bottom - int((i / max_wartosc) * max_wysokosc) - y_offset
                canvas.create_text(margin_left - 20 + przesuniecie_os_y, y_pos, text=str(i), anchor=tk.E)

            # Znaczniki na osi X
            for i in range(0, 257, 50):  # Znaczniki co 50 jednostek
                x_pos = margin_left + i * slupki_szerokosc + przesuniecie_os_y
                canvas.create_text(x_pos, canvas_height - margin_bottom + 20 - y_offset, text=str(i), anchor=tk.N)

            # Podpis osi X
            canvas.create_text(canvas_width / 2 + przesuniecie_os_y, canvas_height - 30 - y_offset,
                               text="Wartość piksela",
                               anchor=tk.CENTER)
            # Podpis osi Y
            canvas.create_text(margin_left - 60 + przesuniecie_os_y, (canvas_height - y_offset) - max_wysokosc / 2,
                               text="Częstotliwość", anchor=tk.CENTER, angle=90)

        # Funkcja do rysowania histogramu i podłączania zdarzeń myszki dla słupków
        def rysuj_histogram(histogram, color, y_offset, przesuniecie_os_y=0):
            max_wartosc = max(histogram) + 100
            for i in range(256):
                wysokosc_slupka = int((histogram[i] / max_wartosc) * max_wysokosc) if max_wartosc > 0 else 0
                rect = canvas.create_rectangle(margin_left + i * slupki_szerokosc + przesuniecie_os_y,
                                               canvas_height - margin_bottom - wysokosc_slupka - y_offset,
                                               margin_left + i * slupki_szerokosc + slupki_szerokosc + przesuniecie_os_y,
                                               canvas_height - margin_bottom - y_offset,
                                               fill=color, outline=color)

                # Funkcja obsługująca zdarzenie najechania myszką dla danego prostokąta
                def motion(event, wartosc_x=i, wartosc_y=histogram[i]):
                    info_label.config(text=f"X: {wartosc_x}, Y: {wartosc_y}")

                # Podpinanie zdarzenia do prostokąta
                canvas.tag_bind(rect, "<Enter>", motion)

        if obraz.mode == 'RGB':  # Tryb kolorowy
            r, g, b = obraz.split()
            r_array, g_array, b_array = np.array(r), np.array(g), np.array(b)

            # Zliczanie liczby wystąpień dla każdego kanału (R, G, B)
            histogram_r = [0] * 256
            histogram_g = [0] * 256
            histogram_b = [0] * 256

            for piksel in r_array.flatten():
                histogram_r[piksel] += 1
            for piksel in g_array.flatten():
                histogram_g[piksel] += 1
            for piksel in b_array.flatten():
                histogram_b[piksel] += 1

            # Rysowanie dla każdego kanału osobno
            rysuj_osie(y_offset=520, max_wartosc=max(histogram_r))  # Kanał czerwony (Red)
            rysuj_histogram(histogram_r, 'red', y_offset=520)

            rysuj_osie(y_offset=260, max_wartosc=max(histogram_g))  # Kanał zielony (Green)
            rysuj_histogram(histogram_g, 'green', y_offset=260)

            rysuj_osie(y_offset=0, max_wartosc=max(histogram_b))  # Kanał niebieski (Blue)
            rysuj_histogram(histogram_b, 'blue', y_offset=0)

        elif obraz.mode == 'L':  # Tryb skali szarości
            piksele = np.array(obraz)
            histogram = [0] * 256

            # Zliczanie liczby wystąpień dla wartości w skali szarości
            for piksel in piksele.flatten():
                histogram[piksel] += 1

            # Rysowanie osi dla obrazu w skali szarości
            rysuj_osie(y_offset=0, max_wartosc=max(histogram))

            # Rysowanie histogramu dla obrazu w skali szarości
            rysuj_histogram(histogram, 'gray', y_offset=0)

        else:
            messagebox.showwarning("Nieobsługiwany tryb", "Obsługiwane są tylko tryby L i RGB.")

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
