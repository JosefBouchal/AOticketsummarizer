### Shrnutí support ticketu

1. **Téma ticketu:**
   - Uživatel hlásil problém s nezobrazováním komentářů v předchozí záložce úkolu.

2. **Spokojenost:**
   - Nelze odhadnout – chybí hodnocení i zpětná vazba.

3. **Klíčové kroky provedené během řešení:**
   - byl zajištěn přenos ticketu k vývojovému týmu.
   - byl proveden pokus o diagnostiku chyby 414, která byla zmíněna uživatelem.
   - bylo potvrzeno, že změny se přenášejí přes web sockets, což vylučuje chybu 414 jako příčinu.

4. **Poznámky:**
   - Řešení ticketu trvalo 4215 minut.
   - Během vyřešení proběhly dva komentáře, všechny od jiného uživatele než vlastníka.
   - Uživatel se v komentáři zmínil o pokusu zkopírovat text, což mohlo ovlivnit situaci.

5. **Doporučení pro vývoj/support:**
   - prověřit interní logy pro případné další informace týkající se aktualizace komentářů.
   - navrhnout uživatelům obnovení stránky jako standardní postup při podobných problémech.
   - zvážit zlepšení chybového hlášení pro evidenci problémů s requesty.