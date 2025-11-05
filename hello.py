from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

API_KEY = "2597522b3emsh0cabcabdff55152p12fa39jsn13dfaadadc0e"
API_HOST = "food-product-api-comprehensive-food-database.p.rapidapi.com"
API_BASE = f"https://{API_HOST}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Food Product</title>
</head>
<body>
<h2>Recherche produit par code-barres</h2>
<form id="searchForm">
    <input type="text" id="query" placeholder="Code-barres" required>
    <button type="submit">Rechercher</button>
</form>
<div id="results"></div>

<script>
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const barcode = document.getElementById('query').value;
    const resDiv = document.getElementById('results');
    resDiv.innerHTML = "<p>Recherche en cours...</p>";

    try {
        const response = await fetch(`/product/${barcode}`);
        const data = await response.json();

        // Vérifier si c'est un produit unique
        const product = data.data;  

        if (!product) {
            resDiv.innerHTML = "<p>Aucun produit trouvé.</p>";
            return;
        }

        // Construire le HTML
        let html = `<h3>${product.identification.name}</h3>
                    <p>Marques: ${product.identification.brands.join(", ")}</p>
                    <p>Quantité: ${product.identification.quantity}</p>
                    <p>Portion: ${product.identification.serving_size}</p>
                    <p>Allergènes: ${product.composition.allergens.join(", ")}</p>
                    <p>Additifs: ${product.composition.additives.join(", ")}</p>
                    <p>Ingrédients: ${product.composition.ingredients_text}</p>
                    ${product.images.front ? `<img src="${product.images.front}" alt="image produit">` : ""}`;

        resDiv.innerHTML = html;

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

@app.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "param q required"}), 400
    url = f"{API_BASE}/products/search"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
    params = {"query": query}
    r = requests.get(url, headers=headers, params=params)
    return (r.text, r.status_code, {"Content-Type": "application/json"})

@app.route("/product/<barcode>")
def get_product(barcode):
    url = f"{API_BASE}/product/{barcode}"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
    r = requests.get(url, headers=headers)
    return (r.text, r.status_code, {"Content-Type": "application/json"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
