"""API REST para predecir las probabilidades de género de una película a partir
de su plot (sinopsis). Compatible con AWS Elastic Beanstalk: la variable WSGI
se llama `application`.
"""
from flask import Flask
from flask_restx import Api, Resource, fields
from movie_genre_model import predict_genres

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clasificador de Géneros de Películas</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background-color: #EAEDF2;
  font-family: 'DM Sans', sans-serif;
  color: #0D1826;
  min-height: 100vh;
}

.header {
  background: #0F2952;
  padding: 3rem 2rem 2.5rem;
  text-align: center;
}
.header h1 {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 400;
  color: #E8F0FF;
  line-height: 1.2;
  max-width: 600px;
  margin: 0 auto 1rem;
}
.header p {
  color: #8AAAD4;
  font-size: 1rem;
  font-weight: 300;
  max-width: 480px;
  margin: 0 auto;
  line-height: 1.6;
}

.main {
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

.card {
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #C8D0DF;
  padding: 2rem;
  margin-bottom: 1rem;
}

.step-inline {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.7rem;
  margin: 1.5rem 0 0.5rem;
  font-size: 0.92rem;
  color: #0D1826;
}
.step-circle {
  min-width: 22px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1A4FBF;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #4A5B7A;
  margin-bottom: 0.6rem;
}

textarea {
  width: 100%;
  min-height: 140px;
  padding: 0.9rem 1rem;
  border: 1.5px solid #C8D0DF;
  border-radius: 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  color: #0D1826;
  background: #F5F7FB;
  resize: vertical;
  transition: border-color 0.2s;
  line-height: 1.6;
}
textarea:focus { outline: none; border-color: #1A4FBF; }
textarea::placeholder { color: #9AAAC0; }

.example-hint {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #8AAAD4;
}
.example-hint button {
  background: none; border: none;
  color: #1A4FBF; font-size: 0.8rem;
  font-family: inherit; cursor: pointer;
  text-decoration: underline; padding: 0;
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #1A4FBF;
  color: #fff;
  border: none;
  padding: 0.9rem 2rem;
  border-radius: 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
  margin-bottom: 1rem;
}
.btn:hover { background: #1438A0; }
.btn:disabled { background: #8AAAD4; cursor: not-allowed; }

.spinner {
  display: none;
  width: 18px; height: 18px;
  border: 2.5px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-msg {
  display: none;
  background: #EEF2FF;
  border: 1px solid #A8BCE8;
  color: #0A2A7A;
  padding: 0.9rem 1.1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  margin-top: 1rem;
}

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
}
.results-subtitle { font-size: 0.8rem; color: #4A5B7A; }

.genre-list { display: flex; flex-direction: column; gap: 1rem; }
.genre-item { display: flex; flex-direction: column; gap: 5px; }
.genre-row { display: flex; justify-content: space-between; align-items: baseline; }
.genre-name { font-size: 0.95rem; font-weight: 500; }
.genre-rank {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 4px;
  font-size: 11px; font-weight: 600;
  background: #E8EEFA; color: #1A4FBF;
  margin-right: 8px;
}
.genre-pct { font-size: 0.88rem; font-weight: 500; color: #4A5B7A; }
.bar-track { background: #E2E8F0; border-radius: 99px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; transition: width 0.8s cubic-bezier(0.25,1,0.5,1); width: 0; }

.divider { border: none; border-top: 1px solid #C8D0DF; margin: 1.5rem 0; }

.api-note {
  background: #E8EEFA;
  border: 1px solid #A8BCE8;
  border-radius: 8px;
  padding: 1rem 1.2rem;
  font-size: 0.82rem;
  color: #0A2A7A;
  line-height: 1.6;
}
.api-note code {
  background: rgba(26,79,191,0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.footer {
  text-align: center;
  padding: 2rem 1.5rem 2.5rem;
  background: #0F2952;
  line-height: 1.9;
}
.footer-team { color: #E0ECFF; font-size: 0.88rem; margin-bottom: 0.4rem; }
.footer-uni { color: #6B9FFF; font-size: 0.78rem; }
</style>
</head>
<body>

<div class="header">
  <h1>Clasificador de Géneros de Películas</h1>
  <p>Ingresa la sinopsis de una película en inglés y el modelo predecirá a qué géneros pertenece.</p>
</div>

<div class="main">

  <div class="step-inline">
    <span class="step-circle">1</span>
    <span><strong>Escribe o pega la sinopsis</strong> de la película en inglés</span>
  </div>
  <div class="card">
    <label for="plot-input">Sinopsis de la película (en inglés)</label>
    <textarea id="plot-input" placeholder="Ejemplo: A young wizard discovers he has magical powers and enrolls at a school for wizards, where he makes friends and enemies while uncovering the truth about his past..."></textarea>
    <p class="example-hint">¿No tienes una sinopsis a mano? <button onclick="loadExample()">Cargar ejemplo</button></p>
    <div class="error-msg" id="error-msg"></div>
  </div>

  <div class="step-inline">
    <span class="step-circle">2</span>
    <span>Haz clic en <strong>"Predecir géneros"</strong> y espera unos segundos mientras el modelo analiza el texto</span>
  </div>
  <button class="btn" id="predict-btn" onclick="predict()">
    <span id="btn-text">Predecir géneros</span>
    <div class="spinner" id="spinner"></div>
  </button>

  <div class="step-inline" id="step3-label" style="display:none;">
    <span class="step-circle">3</span>
    <span>Verás los <strong>5 géneros más probables</strong> con su porcentaje de probabilidad</span>
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

<div class="footer">
  <div class="footer-team">
    <strong>Proyecto No. 2 · Realizado por:</strong><br>
    Carlos Francisco Aparicio Rojas · Dayana Franco Salcedo<br>
    Jair Mauricio Henao Casallas · Harol Herney Perafan Velasco
  </div>
  <div class="footer-uni">Maestría en Inteligencia Analítica de Datos · Universidad de los Andes · 2026</div>
</div>

<script>
const BAR_COLORS = ['#1A3FAF','#2C6DD4','#4A96E8','#7AB8F0','#B8D8F8'];

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
    const res = await fetch('/predict/?plot=' + encodeURIComponent(plot));
    if (!res.ok) throw new Error('Error ' + res.status);
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
      const div = document.createElement('div');
      div.className = 'genre-item';
      div.innerHTML =
        '<div class="genre-row">' +
          '<span class="genre-name"><span class="genre-rank">' + (i+1) + '</span>' + item.genre + '</span>' +
          '<span class="genre-pct">' + pct + '%</span>' +
        '</div>' +
        '<div class="bar-track"><div class="bar-fill" id="bar-' + i + '" style="background:' + BAR_COLORS[i] + ';"></div></div>';
      list.appendChild(div);
    });

    document.getElementById('results').style.display = 'block';
    document.getElementById('step3-label').style.display = 'flex';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    setTimeout(function() {
      entries.forEach(function(item, i) {
        var bar = document.getElementById('bar-' + i);
        if (bar) bar.style.width = ((item.prob / maxProb) * 100).toFixed(1) + '%';
      });
    }, 60);

  } catch(err) {
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


application = app

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
