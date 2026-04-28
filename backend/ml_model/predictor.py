"""
ML Model loader and predictor for membrane rejection rate prediction.
"""
import os
import xgboost as xgb
import numpy as np
from typing import List, Optional

# Use environment variable or workspace default
MODEL_PATH = os.environ.get('MODEL_PATH', '/workspace/XGBoost_mem_OMPS_model.json')

# Feature names as expected by the model (in order)
# Model feature names: ['MWCO', 'Contact angle', 'Zeta potential', 'MW', 'Neutral charge', 'Neutral logD']
MODEL_FEATURE_NAMES = [
    'MWCO',
    'Contact angle',
    'Zeta potential',
    'MW',
    'Neutral charge',
    'Neutral logD'
]


class RejectionPredictor:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_path: str = None):
        if model_path is None:
            model_path = MODEL_PATH
        if self._model is None:
            self._model = xgb.XGBRegressor()
            self._model.load_model(model_path)
            print(f"Model loaded from {model_path}")
            print(f"Feature names: {self._model.feature_names_in_}")
            print(f"Number of features: {self._model.n_features_in_}")
        return self

    def predict(self, features: List[float]) -> float:
        """Predict rejection rate from feature vector."""
        if self._model is None:
            self.load_model()

        feature_array = np.array(features).reshape(1, -1)
        prediction = self._model.predict(feature_array)[0]
        # Clamp to 0-100 range
        prediction = float(np.clip(prediction, 0, 100))
        return prediction

    def predict_from_dict(self, feature_dict: dict) -> float:
        """
        Predict from a dictionary of features.
        feature_dict keys: MW, charge, logD, MWCO, contact_angle, zeta_potential
        """
        if self._model is None:
            self.load_model()

        # Build feature vector in model's expected order
        # Model expects: ['MWCO', 'Contact angle', 'Zeta potential', 'MW', 'Neutral charge', 'Neutral logD']
        feature_vector = [
            feature_dict.get('MWCO'),
            feature_dict.get('contact_angle'),
            feature_dict.get('zeta_potential'),
            feature_dict.get('MW'),
            feature_dict.get('charge'),
            feature_dict.get('logD'),
        ]
        return self.predict(feature_vector)


# Singleton instance
_predictor = None


def get_predictor() -> RejectionPredictor:
    global _predictor
    if _predictor is None:
        _predictor = RejectionPredictor()
        _predictor.load_model()
    return _predictor
