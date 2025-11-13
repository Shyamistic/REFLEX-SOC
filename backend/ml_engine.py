import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import time
from typing import List, Dict

class MLThreatDetector:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.baseline_features = []
        self.is_trained = False
        self.threat_history = []
    
    def extract_features(self, event: Dict) -> List[float]:
        """Extract numerical features from security event"""
        features = [
            1.0 if event.get("event_type") == "process_start" else 0.0,
            1.0 if event.get("event_type") == "file_write" else 0.0,
            1.0 if event.get("event_type") == "network_connection" else 0.0,
            float(event.get("threat_score", 0)) / 100.0,
            1.0 if "curl" in str(event.get("details", {})).lower() else 0.0,
            1.0 if "bash" in str(event.get("details", {})).lower() else 0.0,
        ]
        return features
    
    def learn_baseline(self, events: List[Dict]):
        """Learn behavioral baseline from event history"""
        if len(events) < 10:
            return False
        
        features_list = []
        for event in events[-100:]:  # Use last 100 events
            features = self.extract_features(event)
            features_list.append(features)
        
        if len(features_list) < 10:
            return False
        
        X = np.array(features_list)
        self.baseline_features = X
        
        try:
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
            print("✅ ML Model trained on baseline")
            return True
        except Exception as e:
            print(f"❌ ML training failed: {e}")
            return False
    
    def detect_anomaly(self, event: Dict) -> Dict:
        """Detect anomalies using ML model"""
        if not self.is_trained:
            # Fallback to rule-based
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "method": "untrained",
                "reasoning": "Model not yet trained"
            }
        
        try:
            features = np.array([self.extract_features(event)])
            X_scaled = self.scaler.transform(features)
            
            # -1 = anomaly, 1 = normal
            prediction = self.model.predict(X_scaled)[0]
            anomaly_score = abs(self.model.score_samples(X_scaled)[0])
            
            is_anomaly = prediction == -1
            
            result = {
                "is_anomaly": is_anomaly,
                "anomaly_score": float(anomaly_score),
                "method": "isolation_forest",
                "reasoning": f"Anomaly score: {anomaly_score:.3f} (threshold: 0.5)"
            }
            
            self.threat_history.append({
                "event_id": event.get("agent_id", "unknown"),
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "timestamp": int(time.time())
            })
            
            return result
        except Exception as e:
            print(f"❌ Anomaly detection failed: {e}")
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "method": "error",
                "reasoning": str(e)
            }
    
    def get_detection_stats(self) -> Dict:
        """Get ML detection statistics"""
        if not self.threat_history:
            return {"total": 0, "anomalies": 0, "detection_rate": 0.0}
        
        total = len(self.threat_history)
        anomalies = sum(1 for t in self.threat_history if t["is_anomaly"])
        
        return {
            "total_events_analyzed": total,
            "anomalies_detected": anomalies,
            "detection_rate": round(anomalies / total * 100, 2),
            "avg_anomaly_score": round(np.mean([t["score"] for t in self.threat_history]), 3),
            "model_status": "trained" if self.is_trained else "untrained"
        }

# Global detector instance
detector = MLThreatDetector()
