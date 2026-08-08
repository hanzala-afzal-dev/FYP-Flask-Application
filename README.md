# Signed Link Prediction on the Epinions Trust Network

Final Year Project (Bachelor's) — a Flask web application that predicts the **sign of a relationship** between two users in a signed social network: trust (positive), distrust (negative), or no relationship (missing edge). The underlying model is trained on the [Epinions](http://www.trustlet.org/epinions.html) trust/distrust dataset.

#### Home Page
![Home Page](https://img.techpowerup.org/201010/fyp-home.png)
#### Result
![Home Page/Result](https://img.techpowerup.org/201010/fyp-result.png)
#### Dashboard
![Dashboard](https://img.techpowerup.org/201010/fyp-dashboard.png)

## Overview

Epinions is a "who-trust-whom" social network where each edge between two users is labeled as trust (+1) or distrust (-1). This project treats sign prediction as a supervised learning problem over graph embeddings, and wraps the resulting model in a web app where a logged-in user can enter two node IDs and get a live prediction, with a history/dashboard of past predictions.

The model-training pipeline lives in [`Epinions (2).ipynb`](Epinions%20(2).ipynb); the trained artifacts are served by the Flask app in [`app.py`](app.py).

## Methodology

1. **Preprocessing** — load the Epinions edge list (`source`, `target`, `sign`) and split into train/test sets.
2. **Community detection** — split the training graph into 3 sub-communities using Newman's leading eigenvector method (`igraph`), maximizing modularity.
3. **Class balancing** — oversample the minority class within each community so trust/distrust/missing edges are better represented.
4. **Missing-edge generation** — sample non-existent edges within each community to represent the "no relationship" class.
5. **Node embeddings** — learn 128-dimensional node embeddings per community with `node2vec` (biased random walks + `gensim` Word2Vec).
6. **Edge embeddings** — combine two node embeddings into an edge embedding via element-wise (Hadamard) product.
7. **Model training** — train one classifier per community (decision tree / ensemble variants were evaluated, including `BalancedBaggingClassifier`, `RandomForestClassifier`, `ExtraTreesClassifier`, and `LogisticRegression`).
8. **Ensembling** — at inference time, all 3 community models vote on an edge; the majority label (positive / negative / no relationship) is returned.

The 3 trained community models are pickled as [`static/data/_com0.pkl`](static/data/_com0.pkl), [`_com1.pkl`](static/data/_com1.pkl), [`_com2.pkl`](static/data/_com2.pkl), and loaded by [`model_api.py`](model_api.py) at prediction time.

## Features

- **Link prediction** — enter two node IDs and get a live trust/distrust/no-relationship prediction ([`app.py`](app.py))
- **User accounts** — signup, login, logout, profile & password management ([`mypanel.py`](mypanel.py))
- **Prediction history & dashboard** — every prediction a user makes is stored and summarized with a simple trust/distrust score
- **About page** describing the project

## Tech stack

- **Backend**: Flask, Flask-MySQLdb
- **Database**: MySQL (user accounts, node embeddings, prediction history)
- **ML / graph**: scikit-learn, imbalanced-learn, node2vec, networkx, python-igraph, gensim, NumPy, pandas
- **Deployment**: gunicorn (see [`Procfile`](Procfile))

## Project structure

```
app.py            # Flask app: routes, MySQL connection, /predict endpoint
mypanel.py         # Blueprint: auth, dashboard, history, profile
model_api.py        # Loads the 3 pickled community models and majority-votes a prediction
Epinions (2).ipynb    # Data prep, community detection, node2vec, model training/evaluation
static/data/         # Pickled models (_com0/1/2.pkl) + sample node IDs (dummy_nodes.csv)
templates/          # Jinja templates (landing page, about, login/signup/dashboard/history)
```

## Running locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a MySQL database (`nodes` by default, see `app.config` in [`app.py`](app.py)) with the following tables — there's no schema file in the repo, so create them to match the queries in `app.py` / `mypanel.py`:
   - `tbl_users(id, email, password, name)`
   - `tbl_predicted(id, user_id, node1, node2, sign)`
   - `embeds(node, <128 embedding columns>)` — populated from the node2vec embeddings produced in the notebook
3. Update the `MYSQL_*` values in [`app.py`](app.py) to match your local MySQL setup.
4. Run the app:
   ```bash
   python app.py
   ```

## Notes

This was built as an academic proof of concept, not a production system — database credentials and the Flask secret key are hardcoded for local development, and passwords are stored in plain text. Harden these before deploying anywhere public.
