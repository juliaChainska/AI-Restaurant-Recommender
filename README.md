# 🍽️ Smart Meal Finder AI

Smart Meal Finder AI o aplikacja oparta na sztucznej inteligencji, która pomaga użytkownikom znaleźć dania w pobliżu ich lokalizacji. Umożliwia wyszukiwanie restauracji na podstawie konkretnego posiłku (np. „chicken burger”) oraz analizuje dostępne oferty pod kątem zgodności z zapytaniem, jakości obsługi i zawartości menu.

System oparty jest na wieloagentowej architekturze wykorzystującej LangChain (LLM) i integrację z Google Places API.

---

## Funkcjonalności

- Wyszukiwanie po nazwie dania (np. *chicken burger*)
- Geokodowanie lokalizacji wpisanej jako adres lub ulica
- Dopasowanie dań przez agenta AI (LangChain + ChatGPT)
- Analiza opinii z Google Reviews
- Analiza menu (scraping stron restauracji)
- Propozycje dań i ich wariantów (agent sugerujący)
- Filtrowanie po ocenach i sortowanie wyników
- Wykres rozkładu ocen restauracji


---

## Struktura projektu

<pre lang="markdown"><code>📁 src/ 
├── agents/ # Agenci: dopasowywanie dań, analiza recenzji, sugestie
├── managers/ # Zarządzanie konfiguracją i promptami
├── tools/ # Integracja z Google Places API
├── prompts/ # YAML z promptami do LLM
├── workflow/ # Główna logika aplikacji (multi-agent system)
├── streamlit_app.py # Interfejs użytkownika (web) 
└── app.py # Alternatywny interfejs CLI </code> </pre>

---

## Wymagania

- Python 3.8+
- Klucz OpenAI API
- Klucz Google Maps API (z włączonym Places API) 
- Klucz Langsmith
- Klucz Tavily

---
## Instalacja
### Instalacja paczek
<pre lang="markdown"> <code>
pip install -r requirements.txt
</code> </pre>

### Konfiguracja środowiska
W katalogu src/ utwórz plik .env z następującą zawartością:
<pre lang="markdown"> <code>
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
MODEL=chatGPT_model
TEMPERATURE=model_temeprature
TAVILY_API_KEY=your_tavily_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="your_langsmith_key"
LANGSMITH_PROJECT="pr-nautical-networking-70"

</code></pre>


---

## Uruchomienie aplikacji

Web (Streamlit):
<pre lang="markdown"> <code>
streamlit run streamlit_app.py

</code></pre>

CLI:
<pre lang="markdown"> <code>
python app.py

</code></pre>

---

## Przykładowe działanie

1. Użytkownik wpisuje np. "chicken burger" oraz lokalizację "Warsaw, Poland"

2. System:
   - Pobiera dane z Google Places API
   - Weryfikuje, czy restauracje oferują poszukiwane danie (analiza typu i treści strony)
   - Analizuje recenzje Google
   - Pobiera i przetwarza fragmenty menu z witryn internetowych
3. Wyniki są filtrowane, sortowane i prezentowane użytkownikowi w czytelnej formie

---

## Autorzy

Zofia Zakrzewska, Natalia Janasiewicz, Julia Chaińska, Wojciech Różalski

