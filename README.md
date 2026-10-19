# SALAM HALAL INTELLIGENCE

**Plateforme intelligente de suivi industriel et d'aide à la décision**  
**PROTOTYPE ACADÉMIQUE — DONNÉES SIMULÉES**

## 1) Vue d'ensemble
Ce dépôt contient un prototype académique Streamlit pour illustrer le suivi de production, la traçabilité, la gestion des stocks, la surveillance de la chaîne du froid et une expérimentation de prévision de la demande.

> Important : les enregistrements générés par l'application sont explicitement marqués **SIMULATED DATA**. Le projet ne représente pas des données opérationnelles réelles de Salam Halal.

## 2) Objectifs académiques
- Montrer une architecture séparant UI, accès données, logique métier, simulation et forecasting.
- Démontrer des contrôles de base (contraintes SQL, validation, transactions).
- Illustrer une approche honnête de prévision avec split chronologique, baseline et métriques sur test.

## 3) Fonctionnalités
- **Tableau de bord** : KPI DB, graphiques production/produits/température/stocks, alertes.
- **Production et traçabilité** : création de lots, validation, recherche/filtres, détails/historique.
- **Gestion des stocks** : entrées/sorties, prévention stock négatif, alertes stock bas, export CSV.
- **Dates de péremption** : expirés, proches, manquants, lots à revoir (alerte administrative).
- **Chaîne du froid** : saisie relevés, série temporelle, seuils, stats, mesures à revoir.
- **Prévision de la demande** : fallback moyenne mobile si données limitées, RandomForest si suffisant, MAE/RMSE sur test, prévision 7 jours.

## 4) Stack technique
- Python 3
- Streamlit
- Pandas
- NumPy
- Plotly
- scikit-learn
- sqlite3
- pytest

## 5) Architecture
```
app.py
requirements.txt
README.md
src/
  config.py
  database/
    __init__.py
    connection.py
    schema.py
    repositories.py
  processing/
    __init__.py
    validation.py
    inventory.py
    expiration.py
    cold_chain.py
  forecasting/
    __init__.py
    features.py
    demand_model.py
  simulation/
    __init__.py
    data_generator.py
  ui/
    __init__.py
    dashboard.py
    batches_page.py
    inventory_page.py
    expiration_page.py
    cold_chain_page.py
    forecasting_page.py
    about_page.py
tests/
  test_validation.py
  test_inventory.py
  test_expiration.py
  test_cold_chain.py
  test_forecasting.py
```

## 6) Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7) Lancement de l'application
```bash
streamlit run app.py
```

## 8) Exécution des tests
```bash
pytest -q
```

## 9) Base de données SQLite
- Fichier local : `data/salam_halal_intelligence.db`
- Initialisation automatique au démarrage de l'app.
- Clés étrangères activées (`PRAGMA foreign_keys = ON`).
- Tables normalisées : `products`, `batches`, `inventory_movements`, `temperature_measurements`, `sales`.
- Contraintes clés : unicité code lot, quantités > 0 (ou >= 0 ventes), index principaux, liens FK.
- Création de lot atomique : insertion du lot + mouvement de production exactement une fois dans une transaction.

## 10) Sources de données et licences
- Aucune source externe publique n'est intégrée par défaut dans ce MVP.
- Les séries de ventes, températures et opérations sont **simulées de manière déterministe** (seed fixe) pour démonstration académique.
- Si un dataset public est ajouté plus tard, il doit être conservé séparément dans `data/raw/` avec source et licence documentées.

## 11) Distinction réel vs simulé
- Les enregistrements générés portent explicitement le marquage **SIMULATED DATA**.
- Les analyses, alertes et prévisions de ce prototype ne doivent pas être interprétées comme résultats réels d'exploitation.

## 12) Limites
- Seuils de température paramétrables mais non universels.
- Prévision simplifiée (variables limitées, horizon court de démonstration).
- Portée stock centrée sur produits finis.

## 13) Pistes d'amélioration
- Import de datasets publics (avec attribution/licence) via module dédié.
- Contrôles qualité de données plus avancés.
- Gestion multi-sites et rôles utilisateurs.
- Historisation plus riche des événements traçabilité.
