# Musiikinjakosovellus
Sovelluksessa näkyy alueita, joista jokaisella on tietyn genren musiikkia. Alueilla on käyttäjien lataamia kappaleita, joissa on myös kommenttiketjut. Erikoisuutena on se, että kappaleista voi ladata useita eri versioita, jotta muut käyttäjät voivat seurata ja kommentoida projektin edistymistä. Jokainen käyttäjä on peruskäyttäjä tai ylläpitäjä.
Sovelluksen ominaisuuksia:
- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
- Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen kappaleiden määrän ja viimeksi ladatun kappaleen ajankohdan. Alueet on jaettu genrejen perusteella.
- Käyttäjä voi ladata sovellukseen kappaleen, jolle hän antaa nimen, genren, kuvauksen ja mahdollisia aihetunnisteita. 
- Käyttäjä voi ladata sovellukseen kappaleista useita versioita, jotka näkyvät eri välilehdillä kappalesivulla. Uuden version kuvaukseen käyttäjä voi merkitä, mitä versiossa on muutettu ja missä kohdassa.
- Käyttäjä voi asettaa kappaleen yksityiseksi ja määrittää, keillä on pääsy siihen.
- Käyttäjä voi kirjoittaa kommentin omaan tai toisen lataamaan kappaleeseen.
- Käyttäjä voi muokata lataamansa kappaleen sekä kirjoittamansa kommentin sisältöä. Käyttäjä voi myös poistaa kappaleen tai kommentin.
- Käyttäjä voi etsiä kappaleita sanojen tai aihetunnisteiden perusteella (esim. genre).
- Ylläpitäjä voi lisätä ja poistaa kappaleita tai kommentteja. Ylläpitäjä näkee kaikki lataukset, myös yksityiseksi asetetut.
- Ylläpitäjä voi asettaa julkiseksi asetettuja kappaleita ”valokeilaan”, joka näkyy sovelluksessa ensimmäisenä.
- Ylläpitäjä voi tehdä kappaleista soittolistoja, jotka näkyvät omalla alueellaan.

## Testausohjeet

Sovellus ei ainakaan tällä hetkellä toimi Fly.iossa, joten testaus on tehtävä lokaalisti. Jos se toimiikin testaushetkellä, osoite on https://musiikinjakosovellus.fly.dev/.

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:

DATABASE_URL=postgresql:///käyttäjänimi
SECRET_KEY=(salainen avain)

Aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla

$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt

Skeeman saa asennettua komennolla psql < schema.sql. 

Lopuksi sovellus käynnistyy komennolla flask run.

## Tämänhetkiset ominaisuudet

- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen, joko ylläpitäjän tai käyttäjän.
- Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen kappaleiden määrän ja viimeksi ladatun kappaleen ajankohdan. Alueet on jaettu genrejen perusteella.
- Käyttäjä voi ladata sovellukseen kappaleen, jolle hän antaa nimen, genren ja kuvauksen.
- Käyttäjä voi asettaa kappaleen yksityiseksi.
- Käyttäjä voi kirjoittaa kommentin omaan tai toisen lataamaan kappaleeseen.
- Käyttäjä voi muokata lataamansa kappaleen sekä kirjoittamansa kommentin sisältöä. Käyttäjä voi myös poistaa kappaleen tai kommentin.
- Käyttäjä voi etsiä kappaleita sanojen perusteella.
- Ylläpitäjä voi lisätä ja poistaa kappaleita tai kommentteja. Ylläpitäjä näkee kaikki lataukset, myös yksityiseksi asetetut.