# Musiikinjakosovellus
Sovelluksessa näkyy alueita, joista jokaisella on tietyn genren musiikkia. Alueilla on käyttäjien lataamia kappaleita, joissa on myös kommenttiketjut. Erikoisuutena on se, että kappaleista voi ladata useita eri versioita, jotta muut käyttäjät voivat seurata ja kommentoida projektin edistymistä. Jokainen käyttäjä on peruskäyttäjä tai ylläpitäjä.
Sovelluksen ominaisuudet:
- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen, joko ylläpitäjän tai käyttäjän.
- Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen kappaleiden määrän ja viimeksi ladatun kappaleen ajankohdan. Alueet on jaettu genrejen perusteella.
- Käyttäjä voi ladata sovellukseen kappaleen, jolle hän antaa nimen, genren, kuvauksen ja mahdollisia aihetunnisteita.
- Käyttäjä voi ladata sovellukseen kappaleista useita versioita, jotka näkyvät eri välilehdillä kappalesivulla. Uuden version kuvaukseen käyttäjä voi merkitä, mitä versiossa on muutettu ja missä kohdassa.
- Käyttäjä voi asettaa kappaleen yksityiseksi ja jakaa sen muille tietyllä jakolinkillä.
- Käyttäjä voi kirjoittaa kommentin omaan tai toisen lataamaan kappaleeseen.
- Käyttäjä voi muokata lataamansa kappaleen sekä kirjoittamansa kommentin sisältöä. Käyttäjä voi myös poistaa kappaleen tai kommentin.
- Käyttäjä voi etsiä kappaleita sanojen ja aihetunnisteiden perusteella.
- Ylläpitäjä voi lisätä ja poistaa kappaleita tai kommentteja. Ylläpitäjä näkee kaikki lataukset, myös yksityiseksi asetetut.
- Ylläpitäjä voi asettaa julkiseksi asetettuja kappaleita ”valokeilaan”, joka näkyy sovelluksessa ensimmäisenä.
- Ylläpitäjä voi tehdä kappaleista soittolistoja, jotka näkyvät omalla alueellaan.

## Testausohjeet

Sovellus on valitettavasti testattavissa vain lokaalisti. Sovelluksen käyttäminen vaatii, että python3 ja postgresql on asennettu. Ohjeet testaamiseen ovat seuraavat:

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon.

`git clone https://www.github.com/kortekoski/Musiikinjakosovellus`

Siirry oikeaan hakemistoon (`cd Musiikinjakosovellus`). Aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet.

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r ./requirements.txt`

Luo projektille tietokanta psql:ssä.

`psql`

`CREATE DATABASE tietokannan_nimi;`

Palaa komentoriville komennolla `\q` ja syötä tietokannan skeema tietokantaan.

`psql tietokannan_nimi < schema.sql`

Luo kansioon .env-tiedosto ja määritä sen sisältö.

`DATABASE_URL=postgres:///tietokannan_nimi`

`SECRET_KEY=(salainen avain)`

Salaisen avaimen voi luoda esimerkiksi Python-tulkilla:

`python3`
`import secrets`
`secrets.token_hex(16)`

Lopuksi sovelluksen pitäisi käynnistyä ajamalla `flask run`. Samalla tulee pitää postgresql-tietokantaa auki toisessa terminaalissa (`start-pg.sh`).

Huom.! Aivan aluksi testaajan on tehtävä admin-käyttäjä (create account -> admin yes) ja lisättävä muutama genre (admin panel -> add genre). Muuten oikein mikään muu ei toimi!