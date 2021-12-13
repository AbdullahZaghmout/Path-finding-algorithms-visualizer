1.Många klasser används

2.koden är strukterad, inga globala variabler. Dock är vissa klasser som "Graphics" och "Simulate" alldeles för långa. däremot är de flesta funktionerna 

3.lagom stora och även de som är som är one-liners gör programmet mer läsbart. Några one-liners som är onödiga dock. Funktionerna parseInputs och initUI är lite för stora men fortfarande lagom stora 

4.Alla klasser och metoder är dokumneterade

5.Ingenting ligger globalt, allting ligger i funktioner och klasser

6.compakt kod inga upprepningar. gillar exmepelvis def getTime(self):
		minStr = str(self.getMinute())
		if len(minStr) < 2:
			minStr = "0" + minStr
		return str(self.getHour()) + "." + minStr)
men jag tror att vissa funcktioner är typ onödiga som
 def getAbsolute(self):
		return self._absoluteTime
7.Ingen hårdkodning. om ett visst värde eller en viss sträng används direkt utan att ha en variabel som pekar på den så avnänds den en gång

8. All användning sker via GUI:t som är intuitiv och lätt att förstå
9.bra variabel namn och namn på funktioner som robberProb setEndService currentTime iterate osv.
