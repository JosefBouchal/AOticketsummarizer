### Shrnutí support ticketu

1. **Téma ticketu:**
   - Uživatel hlásil problém s automatickým občerstvením stránky Aliteo, které mu neúmyslně odčítalo rozpracované komentáře.

2. **Spokojenost:**
   - Pravděpodobně spokojený – uživatel potvrdil, že se mu problém již delší dobu neprojevil a souhlasil s uzavřením ticketu.

3. **Klíčové kroky provedené během řešení:**
   - prozkoumání kódu a identifikace různých možných příčin problému.
   - analýza HAR souboru, který poskytl detailní informace o autentizaci a session.
   - konzultace mezi členy týmu ohledně situace a testování různých scénářů v prohlížečích.
   - určení, že problém může souviset s expiračními cookies a zmeškanými HTTP požadavky.
   - návrh na přechod na WebSockety pro stabilnější spojení a eliminaci potřeby obnovování stránky.

4. **Poznámky:**
   - Ticket byl otevřen v dubnu 2023 a uzavřen v srpnu 2024.
   - Celkový čas řešení ticketu trval více než 500 hodin.
   - Komunikace probíhala prostřednictvím 31 příspěvků od různých autorů.
   - Uživatel aktivně testoval možné příčiny problému a poskytoval námětky na zlepšení.

5. **Doporučení pro vývoj/support:**
   - přejít na implementaci WebSocketů pro zajištění stálého připojení.
   - zkontrolovat plnění cookies a možnosti identifikace problému s autentizací.
   - informovat uživatele o možnostech ukládání rozpracovaných komentářů v pravidelných intervalech pro zajištění datové integrity.