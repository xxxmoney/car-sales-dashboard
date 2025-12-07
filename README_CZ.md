# **Dokumentace k projektu: Analytický Dashboard pro Prodej Aut**

 - **Předmět:** Interpretace a prezentace dat (MDIP)
 - **Autor:** Jakub Hána

## **1\. Úvod a Cíle Projektu**
### **1.1 Cíl projektu**
 - Cílem této práce bylo vytvořit interaktivní analytický dashboard pro vizualizaci dat o prodeji ojetých vozů na německém trhu (AutoScout24 dataset) 
 - Aplikace slouží k rychlé orientaci v tržních trendech, analýze cenotvorby a identifikaci klíčových faktorů ovlivňujících cenu vozidel
### **1.2 Cílová skupina**
 - Dashboard je navržen pro **manažery prodeje** a **datové analytiky** v automobilovém průmyslu
   - **Potřeby:** Rychlý přehled o trhu, možnost filtrovat data podle specifických parametrů (značka, palivo) a identifikovat cenové anomálie  
   - **Řešení:** Aplikace nabízí jak globální pohled ("Market Overview"), tak detailní "drill-down" analýzu ("Price & Performance Analysis")
### **1.3 Typ dashboardu**
 - Jedná se o **Analytický dashboard**
   - **Zdůvodnění:** Aplikace klade důraz na interaktivitu (filtry, zoomování v grafech), zkoumání korelací (heatmapa) a distribuci dat (box ploty), což umožňuje uživateli aktivně hledat odpovědi na specifické otázky, spíše než jen pasivně sledovat status

## **2\. Popis Dashboardu a Vizualizace**
 - Dashboard je rozdělen do logických sekcí pomocí karet (tabs), což zajišťuje přehlednost
### **2.1 Klíčové Metriky (KPIs)**
 - V horní části jsou vždy viditelné tři klíčové ukazatele:
   - **Total Vehicles:** Celkový počet vozů odpovídajících filtrům.  
   - **Avg. Price:** Průměrná cena ve výběru.  
   - **Avg. Mileage:** Průměrný nájezd kilometrů.  
   - *Funkce:* Poskytují okamžitý kontext o velikosti a charakteru vybraného vzorku dat.
### **2.2 Smart Insights (Chytrý vhled)**
 - Dynamický textový blok, který automaticky analyzuje vybraná data a generuje slovní popis:
   - Při výběru značky ukazuje **nejčastější model** a porovnává **cenovou hladinu** vůči globálnímu průměru (např. "Premium" vs. "Budget-Friendly")  
   - Při globálním pohledu identifikuje **dominatní značku** a **palivo** na trhu
### **2.3 Grafy a jejich význam**
#### **A. Záložka "Market Overview" (Přehled trhu)**
 - **Sunburst Chart (Market Hierarchy):**  
   - *Typ:* Hierarchický koláčový graf.
   - *Data:* Značka \-\> Model \-\> Palivo
   - *Přínos:* Umožňuje intuitivně chápat strukturu trhu a podíly jednotlivých značek - interaktivně lze "rozkliknout" značku a vidět detail modelů  
   - **Line Chart (Price Evolution):**  
     - *Typ:* Čárový graf 
     - *Data:* Průměrná cena v závislosti na roku výroby
     - *Přínos:* Vizualizuje depreciaci (pokles hodnoty) v čase
   - **Donut Chart (Transmission Share):**  
     - *Typ:* Prstencový graf
     - *Data:* Poměr manuálních a automatických převodovek
     - *Přínos:* Rychlý přehled o technologických preferencích trhu

