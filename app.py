from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# API actuelle
API_KEY = "2597522b3emsh0cabcabdff55152p12fa39jsn13dfaadadc0e"
API_HOST = "food-product-api-comprehensive-food-database.p.rapidapi.com"
API_BASE = f"https://{API_HOST}"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Recherche Produits</title>
<style>
body { font-family: Arial; margin: 20px; }
input[type=text] { width: 300px; padding: 5px; }
button { padding: 5px 10px; }
.result { border: 1px solid #ccc; padding: 10px; margin-top: 10px; }
.result img { max-width: 150px; margin-right: 10px; }
.flex { display: flex; align-items: flex-start; gap: 10px; }
</style>
</head>
<body>
<h2>Recherche produit par mot-clé ou code-barres</h2>
<form id="searchForm">
    <input type="text" id="query" placeholder="Ex: pizza ou 5053990159253" required>
    <button type="submit">Rechercher</button>
</form>
<div id="results"></div>

<script>
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('query').value;
    const resDiv = document.getElementById('results');
    resDiv.innerHTML = "<p>Recherche en cours...</p>";

    try {
        let apiUrl;
        // Si c'est un code-barres
        if (/^\\d{6,}$/.test(query)) {
            apiUrl = `/product/${query}`;
            const response = await fetch(apiUrl);
            const data = await response.json();
            displayProducts([data.data]);
        } else {
            // Mot-clé → recherche OpenFoodFacts
            const res = await fetch(`/search_keyword?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            displayProducts(data);
        }

        function displayProducts(products) {
            if (!products || products.length === 0) {
                resDiv.innerHTML = "<p>Aucun produit trouvé.</p>";
                return;
            }

            let html = "";
            products.forEach(p => {
                const id = p.identification || p;
                const comp = p.composition || {};
                const nutrition = p.nutrition || {};
                const imgs = p.images || {};

                html += `<div class="result">
                            <div class="flex">
                            ${imgs.front ? `<img src="${imgs.front}" alt="image produit">` : ""}
                            <div>
                                <h3>${id.name || "Nom inconnu"}</h3>
                                <p><strong>Marques:</strong> ${id.brands ? id.brands.join(", ") : "Inconnu"}</p>
                                <p><strong>Quantité:</strong> ${id.quantity || "Inconnue"}</p>
                                <p><strong>Portion:</strong> ${id.serving_size || "Inconnue"}</p>
                                <p><strong>Allergènes:</strong> ${comp.allergens ? comp.allergens.join(", ") : "Aucun"}</p>
                                <p><strong>Additifs:</strong> ${comp.additives ? comp.additives.join(", ") : "Aucun"}</p>
                                <p><strong>Ingrédients:</strong> ${comp.ingredients_text || "Non disponible"}</p>
                                ${nutrition.per_100g ? `<p><strong>Énergie (kcal/100g):</strong> ${nutrition.per_100g["energy-kcal_100g"] || "?"}</p>` : ""}
                            </div>
                            </div>
                         </div>`;
            });
            resDiv.innerHTML = html;
        }

    } catch (err) {
        resDiv.innerHTML = "<p>Erreur lors de la requête.</p>";
        console.error(err);
    }
});
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

# Endpoint pour code-barres
@app.route("/product/<barcode>")
def get_product(barcode):
    url = f"{API_BASE}/product/{barcode}"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
    r = requests.get(url, headers=headers)
    return (r.text, r.status_code, {"Content-Type": "application/json"})

# Endpoint pour mot-clé via OpenFoodFacts
@app.route("/search_keyword")
def search_keyword():
    keyword = request.args.get("q")
    if not keyword:
        return jsonify([])

    # 1️⃣ Rechercher sur OpenFoodFacts
    off_res = requests.get(
        "https://world.openfoodfacts.org/cgi/search.pl",
        params={"search_terms": keyword, "search_simple":1, "action":"process", "json":1}
    )
    off_data = off_res.json()
    products = []
    # On prend seulement les 5 premiers produits pour ne pas saturer
    for item in off_data.get("products", [])[:5]:
        barcode = item.get("code")
        if not barcode:
            continue
        # 2️⃣ Appeler l'API actuelle avec le code-barres
        api_res = requests.get(
            f"{API_BASE}/product/{barcode}",
            headers={"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
        )
        if api_res.status_code == 200:
            products.append(api_res.json().get("data"))
    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
