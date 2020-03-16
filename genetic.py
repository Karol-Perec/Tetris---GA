# Karol Perec
# czesc z funkcjami i mechnimami algorytmu genetycznego


from tetris import *
from itertools import combinations


def funkcja_decyzyjna(plansza, ilosc_usunietych_lini, chromosom):
    # funkcja obliczajaca wartosc danego ruchu na planszy (plansza)
    # wzgledem aktualnej strategii decyzyjnej (chromosom)

    suma_wysokosci, gladkosc, dziury = parametry_planszy(plansza)
    wartosc_funkcji_decyzyjnej = chromosom[0]*ilosc_usunietych_lini + \
                                 chromosom[1]*suma_wysokosci + \
                                 chromosom[2]*gladkosc + \
                                 chromosom[3]*dziury
    return wartosc_funkcji_decyzyjnej


def parametry_planszy(plansza):
    # funkcja oblicza parametry planszy (plansza) w danym momencie
    # parametry to
    # wysokosci - suma wysokosci kolumn na planszy
    # gladkosc - suma roznic pomiedzy sasiedznimi kolumnami
    # dziury - suma pustych pol ponizej najwyzszego zjetego pola w kazdej kolumnie

    wysokosci = [0]*BOARDWIDTH
    gladkosc = 0
    dziury = 0

    for i in range(0, BOARDWIDTH):
        for j in range(0, BOARDHEIGHT):
            if plansza[i][j] != '0':
                wysokosci[i] += (BOARDHEIGHT - j)
                break

    suma_wysokosci = sum(wysokosci)

    for i in range(1, BOARDWIDTH):
        gladkosc += abs(wysokosci[i] - wysokosci[i-1])

    for i in range(0, BOARDWIDTH):
        flaga = 0
        for j in range(0, BOARDHEIGHT):
            if plansza[i][j] != '0':
                flaga = 1
            if plansza[i][j] == '0' and flaga == 1:
                dziury += 1

    return suma_wysokosci, gladkosc, dziury


def inicjalizacja(rozmiar_populacji, rozmiar_chromosomu):
    # tworzy populacje poczatkowa o rozmiarze rozmiar_populacji
    # osobnikow - chromosomy o wielkosci rozmiar_chromosomu
    # kodujacych liczby calkowite z zakresu (-1,1)
    # zawezenio zakres losowania dla poszczegolnego genu

    populacja = [0]*rozmiar_populacji
    chromosom = [0]*rozmiar_chromosomu
    for i in range(0, rozmiar_populacji):
        for j in range (0, rozmiar_chromosomu):
            if j==0:
                chromosom[j] = random.uniform(0,1)
            else:
                chromosom[j] = random.uniform(-1,0)

        populacja[i] = copy.deepcopy(chromosom)
    return populacja


def selekcja(populacja, rozmiar_populacji):
    # selekecja rankingowa osobnikow z populacji (populacja)
    # o wielkosci rozmiar_populacji
    # z iloscia rodzicow rowna 0.4*rozmiar_populacji

    populacja.sort(reverse=True)
    wyselekcjonowane = [0] * int(rozmiar_populacji * 0.4)
    odrzucone = [0] * int(rozmiar_populacji * 0.6)

    for i in range(0, int(rozmiar_populacji * 0.4)):
        wyselekcjonowane[i] = populacja[i]
    for i in range(0, int(rozmiar_populacji * 0.6)):
        odrzucone[i] = populacja[rozmiar_populacji - i - 1]

    return wyselekcjonowane, odrzucone


def krzyzowanie(rodzice):
    # krzyzowanie kazdy z kazdym dla 4 rodzicow
    # krzyzowanie funkcja wazona po funkcji przystosowania
    # otrzymujemy 6 potomkow
    dzieci=[]
    for i in combinations(numpy.arange(len(rodzice)), 2):
        dziecko = []
        for j in range(0, int(len(rodzice[0][1]))):
            if (rodzice[i[0]][0]+rodzice[i[1]][0]) != 0:
                dziecko.append((rodzice[i[0]][1][j]*rodzice[i[0]][0] +
                               rodzice[i[1]][1][j]*rodzice[i[1]][0]) /
                               (rodzice[i[0]][0]+rodzice[i[1]][0]))      # krzyżowanie ważone po funkcji przystosowania
            else:
                dziecko.append((rodzice[i[0]][1][j]+rodzice[i[1]][1][j])/2)

        dzieci.append(dziecko)

    return rodzice, dzieci