#### **B. Záložka "Price & Performance Analysis" (Detailní analýza)**
 - **Scatter Plot (Price vs. Mileage):**  
   - *Typ:* Bodový graf.  
   - *Data:* Osa X \= Nájezd, Osa Y \= Cena, Barva \= Palivo.  
   - *Přínos:* Odhaluje vztah mezi opotřebením a cenou - umožňuje identifikovat "výhodné koupě" (nízká cena, nízký nájezd) nebo extrémy - Po kliknutí na bod se otevře detail vozu  
   - **Box Plot (Price by Brand):**  
     - *Typ:* Krabicový graf
     - *Data:* Rozdělení cen pro jednotlivé značky
     - *Přínos:* Ukazuje medián, rozptyl cen a odlehlé hodnoty (outliers) pro každou značku

#### **C. Záložka "Correlations" (Statistika)**
 - **Heatmap (Correlation Matrix):**  
   - *Typ:* Teplotní mapa
   - *Data:* Korelace mezi numerickými proměnnými (Cena, Nájezd, Výkon, Rok)
   - *Přínos:* Statisticky potvrzuje vztahy (např. silná negativní korelace mezi nájezdem a cenou)

## **3\. Technická Dokumentace**
### **3.1 Architektura aplikace**
 - Aplikace je napsána v jazyce **Python** 
   - Správce balíčků **Poetry**
   - Framework **Dash** (nadstavba nad Flask a React.js)
   - Knihovna **Plotly** pro vizualizaci

**Struktura projektu:**
   - main.py: Vstupní bod aplikace.  
   - src/app.py: Definice layoutu, UI komponent a callbacků (interaktivní logika).  
   - src/charts.py: Funkce pro generování jednotlivých grafů (zapouzdření vizuální logiky).  
   - src/data\_loader.py: Třída pro načítání, čištění a přípravu dat (ETL proces).  
   - src/constants.py: Konfigurace barev, cest a stylů.

### **3.2 Popis klíčových funkcí**
#### **Třída DataLoader (src/data\_loader.py)**
 - load\_data(): Načte CSV soubor, odstraní řádky s chybějícími kritickými hodnotami (HP, Gear, Model) a převede datové typy
 - get\_brands(): Vrací seznam unikátních značek pro filtry

#### **Modul charts (src/charts.py)**
 - create\_sunburst\_chart(data): Agreguje data a vytváří hierarchický graf - automaticky seskupuje malé značky do kategorie "Other" pro zachování čitelnosti  
 - \_update\_layout(fig): Privátní pomocná funkce, která aplikuje jednotný grafický styl (fonty, průhledné pozadí) na všechny grafy

#### **Aplikace app (src/app.py)**
 - update\_dashboard(...): Hlavní callback funkce. Přijímá hodnoty z filtrů, filtruje dataset pomocí Pandas a volá funkce pro překreslení všech grafů a výpočet KPI.  
 - update\_model\_options(...): "Chained callback", který dynamicky aktualizuje nabídku modelů podle vybrané značky.

### **3.3 Použité knihovny**
 - **Dash & Dash Bootstrap Components:** Pro tvorbu webového rozhraní a responzivního layoutu.  
 - **Plotly:** Pro interaktivní grafy.  
 - **Pandas:** Pro manipulaci s daty a filtraci.

### **3.4 Instalace a spuštění**
 - **Prerekvizity:**    
   - Python 3.13+
 - **Instalace závislostí:**  
   - Je použit package manager Poetry (https://python-poetry.org)
     - Stačí nainslatovat pomocí `pip install poetry`
   - Vytvoření vyrtuálního prostředí `python3 -m venv .venv`
   - Nainstalování balíčků: `poetry install`
 - **Spuštění:**  
   - `python main.py`

4. Aplikace se spustí na adrese http://127.0.0.1:8050

## **4\. Řešení nenadálých situací**
 - **Chybějící data:** Třída DataLoader automaticky filtruje nekompletní záznamy při startu. Pokud filtr vrátí prázdnou sadu dat, dashboard zobrazí informaci "No data available" a grafy se skryjí, aby aplikace nespadla  
 - **Extrémní hodnoty:** Rozsah sliderů pro cenu a nájezd je dynamicky vypočítán na základě 98\. percentilu, aby extrémní odlehlé hodnoty (outliers) nedeformovaly ovládací prvky