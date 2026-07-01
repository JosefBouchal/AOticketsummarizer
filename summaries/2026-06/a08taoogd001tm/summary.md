### Shrnutí support ticketu

1. **Téma ticketu:**
   - Problém s API voláním /SyncGetSimpleComponents, které vrací typ Create i když je ID již vyplněno.

2. **Spokojenost:**
   - Pravděpodobně spokojený – uživatel potvrdil funkčnost po opravě.

3. **Klíčové kroky provedené během řešení:**
   - vyvstala otázka ohledně vraceného typu API.
   - byl zahájen interní proces pro vyřešení problému.
   - vývojář potvrdil, že je chybné chování API design.
   - bylo dohodnuto, že typ vracený API bude změněn na Modify, pokud je ExternalId naplněno.
   - oprava byla implementována a otestována uživatelem.

4. **Poznámky:**
   - celková doba řešení ticketu byla přibližně 8 dnů.
   - proběhlo 14 komentářů od dvou unikátních autorů.
   - komunikace probíhala prostřednictvím poznámek mezi vývojáři a uživateli.
   - uživatel nenutil rychlé řešení, což naznačuje dobré vztahy.

5. **Doporučení pro vývoj/support:**
   - zvážit revizi designu API pro lepší intuitivnost.
   - vést uživatele k rychlé zpětné vazbě po opravách.
   - systematicky kontrolovat podobné případy v API pro jejich konzistenci.