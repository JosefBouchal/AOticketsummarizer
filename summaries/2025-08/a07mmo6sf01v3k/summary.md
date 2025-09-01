### Shrnutí support ticketu

1. **Téma ticketu:**
   - Uživatel se pokusil automaticky zakládat externí uživatele prostřednictvím API, ale narazil na chybové hlášení kvůli nesprávným parametrům.

2. **Spokojenost:**
   - Pravděpodobně spokojený – uživatel potvrdil funkčnost na konci konverzace.

3. **Klíčové kroky provedené během řešení:**
   - bylo identifikováno, že parametr usercompany je uveden nesprávně a mělo by se použít ID administrátora.
   - bylo doporučeno vynechat parametr usercompany a používat pouze company a emailtoinvite.
   - uživatel byl instruován, aby neuváděl email, ale pouze emailtoinvite.
   - uživatel potvrdil, že problém vyřešil a uzavřel ticket.

4. **Poznámky:**
   - Řešení trvalo 7 dní od vytvoření do uzavření ticketu.
   - Komunikace probíhala mezi dvěma různými autory.
   - Celkový počet komentářů činil 14, což naznačuje aktivní zapojení účastníků.
   - První odpověď na ticket byla poskytnuta do 46 minut.

5. **Doporučení pro vývoj/support:**
   - Zajistit jasnější dokumentaci k použitým API parametrům.
   - Vytvořit příklady správných API volání pro běžné scénáře.
   - Zvýšit školení supportního týmu o nejčastějších chybách v API.