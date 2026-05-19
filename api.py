"""API REST para predecir las probabilidades de género de una película a partir
de su plot (sinopsis). Compatible con AWS Elastic Beanstalk: la variable WSGI
se llama `application`.
"""
from flask import Flask
from flask_restx import Api, Resource, fields

from movie_genre_model import predict_genres

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Movie Genre Classifier",
    description="Proyecto 2 — Clasificación multilabel de géneros a partir del plot.",
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
