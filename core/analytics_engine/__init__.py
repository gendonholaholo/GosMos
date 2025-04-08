import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import List, Dict, Optional
import statsmodels.api as sm
from lightgbm import LGBMRegressor

class TrendAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def analyze_trends(self, window: int = 7) -> Dict:
        """
        Analyze trends using moving averages and seasonal decomposition.
        """
        # Calculate moving average
        self.data['moving_avg'] = self.data['sales'].rolling(window=window).mean()
        
        # Seasonal decomposition
        decomposition = sm.tsa.seasonal_decompose(
            self.data['sales'].fillna(method='ffill'),
            period=window
        )
        
        return {
            'trend': decomposition.trend.to_dict(),
            'seasonal': decomposition.seasonal.to_dict(),
            'residual': decomposition.resid.to_dict(),
            'moving_avg': self.data['moving_avg'].to_dict()
        }

class RevenueEstimator:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.models = {
            'random_forest': RandomForestRegressor(),
            'lightgbm': LGBMRegressor()
        }
    
    def train(self, target: str = 'revenue', features: List[str] = None):
        """
        Train revenue estimation models.
        """
        if features is None:
            features = ['views', 'likes', 'comments', 'shares']
        
        X = self.data[features]
        y = self.data[target]
        
        for name, model in self.models.items():
            model.fit(X, y)
    
    def predict(self, features: Dict) -> Dict:
        """
        Predict revenue using trained models.
        """
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict([list(features.values())])[0]
        return predictions

class OutlierDetector:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.scaler = StandardScaler()
    
    def detect_zscore(self, threshold: float = 3.0) -> List[int]:
        """
        Detect outliers using Z-score method.
        """
        scaled_data = self.scaler.fit_transform(self.data[['sales']])
        z_scores = np.abs(scaled_data)
        return np.where(z_scores > threshold)[0].tolist()
    
    def detect_isolation_forest(self, contamination: float = 0.1) -> List[int]:
        """
        Detect outliers using Isolation Forest.
        """
        clf = IsolationForest(contamination=contamination)
        predictions = clf.fit_predict(self.data[['sales']])
        return np.where(predictions == -1)[0].tolist()

class CreatorClusterer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
    
    def cluster_kmeans(self, n_clusters: int = 5) -> Dict:
        """
        Cluster creators using K-means.
        """
        features = ['followers', 'products', 'rating']
        scaled_data = self.scaler.fit_transform(self.data[features])
        reduced_data = self.pca.fit_transform(scaled_data)
        
        kmeans = KMeans(n_clusters=n_clusters)
        clusters = kmeans.fit_predict(reduced_data)
        
        return {
            'labels': clusters.tolist(),
            'centers': kmeans.cluster_centers_.tolist(),
            'explained_variance': self.pca.explained_variance_ratio_.tolist()
        }
    
    def cluster_dbscan(self, eps: float = 0.5, min_samples: int = 5) -> Dict:
        """
        Cluster creators using DBSCAN.
        """
        features = ['followers', 'products', 'rating']
        scaled_data = self.scaler.fit_transform(self.data[features])
        reduced_data = self.pca.fit_transform(scaled_data)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(reduced_data)
        
        return {
            'labels': clusters.tolist(),
            'explained_variance': self.pca.explained_variance_ratio_.tolist()
        }

class AnalyticsEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.trend_analyzer = TrendAnalyzer(data)
        self.revenue_estimator = RevenueEstimator(data)
        self.outlier_detector = OutlierDetector(data)
        self.creator_clusterer = CreatorClusterer(data)
    
    def analyze(self, analysis_type: str, **kwargs) -> Dict:
        """
        Perform various types of analysis based on the specified type.
        """
        if analysis_type == 'trends':
            return self.trend_analyzer.analyze_trends(**kwargs)
        elif analysis_type == 'revenue':
            return self.revenue_estimator.predict(**kwargs)
        elif analysis_type == 'outliers':
            return {
                'zscore': self.outlier_detector.detect_zscore(**kwargs),
                'isolation_forest': self.outlier_detector.detect_isolation_forest(**kwargs)
            }
        elif analysis_type == 'clusters':
            return {
                'kmeans': self.creator_clusterer.cluster_kmeans(**kwargs),
                'dbscan': self.creator_clusterer.cluster_dbscan(**kwargs)
            }
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}") 