def mutacja(populacja, prawdopodobienstwo_mutacji):
    # funkcja mutacji z zadanym prawdopodobienstwem
    # mutuje jeden z parametrow o wartosc z rozkladu normalnego
    # jesli zmutowana wartosc przekroczy zadane zakresy, losowana jest nowa wartosc, az do skutku

    for chromosom in populacja:
        if random.uniform(0, 1) < prawdopodobienstwo_mutacji:
            indeks_parametru = random.randint(0, 4)

            if indeks_parametru == 0:
                while True:
                    mutacja = chromosom[indeks_parametru] + numpy.random.normal(loc=0, scale=0.2)
                    if (mutacja > 0 and mutacja < 1):
                        chromosom[indeks_parametru] = mutacja
                        break

            if indeks_parametru == 1:
                while True:
                    mutacja = chromosom[indeks_parametru] + numpy.random.normal(loc=0, scale=0.2)
                    if (mutacja > -1 and mutacja < 0):
                        chromosom[indeks_parametru] = mutacja
                        break

            if indeks_parametru == 2:
                while True:
                    mutacja = chromosom[indeks_parametru] + numpy.random.normal(loc=0, scale=0.2)
                    if (mutacja > -1 and mutacja < 0):
                        chromosom[indeks_parametru] = mutacja
                        break

            if indeks_parametru == 3:
                while True:
                    mutacja = chromosom[indeks_parametru] + numpy.random.normal(loc=0, scale=0.2)
                    if (mutacja > -1 and mutacja < 0):
                        chromosom[indeks_parametru] = mutacja
                        break
    return populacja


def sukcesja(populacja, rozmiar_chromosomu):
    # funkcja sukcesji
    # do 6 potomkow i 2 najlepszych rodzicow dolaczane sa 2 nowo wygenerowane osobniki

    nowe_losowe = inicjalizacja(2, rozmiar_chromosomu)
    return populacja + nowe_losowe


# def genetic(rozmiar_populacji,rozmiar_chromosomu,liczba_pokolen,prawdopodobienstwo_mutacji,ilosc_prob_fp,czas_stop):
#     # funkcja dostepna w pliku tetris.py
#     # funkcja algorytmu genetycznego z zadanym rozmiarem populacji, rozmiarem chromosomu=4, liczba pokolen
#     # prawdopodobienstwem mutacji, iloscia prob przy obliczaniu funkcji decyzyjnej oraz gornym progiem
#     # czasu dzialania algorytmu
#     # komunikaty w konsoli systemowej, przebieg algorytmu zapisywany do pliku *.txt
#     # wyrysowany wykres krzywej uczacej
#
#     t = time.time()
#     plik_baza_danych = open("baza_danych.txt", "w")
#
#     populacja = inicjalizacja(rozmiar_populacji, rozmiar_chromosomu)
#     baza_danych = [[0] * rozmiar_populacji for i in range(liczba_pokolen)]
#
#     for i in range(0, liczba_pokolen):
#         for j in range(0, rozmiar_populacji):
#             wartosc_funkcji_przystosowania=0
#             for ilosc_prob in range(ilosc_prob_fp):
#                 wartosc_fp, chromosom = run_game(populacja[j], i+1, j+1, ilosc_prob+1)
#                 print("proba nr", ilosc_prob + 1, "lini", wartosc_fp)
#                 wartosc_funkcji_przystosowania += wartosc_fp
#             wartosc_funkcji_przystosowania=wartosc_funkcji_przystosowania/ilosc_prob_fp
#
#             baza_danych[i][j] = [wartosc_funkcji_przystosowania, chromosom]
#             plik_baza_danych.write("Pokolenie " + repr(i + 1) + " osobnik " +
#                                    repr(j + 1) + " chromosom " + repr(chromosom) +
#                                     " lini " + repr(wartosc_funkcji_przystosowania) + "\n")
#             print("Pokolenie ",i+1, "osobnik", j+1, "chromosom ", chromosom, " lini ", wartosc_funkcji_przystosowania)
#         wyselekcjonowane, odrzucone = selekcja(baza_danych[i], rozmiar_populacji)
#         rodzice, dzieci = krzyzowanie(wyselekcjonowane)
#         populacja = [rodzice[0][1]] + [rodzice[1][1]] + dzieci
#         populacja = mutacja(populacja, prawdopodobienstwo_mutacji)
#         populacja = sukcesja(populacja, rozmiar_chromosomu)
#
#         if (time.time() - t) > czas_stop:
#             print("CZAS UPLYNAL")
#             break
#
#     plik_baza_danych.close()
#
#     maxx = [0] * (i + 1)
#     for k in range(0, i + 1):
#         maxx[k] = max([col[0] for col in baza_danych[k]])
#     plt.figure(1)
#     plt.plot(numpy.arange(1, k + 2), maxx, 'k-')
#     plt.xlabel('Pokolenie')
#     plt.ylabel('Przystosowanie najlepszego chromosomu')
#     plt.xlim(1, k + 1)
#     plt.ylim(0, max(maxx) * 1.1)
#     plt.show()
