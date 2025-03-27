### Shrnutí support ticketu

1. **Téma ticketu:**
   - Uživatel hlásil kritickou chybu v API týkající se pole SupervisorM, které nelze nastavit jako Readonly.

2. **Spokojenost:**
   - Pravděpodobně spokojený – uživatel byl schopen definovat problém a dostal potřebné informace.

3. **Klíčové kroky provedené během řešení:**
   - bylo provedeno upozornění vývojového týmu, aby se na problém podíval
   - byla analyzována chybová logika v kódu související s SupervisorM
   - uživatel byl informován o nutnosti změny hodnoty, aby se Readonly neuplatňovalo
   - došlo k diskusi o úpravách v dokumentaci API a možnostech pro edukaci uživatelů

4. **Poznámky:**
   - celková doba řešení ticketu byla 150 minut
   - bylo zde 10 komentářů, z toho 3 od vlastníka ticketu
   - diskuse probíhala aktivně mezi dvěma hlavními autory
   - probíhala konverzace o nutnosti zlepšení dokumentace v API

5. **Doporučení pro vývoj/support:**
   - upravit API tak, aby hodnotu Readonly pro SupervisorM nebylo možné přiřadit.
   - zlepšit dokumentaci v Swaggeru, aby jasně popisovala pravidla a možnosti pro pole SupervisorM.
   - zavést pravidelné revize a analýzy kódu, aby se předešlo podobným problémům v budoucnu.