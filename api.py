"""API REST para predecir las probabilidades de género de una película a partir
de su plot (sinopsis). Compatible con AWS Elastic Beanstalk: la variable WSGI
se llama `application`.
"""
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

from movie_genre_model import predict_genres

app = Flask(__name__)

# --- Interfaz visual en la ruta raíz ---
HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clasificador de Géneros de Películas</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #F7F4EE;
    --surface: #FFFFFF;
    --ink: #1A1814;
    --ink-secondary: #6B6760;
    --accent: #C94B1A;
    --accent-soft: #FAF0EB;
    --border: #E0DBD3;
    --bar-1: #C94B1A;
    --bar-2: #D9743F;
    --bar-3: #E89A65;
    --bar-4: #F2B88C;
    --bar-5: #F8D4B8;
    --radius: 12px;
    --shadow: 0 2px 16px rgba(0,0,0,0.07);
  }

  body {
    background: var(--bg);
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
    min-height: 100vh;
    padding: 0;
  }

  .header {
    background: var(--ink);
    padding: 3rem 2rem 2.5rem;
    text-align: center;
  }

  .header-eyebrow {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.75rem;
  }

  .header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 400;
    color: #FAF8F5;
    line-height: 1.15;
    max-width: 600px;
    margin: 0 auto 1rem;
  }

  .header p {
    color: #A09B94;
    font-size: 1rem;
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
  }

  .main {
    max-width: 700px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
  }

  .card {
    background: var(--surface);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    padding: 2rem;
    margin-bottom: 1.5rem;
  }

  .instructions {
    margin-bottom: 2rem;
  }

  .instructions-title {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-secondary);
    margin-bottom: 1rem;
  }

  .steps {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .step {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .step-num {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .step-text {
    font-size: 0.9rem;
    color: var(--ink-secondary);
    line-height: 1.55;
  }

  .step-text strong { color: var(--ink); font-weight: 500; }

  label {
    display: block;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-secondary);
    margin-bottom: 0.6rem;
  }

  textarea {
    width: 100%;
    min-height: 140px;
    padding: 0.9rem 1rem;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--ink);
    background: #FDFCFB;
    resize: vertical;
    transition: border-color 0.2s;
    line-height: 1.6;
  }

  textarea:focus { outline: none; border-color: var(--accent); }
  textarea::placeholder { color: #C0BAB2; }

  .example-hint {
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #A09B94;
  }

  .example-hint button {
    background: none;
    border: none;
    color: var(--accent);
    font-size: 0.8rem;
    font-family: inherit;
    cursor: pointer;
    text-decoration: underline;
    padding: 0;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--accent);
    color: #FFF;
    border: none;
    padding: 0.85rem 2rem;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    margin-top: 1.2rem;
    width: 100%;
    justify-content: center;
  }

  .btn:hover { background: #A83C13; }
  .btn:active { transform: scale(0.99); }
  .btn:disabled { background: #D0CCC5; cursor: not-allowed; transform: none; }

  .spinner {
    display: none;
    width: 18px; height: 18px;
    border: 2.5px solid rgba(255,255,255,0.35);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  #results { display: none; }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1.5rem;
  }

  .results-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    font-weight: 400;
    color: var(--ink);
  }

  .results-subtitle {
    font-size: 0.8rem;
    color: var(--ink-secondary);
  }

  .genre-list { display: flex; flex-direction: column; gap: 1rem; }

  .genre-item { display: flex; flex-direction: column; gap: 5px; }

  .genre-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .genre-name {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--ink);
  }

  .genre-rank {
    display: inline-block;
    width: 20px;
    height: 20px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-align: center;
    line-height: 20px;
    margin-right: 8px;
    background: var(--accent-soft);
    color: var(--accent);
  }

  .genre-pct {
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--ink-secondary);
  }

  .bar-track {
    background: #F0EDE8;
    border-radius: 99px;
    height: 8px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s cubic-bezier(0.25, 1, 0.5, 1);
    width: 0;
  }

  .divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
  }

  .api-note {
    background: var(--accent-soft);
    border: 1px solid #F2C8B0;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-size: 0.82rem;
    color: #7A3010;
    line-height: 1.6;
    margin-top: 1rem;
  }

  .api-note code {
    background: rgba(201,75,26,0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
  }

  .error-msg {
    display: none;
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    color: #991B1B;
    padding: 0.9rem 1.1rem;
    border-radius: 8px;
    font-size: 0.88rem;
    margin-top: 1rem;
  }

  .footer {
    text-align: center;
    padding: 2rem;
    font-size: 0.78rem;
    color: #C0BAB2;
  }
</style>
</head>
<body>

<div class="header">
  <p class="header-eyebrow">Proyecto 2 · MIAD 2026</p>
  <h1>Clasificador de Géneros de Películas</h1>
  <p>Ingresa la sinopsis de una película en inglés y el modelo predecirá a qué géneros pertenece.</p>
</div>

<div class="main">

  <div class="card instructions">
    <p class="instructions-title">Cómo usar esta herramienta</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-text">
          <strong>Escribe o pega la sinopsis</strong> de la película en el campo de texto. Debe estar en <strong>inglés</strong> para mejores resultados.
        </div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-text">
          Haz clic en <strong>"Predecir géneros"</strong> y espera unos segundos mientras el modelo analiza el texto.
        </div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-text">
          Verás los <strong>5 géneros más probables</strong> con su porcentaje de probabilidad ordenados de mayor a menor.
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <label for="plot-input">Sinopsis de la película (en inglés)</label>
    <textarea
      id="plot-input"
      placeholder="Ejemplo: A young wizard discovers he has magical powers and enrolls at a school for wizards, where he makes friends and enemies while uncovering the truth about his past..."
    ></textarea>
    <p class="example-hint">
      ¿No tienes una sinopsis a mano?
      <button onclick="loadExample()">Cargar ejemplo</button>
    </p>
    <div class="error-msg" id="error-msg"></div>
    <button class="btn" id="predict-btn" onclick="predict()">
      <span id="btn-text">Predecir géneros</span>
      <div class="spinner" id="spinner"></div>
    </button>
  </div>

  <div class="card" id="results">
    <div class="results-header">
      <span class="results-title">Top 5 géneros predichos</span>
      <span class="results-subtitle">Probabilidad del modelo</span>
    </div>
    <div class="genre-list" id="genre-list"></div>
    <hr class="divider">
    <div class="api-note">
      <strong>Uso directo vía API:</strong> también puedes consumir este modelo programáticamente en
      <code>GET /predict/?plot=&lt;sinopsis&gt;</code> — devuelve las 24 probabilidades en formato JSON.
    </div>
  </div>

</div>

<div class="footer">Proyecto 2 · Machine Learning y PLN · Universidad de los Andes · MIAD 2026</div>

<script>
const BAR_COLORS = ['var(--bar-1)','var(--bar-2)','var(--bar-3)','var(--bar-4)','var(--bar-5)'];

const EXAMPLES = [
  "A teenager discovers she has the power to control fire and must learn to master her abilities while fighting an evil corporation that wants to exploit her gifts. Along the way she falls in love with a fellow student who helps her understand her destiny.",
  "In a dystopian future, humanity fights for survival against alien invaders using giant robots piloted by human minds. A veteran soldier and a rookie pilot must overcome their differences to save Earth from total annihilation.",
  "A struggling stand-up comedian in 1950s New York City discovers her hidden talent after her husband leaves her, and she reinvents herself on the comedy circuit while navigating family expectations and forbidden romance."
];

let exampleIdx = 0;

function loadExample() {
  document.getElementById('plot-input').value = EXAMPLES[exampleIdx % EXAMPLES.length];
  exampleIdx++;
}

async function predict() {
  const plot = document.getElementById('plot-input').value.trim();
  const btn = document.getElementById('predict-btn');
  const spinner = document.getElementById('spinner');
  const btnText = document.getElementById('btn-text');
  const errorMsg = document.getElementById('error-msg');

  errorMsg.style.display = 'none';

  if (!plot) {
    errorMsg.textContent = 'Por favor ingresa la sinopsis de una película antes de predecir.';
    errorMsg.style.display = 'block';
    return;
  }

  btn.disabled = true;
  spinner.style.display = 'block';
  btnText.textContent = 'Analizando...';

  try {
    const url = '/predict/?plot=' + encodeURIComponent(plot);
    const res = await fetch(url);
    if (!res.ok) throw new Error('Error del servidor: ' + res.status);
    const data = await res.json();

    const entries = Object.entries(data)
      .map(([k, v]) => ({ genre: k.replace('p_', ''), prob: v }))
      .sort((a, b) => b.prob - a.prob)
      .slice(0, 5);

    const maxProb = entries[0].prob;
    const list = document.getElementById('genre-list');
    list.innerHTML = '';

    entries.forEach((item, i) => {
      const pct = (item.prob * 100).toFixed(1);
      const barWidth = ((item.prob / maxProb) * 100).toFixed(1);
      const div = document.createElement('div');
      div.className = 'genre-item';
      div.innerHTML = \`
        <div class="genre-row">
          <span class="genre-name"><span class="genre-rank">\${i+1}</span>\${item.genre}</span>
          <span class="genre-pct">\${pct}%</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" id="bar-\${i}" style="background:\${BAR_COLORS[i]};"></div>
        </div>
      \`;
      list.appendChild(div);
    });

    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    setTimeout(() => {
      entries.forEach((item, i) => {
        const barWidth = ((item.prob / maxProb) * 100).toFixed(1);
        const bar = document.getElementById('bar-' + i);
        if (bar) bar.style.width = barWidth + '%';
      });
    }, 60);

  } catch (err) {
    errorMsg.textContent = 'Ocurrió un error al conectar con el modelo. Intenta nuevamente en unos segundos.';
    errorMsg.style.display = 'block';
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    btnText.textContent = 'Predecir géneros';
  }
}

document.getElementById('plot-input').addEventListener('keydown', function(e) {
  if (e.ctrlKey && e.key === 'Enter') predict();
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return HTML_PAGE


# --- API REST con documentación Swagger ---
api = Api(
    app,
    version="1.0",
    title="Movie Genre Classifier",
    description="Proyecto 2 — Clasificación multilabel de géneros a partir del plot.",
    doc="/docs",
)

ns = api.namespace("predict", description="Movie Genre Predictor")

parser = api.parser()
parser.add_argument(
    "plot",
    type=str,
    required=True,
    help="Sinopsis de la película (en inglés)",
    location="args",
)

genre_fields = api.model(
    "GenreProbabilities",
    {
        "p_Action": fields.Float, "p_Adventure": fields.Float, "p_Animation": fields.Float,
        "p_Biography": fields.Float, "p_Comedy": fields.Float, "p_Crime": fields.Float,
        "p_Documentary": fields.Float, "p_Drama": fields.Float, "p_Family": fields.Float,
        "p_Fantasy": fields.Float, "p_Film-Noir": fields.Float, "p_History": fields.Float,
        "p_Horror": fields.Float, "p_Music": fields.Float, "p_Musical": fields.Float,
        "p_Mystery": fields.Float, "p_News": fields.Float, "p_Romance": fields.Float,
        "p_Sci-Fi": fields.Float, "p_Short": fields.Float, "p_Sport": fields.Float,
        "p_Thriller": fields.Float, "p_War": fields.Float, "p_Western": fields.Float,
    },
)


@ns.route("/")
class MovieGenreApi(Resource):
    @api.doc(parser=parser)
    @api.marshal_with(genre_fields)
    def get(self):
        args = parser.parse_args()
        probs = predict_genres(args["plot"])
        return {f"p_{g}": p for g, p in probs.items()}, 200


# Para AWS Elastic Beanstalk: el WSGI espera la variable `application`.
application = app

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
