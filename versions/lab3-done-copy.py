import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import cv2


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

        # Zakładka Operacje logiczne
        logic_menu = tk.Menu(self.menu_bar, tearoff=0)
        logic_menu.add_command(label="NOT", command=self.not_operacja_z_wyborem)
        logic_menu.add_command(label="AND", command=lambda: self.operacja_logiczna_z_wyborem("AND"))
        logic_menu.add_command(label="OR", command=lambda: self.operacja_logiczna_z_wyborem("OR"))
        logic_menu.add_command(label="XOR", command=lambda: self.operacja_logiczna_z_wyborem("XOR"))
        logic_menu.add_command(label="Konwersja binarny ↔ 8-bit", command=self.konwersja_binarny_8bit)
        self.menu_bar.add_cascade(label="Lab 3 - zad 2", menu=logic_menu)

        # Zakładka Lab 4
        lab4_menu = tk.Menu(self.menu_bar, tearoff=0)
        lab4_menu.add_command(label="Wygładzanie liniowe", command=self.wygladzanie_liniowe)
        lab4_menu.add_command(label="Wyostrzanie liniowe", command=self.wyostrzanie_liniowe)
        lab4_menu.add_command(label="Detekcja krawędzi (Sobel)", command=self.detekcja_krawedzi_sobel)
        lab4_menu.add_command(label="Detekcja krawędzi (Prewitt)", command=self.detekcja_krawedzi_prewitt)
        self.menu_bar.add_cascade(label="Lab 4", menu=lab4_menu)

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

    def wybierz_metode_wypelnienia_brzegow(self):
        """Funkcja do wyboru metody uzupełniania brzegów."""
        metoda_wypelnienia = simpledialog.askstring("Metoda uzupełniania brzegów",
                                                    "Wybierz metodę:\n1 - Stała wartość\n2 - Reflect 101\n3 - Reflect")

        if metoda_wypelnienia == '1':
            border_type = cv2.BORDER_CONSTANT
            border_value = simpledialog.askinteger("Wartość stała", "Podaj wartość stałą n:", minvalue=0, maxvalue=255)
            if border_value is None:
                return None, None
            return border_type, border_value
        elif metoda_wypelnienia == '2':
            return cv2.BORDER_REFLECT_101, None
        elif metoda_wypelnienia == '3':
            return cv2.BORDER_REFLECT, None
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy wybór metody uzupełniania brzegów.")
            return None, None

    def obraz_na_cv2(self, indeks):
        """Konwertuje obraz PIL na format zgodny z OpenCV (NumPy array)"""
        obraz = self.obrazy[indeks].convert('RGB')  # Konwersja do RGB, jeśli nie jest
        obraz_cv = np.array(obraz)
        return cv2.cvtColor(obraz_cv, cv2.COLOR_RGB2BGR)

    def wygeneruj_obraz_z_cv2(self, wynik_cv):
        """Konwertuje obraz z formatu OpenCV (NumPy array) na format PIL"""
        wynik_pil = Image.fromarray(cv2.cvtColor(wynik_cv, cv2.COLOR_BGR2RGB))
        return wynik_pil

    def wygladzanie_liniowe(self):
        """Wybór i zastosowanie filtrów wygładzających"""
        aktualna_zakladka = self.notebook.index("current")
        obraz_cv = self.obraz_na_cv2(aktualna_zakladka)

        # Dialog wyboru maski
        maska_wybor = simpledialog.askstring("Maska wygładzania",
                                             "Wybierz maskę:\n1 - Uśredniająca\n2 - Uśrednienie z wagami\n3 - Gaussowska")

        if maska_wybor == '1':  # Uśredniająca
            kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.float32)
            kernel /= kernel.sum()  # Normalizacja

        elif maska_wybor == '2':  # Uśrednienie z wagami
            k = simpledialog.askfloat("Waga środkowego piksela", "Podaj wartość wagi k (liczba dodatnia):", minvalue=0.1)
            if k is None:
                return
            kernel = np.array([[1, 1, 1], [1, k, 1], [1, 1, 1]], dtype=np.float32)
            kernel /= kernel.sum()  # Normalizacja

        elif maska_wybor == '3':  # Gaussowska
            kernel = np.array([[1, 2, 1], [2, 5, 2], [1, 2, 1]], dtype=np.float32)
            kernel /= kernel.sum()  # Normalizacja

        else:
            messagebox.showerror("Błąd", "Nieprawidłowy wybór maski.")
            return

        # Wywołanie funkcji do wyboru metody uzupełniania brzegów
        border_type, border_value = self.wybierz_metode_wypelnienia_brzegow()

        # Zastosowanie filtru wyostrzającego z wybraną maską i metodą uzupełniania brzegów
        if border_type == cv2.BORDER_CONSTANT:
            obraz_cv = cv2.copyMakeBorder(obraz_cv, 1, 1, 1, 1, border_type, value=border_value)
            wynik = cv2.filter2D(obraz_cv, -1, kernel)
        else:
            wynik = cv2.filter2D(obraz_cv, -1, kernel, borderType=border_type)

        wynik_obraz = self.wygeneruj_obraz_z_cv2(wynik)
        self.dodaj_obraz_do_notebooka(wynik_obraz, f"Wyostrzanie: Maska {maska_wybor}")

    def wyostrzanie_liniowe(self):
        """Wybór i zastosowanie filtrów wyostrzających"""
        aktualna_zakladka = self.notebook.index("current")
        obraz_cv = self.obraz_na_cv2(aktualna_zakladka)

        maska_wybor = simpledialog.askstring("Maska wyostrzania",
                                             "Wybierz maskę:\n1 - Laplasjan 1\n2 - Laplasjan 2\n3 - Laplasjan 3")

        if maska_wybor == '1':
            kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
        elif maska_wybor == '2':
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
        elif maska_wybor == '3':
            kernel = np.array([[-1, 2, -1], [2, -4, 2], [-1, 2, -1]], dtype=np.float32)
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy wybór maski.")
            return

        # Wywołanie funkcji do wyboru metody uzupełniania brzegów
        border_type, border_value = self.wybierz_metode_wypelnienia_brzegow()

        # Zastosowanie filtru wyostrzającego z wybraną maską i metodą uzupełniania brzegów
        if border_type == cv2.BORDER_CONSTANT:
            obraz_cv = cv2.copyMakeBorder(obraz_cv, 1, 1, 1, 1, border_type, value=border_value)
            wynik = cv2.filter2D(obraz_cv, -1, kernel)
        else:
            wynik = cv2.filter2D(obraz_cv, -1, kernel, borderType=border_type)

        wynik_obraz = self.wygeneruj_obraz_z_cv2(wynik)
        self.dodaj_obraz_do_notebooka(wynik_obraz, f"Wyostrzanie: Maska {maska_wybor}")

    def detekcja_krawedzi_sobel(self):
        """Wybór i zastosowanie 8-kierunkowych masek Sobela z możliwością wyboru metody uzupełniania brzegów"""
        aktualna_zakladka = self.notebook.index("current")
        obraz_cv = self.obraz_na_cv2(aktualna_zakladka)

        # Zapytaj użytkownika o wybór kierunku
        kierunek = simpledialog.askstring(
            "Kierunek Sobela",
            "Wybierz kierunek (1-8):\n"
            "1 - Poziomy (0°)\n"
            "2 - 45°\n"
            "3 - Pionowy (90°)\n"
            "4 - 135°\n"
            "5 - 180°\n"
            "6 - 225°\n"
            "7 - 270°\n"
            "8 - 315°"
        )

        # Wywołanie funkcji do wyboru metody uzupełniania brzegów
        border_type, border_value = self.wybierz_metode_wypelnienia_brzegow()

        # Wybór kierunku maski Sobela i zastosowanie wybranej metody uzupełniania brzegów
        if kierunek == '1':  # 0° (poziome krawędzie)
            sobel_x = 1
            sobel_y = 0
        elif kierunek == '2':  # 45°
            sobel_x, sobel_y = 1, 1
        elif kierunek == '3':  # 90° (pionowe krawędzie)
            sobel_x, sobel_y = 0, 1
        elif kierunek == '4':  # 135°
            sobel_x, sobel_y = -1, 1
        elif kierunek == '5':  # 180° (odwrócone poziome krawędzie)
            sobel_x, sobel_y = -1, 0
        elif kierunek == '6':  # 225°
            sobel_x, sobel_y = -1, -1
        elif kierunek == '7':  # 270° (odwrócone pionowe krawędzie)
            sobel_x, sobel_y = 0, -1
        elif kierunek == '8':  # 315°
            sobel_x, sobel_y = 1, -1
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy wybór kierunku.")
            return

        # Użycie BORDER_CONSTANT z wartością użytkownika lub wybranej metody
        if border_type == cv2.BORDER_CONSTANT:
            obraz_cv = cv2.copyMakeBorder(obraz_cv, 1, 1, 1, 1, border_type, value=border_value)
            wynik = cv2.Sobel(obraz_cv, cv2.CV_64F, sobel_x, sobel_y, ksize=3)
        else:
            wynik = cv2.Sobel(obraz_cv, cv2.CV_64F, sobel_x, sobel_y, ksize=3, borderType=border_type)

        wynik = cv2.convertScaleAbs(wynik)
        wynik_obraz = self.wygeneruj_obraz_z_cv2(wynik)
        self.dodaj_obraz_do_notebooka(wynik_obraz, f"Detekcja krawędzi Sobel: Kierunek {kierunek}")

    def detekcja_krawedzi_prewitt(self):
        """Detekcja krawędzi operatorami Prewitta z możliwością wyboru metody uzupełniania brzegów"""
        aktualna_zakladka = self.notebook.index("current")
        obraz_cv = self.obraz_na_cv2(aktualna_zakladka)

        # Wywołanie funkcji do wyboru metody uzupełniania brzegów
        border_type, border_value = self.wybierz_metode_wypelnienia_brzegow()

        # Przygotowanie masek Prewitta dla osi X i Y
        kernel_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
        kernel_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)

        # Zastosowanie filtrów Prewitta z wybraną metodą uzupełniania brzegów
        if border_type == cv2.BORDER_CONSTANT:
            obraz_cv = cv2.copyMakeBorder(obraz_cv, 1, 1, 1, 1, border_type, value=border_value)
            prewittx = cv2.filter2D(obraz_cv, -1, kernel_x)
            prewitty = cv2.filter2D(obraz_cv, -1, kernel_y)
        else:
            prewittx = cv2.filter2D(obraz_cv, -1, kernel_x, borderType=border_type)
            prewitty = cv2.filter2D(obraz_cv, -1, kernel_y, borderType=border_type)

        # Sumowanie wyników filtrów Prewitta dla osi X i Y oraz konwersja do wartości bezwzględnych
        wynik = cv2.convertScaleAbs(prewittx + prewitty)
        wynik_obraz = self.wygeneruj_obraz_z_cv2(wynik)
        self.dodaj_obraz_do_notebooka(wynik_obraz, "Detekcja krawędzi Prewitt")

    def dodaj_obraz_do_notebooka(self, obraz, tytul):
        """Dodaj nową zakładkę z obrazem do notebooka"""
        self.obrazy.append(obraz)
        ramka = tk.Frame(self.notebook)
        ramka.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(ramka, bg='white')
        canvas.pack(fill=tk.BOTH, expand=True)

        tk_obraz = ImageTk.PhotoImage(obraz)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_obraz)
        self.tk_obrazy.append((canvas, tk_obraz))
        self.notebook.add(ramka, text=tytul)
        self.notebook.select(ramka)

    def konwersja_binarny_8bit(self):
        """Konwersja obrazu między trybem binarnym (1) a 8-bitowym (L) z użyciem standardowego progu binarności"""
        if not self.obrazy or self.notebook.index("current") == -1:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        aktualna_zakladka = self.notebook.index("current")
        obraz = self.obrazy[aktualna_zakladka]

        if obraz.mode == '1':  # Jeśli obraz jest binarny, konwertuj do 8-bitowego
            konwersja = obraz.convert('L')
            self.dodaj_obraz_do_notebooka(konwersja, "Konwersja na 8-bit")
        elif obraz.mode == 'L':  # Jeśli obraz jest 8-bitowy, konwertuj do binarnego z progiem 128
            konwersja = obraz.point(lambda p: 255 if p >= 128 else 0).convert('1')
            self.dodaj_obraz_do_notebooka(konwersja, "Konwersja na binarny")
        else:
            messagebox.showwarning("Nieobsługiwany tryb", "Obsługiwane są tylko tryby L i 1.")

    def not_operacja_z_wyborem(self):
        """Operacja logiczna NOT na wybranym obrazie"""
        if len(self.tk_obrazy) < 1:
            messagebox.showwarning("Błąd", "Potrzebujesz co najmniej jednego obrazu do wykonania tej operacji.")
            return

        # Wywołanie dialogu do wyboru indeksu obrazu
        indeks = simpledialog.askinteger("Wybór obrazu", "Podaj indeks obrazu:", minvalue=1,
                                         maxvalue=len(self.tk_obrazy))
        if indeks is None:
            return  # Anulowanie operacji, jeśli nie podano indeksu

        indeks -= 1  # Dopasowanie indeksu do listy (indeksacja od 0)

        canvas, tk_obraz = self.tk_obrazy[indeks]

        # Sprawdzenie trybu obrazu
        obraz = self.obrazy[indeks]
        if obraz.mode not in ['1', 'L']:
            messagebox.showwarning("Błąd",
                                   f"Obsługiwane tryby: binarny (1) i skala szarości (L). Obraz ma tryb {obraz.mode}.")
            return

        # Pobieranie rzeczywistych wymiarów wyświetlonego obrazu na płótnie
        szerokosc, wysokosc = tk_obraz.width(), tk_obraz.height()

        # Konwersja obrazu do rozmiaru na płótnie
        obraz_rozmiar = obraz.resize((szerokosc, wysokosc))

        # Przeprowadzenie operacji NOT
        if obraz_rozmiar.mode == '1':  # Binarny
            not_image = ImageOps.invert(obraz_rozmiar.convert('L')).convert('1')
        elif obraz_rozmiar.mode == 'L':  # Skala szarości
            not_image = ImageOps.invert(obraz_rozmiar)

        self.dodaj_obraz_do_notebooka(not_image, f"NOT (Indeks {indeks})")

    def operacja_logiczna_z_wyborem(self, operacja):
        """Wykonanie operacji logicznej AND, OR, XOR między dwoma obrazami"""
        if len(self.tk_obrazy) < 2:
            messagebox.showwarning("Błąd", "Potrzebujesz co najmniej dwóch obrazów do wykonania tej operacji.")
            return

        # Funkcja, która zostanie wywołana po zatwierdzeniu wyboru indeksów
        def wykonaj_operacje(indeks1, indeks2):
            canvas1, tk_obraz1 = self.tk_obrazy[indeks1]
            canvas2, tk_obraz2 = self.tk_obrazy[indeks2]

            # Sprawdzenie zgodności trybów obrazów
            obraz1 = self.obrazy[indeks1]
            obraz2 = self.obrazy[indeks2]
            if obraz1.mode != obraz2.mode:
                messagebox.showwarning("Błąd", "Obrazy muszą mieć ten sam tryb.")
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

            # Przeprowadzenie operacji logicznej na tablicach pikseli
            if operacja == "AND":
                wynik = np.bitwise_and(piksele1, piksele2)
                opis = "AND"
            elif operacja == "OR":
                wynik = np.bitwise_or(piksele1, piksele2)
                opis = "OR"
            elif operacja == "XOR":
                wynik = np.bitwise_xor(piksele1, piksele2)
                opis = "XOR"
            else:
                messagebox.showwarning("Błąd", "Nieznana operacja logiczna.")
                return

            obraz_wynikowy = Image.fromarray(wynik.astype(np.uint8))
            self.dodaj_obraz_do_notebooka(obraz_wynikowy, f"{opis} (Indeksy {indeks1}, {indeks2})")

        # Wywołanie dialogu do wyboru obrazów
        self.wybierz_obrazy_do_operacji_log(wykonaj_operacje)

    def wybierz_obrazy_do_operacji_log(self, operacja):
        """Wyświetl dialog do wyboru dwóch obrazów i wykonaj operację logiczną"""
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

                # Wywołanie operacji na wybranych obrazach
                operacja(indeks1, indeks2)

            except ValueError:
                messagebox.showwarning("Błąd", "Podaj poprawne wartości indeksów.")

        # Przycisk do zatwierdzania
        tk.Button(dialog, text="Zatwierdź", command=zatwierdz_indeksy).grid(row=2, column=0, columnspan=2, pady=10)

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
