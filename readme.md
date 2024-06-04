**Polish version below**

# TalentFinder
## Research and Development Project: Analysis of Youth Football Players' Careers

### Introduction

This project aims to conduct a comprehensive analysis of the careers of youth football players. Our main goal is to understand the factors influencing the success of players and to create an artificial intelligence-based model capable of predicting the potential success of a player based on collected data.

### Project Objective

1. **Analysis of Player Careers:** Examining the career trajectories of youth players, including their achievements, number of appearances, and participation in significant football events.

2. **Success Factors:** Identifying key factors influencing player success, such as technical and physical skills.

3. **Success Prediction Model:** Using the collected data to create a machine learning model that can predict the success potential of a young player.

### Project Stages

1. **Data Collection:** Gathering data on the careers of youth players, including match statistics and information about their participation in various tournaments.

2. **Statistical Analysis:** Conducting a detailed statistical analysis to identify significant patterns and correlations between different variables.

3. **Artificial Intelligence Modeling:** Implementing a machine learning model capable of predicting success based on collected data. Using algorithms such as logistic regression and decision trees.

4. **Model Evaluation:** Assessing the effectiveness of the created model based on a test set and adjusting model parameters to achieve optimal results.

5. **Report and Conclusions:** Developing a final report.

### Tools and Technologies

- **Programming Language:** Python
- **ML Libraries:** gym, scikit-learn, stable-baselines3, torch
- **Statistical Analysis:** pandas, numpy, matplotlib
- **Development Environment:** Jupyter Notebook

### Project Organization

- **data/:** Data directory
  - **flags/:** Flags generated based on collected data
  - **players/:** Data about players for both sides with data
  - **sofascore/:** Scraped data from Sofascore
  - **transfermarkt/:** Scraped data from Transfermarkt
- **scrappers/:** Data scraping scripts
  - **sofascore/:** Data scrapers handling Sofascore website
  - **transfermarkt/:** Data scraper handling Transfermarkt website
- **documention/:** Documentation directory
- **editdata/:** Scripts processing data into flags
- **ml/:** Machine learning scripts
  - **clasification/:** Random Forest classification script
  - **random_forest/:** Random Forest regression script
  - **regresion/:** Regression script
- **readme.md:** Project user manual
- **requirements.txt:** Project dependencies file

### System Requirements

- Python 3.7+
- Libraries listed in the `requirements.txt` file

### Installation and Execution Instructions

1. Clone the repository: `git clone https://github.com/klaudiamarciniakk/TalentFinder`
2. Navigate to the project directory: `cd TalentFinder`
3. Install dependencies: `pip install -r requirements.txt`
4. Run scripts according to the instructions in documentation.

### Contact

For questions or feedback, please contact:

- Klaudia Marciniak - klamar7@st.amu.edu.pl - [Klaudia's GitHub](https://github.com/klaudiamarciniakk)
- Wojciech Lidwin - wojlid@st.amu.edu.pl - [Wojciech's GitHub](https://github.com/Halal37)

---

---
# TalentFinder
# Projekt Badawczo-Rozwojowy: Analiza Kariery Młodzieżowców w Zawodzie Piłkarza

## Wprowadzenie

Projekt ten ma na celu przeprowadzenie kompleksowej analizy kariery młodzieżowców w zawodzie piłkarza. Naszym głównym celem jest zrozumienie czynników wpływających na sukces zawodników, a także stworzenie modelu opartego na sztucznej inteligencji, który będzie w stanie przewidzieć potencjał sukcesu danego zawodnika na podstawie zebranych danych.

## Cel Projektu

1. **Analiza Kariery Zawodników:** Badanie trajektorii kariery młodzieżowców, w tym ich osiągnięć, liczby występów, oraz udziału w ważnych wydarzeniach piłkarskich.

2. **Czynniki Sukcesu:** Identyfikacja kluczowych czynników wpływających na sukces zawodników, takich jak umiejętności techniczne i fizyczne.

3. **Model Przewidywania Sukcesu:** Wykorzystanie zgromadzonych danych do stworzenia modelu opartego na sztucznej inteligencji, który będzie w stanie przewidzieć potencjał sukcesu młodego zawodnika.

## Etapy Projektu

1. **Zbieranie Danych:** Gromadzenie danych dotyczących kariery młodzieżowców, takich jak statystyki meczowe, oraz informacje o ich uczestnictwie w różnych turniejach.

2. **Analiza Statystyczna:** Przeprowadzenie szczegółowej analizy statystycznej w celu zidentyfikowania istotnych wzorców i korelacji pomiędzy różnymi zmiennymi.

3. **Modelowanie Sztucznej Inteligencji:** Implementacja modelu uczenia maszynowego, który będzie w stanie przewidzieć potencjał sukcesu na podstawie zebranych danych. Wykorzystanie algorytmów takich jak regresja logistyczna czy drzewa decyzyjne.

4. **Ewaluacja Modelu:** Ocena skuteczności stworzonego modelu na podstawie zestawu testowego, oraz dostosowywanie parametrów modelu w celu uzyskania jak najlepszych wyników.

5. **Raport i Wnioski:** Opracowanie raportu końcowego.

## Narzędzia i Technologie

- **Język Programowania:** Python
- **Biblioteki ML:** gym, scikit-learn, stable-baselines3, torch
- **Analiza Statystyczna:** pandas, numpy, matplotlib
- **Środowisko Programistyczne:** Jupyter Notebook

## Organizacja Projektu

- **data/:** Katalog danych
  - **flags/:** Flagi wygenrowane w oparciu o zebrane dane
  - **players/:** Dane o zawodnikach do obu stron z danymi
  - **sofascore/:** Dane zescrappowane z Sofascore
  - **transfermarkt/:** Dane zescrappowane z Transfermarkt
- **scrappers/:** Skrypty zbierajace dane
  - **sofascore/:** Scrappery danych obsługujący stronę Sofascore
  - **transfermarkt/:** Scrapper danych obsługujący stronę Transfermarkt
- **documentation/:** Katalog z dokumentacją
- **editdata/:** Skrypty przetwarzające dane na flagi
- **ml/:** Skrypty uczenia maszynowego
  - **clasification/:** Skrypt do klasyfikacji Random Forest
  - **random_forest/:** Skrypt do regresji Random Forest
  - **regresion/:** Skrypt do regresji
- **readme.md:** Plik z instrukcją obsługi projektu
- **requirements.txt:** Plik z zależnościami projektu

## Wymagania Systemowe

- Python 3.7+
- Biblioteki wymienione w pliku `requirements.txt`

## Instrukcje Instalacji i Uruchomienia

1. Sklonuj repozytorium: `git clone https://github.com/klaudiamarciniakk/TalentFinder`
2. Przejdź do katalogu projektu: `cd TalentFinder`
3. Zainstaluj zależności: `pip install -r requirements.txt`
4. Uruchom skrypty zgodnie z instrukcjami w dokumentacji.

## Kontakt

W przypadku pytań lub uwag, prosimy o kontakt:

- Klaudia Marciniak - klamar7@st.amu.edu.pl - [Klaudia's GitHub](https://github.com/klaudiamarciniakk)
- Wojciech Lidwin - wojlid@st.amu.edu.pl - [Wojciech's GitHub](https://github.com/Halal37)

---
