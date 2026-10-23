from functools import lru_cache

from fastapi import FastAPI, HTTPException, Response

from churn.config import settings
from churn.data import carregar_dados, validar_dados
from churn.features import construir_features
from churn.model import load_model

app = FastAPI(title="Churn API")


@lru_cache(maxsize=1)
def _modelo():
    return load_model(settings.model_path)


@lru_cache(maxsize=1)
def _base():
    """Ids, features e o código de 'Yes' na MESMA codificação usada no treino."""
    df = validar_dados(carregar_dados(settings.data_path))
    X, _ = construir_features(df, settings.target, settings.id_column)
    # features.py transforma o target em códigos (No=0, Yes=1), então o modelo
    # não conhece a string "Yes" - precisamos do código equivalente.
    codigo_yes = list(df[settings.target].astype("category").cat.categories).index("Yes")
    return df[settings.id_column], X, codigo_yes


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """O navegador pede isso sozinho; sem rota ele polui o log com 404."""
    return Response(status_code=204)


@app.get("/predict/{customer_id}")
def predict(customer_id: str) -> dict:
    """Probabilidade de churn de um cliente pelo customerID."""
    ids, X, codigo_yes = _base()

    encontrados = ids[ids == customer_id]
    if encontrados.empty:
        raise HTTPException(
            status_code=404, detail=f"cliente {customer_id} não encontrado"
        )

    indice = encontrados.index[0]
    if indice not in X.index:
        raise HTTPException(
            status_code=422, detail=f"cliente {customer_id} tem dados inválidos"
        )

    modelo = _modelo()
    probabilidades = modelo.predict_proba(X.loc[[indice]])[0]
    prob = float(probabilidades[list(modelo.classes_).index(codigo_yes)])

    return {
        "customerID": customer_id,
        "churn_probability": round(prob, 4),
        "churn_prediction": "Yes" if prob >= 0.5 else "No",
    }
