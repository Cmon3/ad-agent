import tensorflow as tf
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from datetime import datetime

class AdRatingModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'scroll_distance',
            'time_spent',
            'click_count',
            'ad_position',
            'image_present',
            'video_present',
            'text_length'
        ]
        self.setup_model()

    def setup_model(self):
        """Initialize the neural network model"""
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(len(self.feature_names),)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')  # Binary classification for ad rating
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

    def extract_features(self, action_data):
        """Extract relevant features from recorded actions"""
        features = {name: 0 for name in self.feature_names}
        
        # Process action data
        for action in action_data:
            if action['type'] == 'scroll':
                features['scroll_distance'] += abs(action['params'].get('amount', 0))
            elif action['type'] == 'click':
                features['click_count'] += 1
            
            # Calculate time spent (if timestamps available)
            if len(action_data) > 1:
                start_time = datetime.fromisoformat(action_data[0]['timestamp'])
                end_time = datetime.fromisoformat(action_data[-1]['timestamp'])
                features['time_spent'] = (end_time - start_time).total_seconds()
        
        return np.array([list(features.values())])

    def train(self, action_sequences, ratings):
        """Train the model on user demonstrations"""
        X = []
        for sequence in action_sequences:
            features = self.extract_features(sequence)
            X.append(features[0])
        
        X = np.array(X)
        y = np.array(ratings)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        history = self.model.fit(
            X_scaled, y,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=1
        )
        
        return history

    def predict(self, action_data):
        """Predict rating based on current action sequence"""
        features = self.extract_features(action_data)
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)
        return float(prediction[0][0])

    def save(self, path='models'):
        """Save the model and scaler"""
        os.makedirs(path, exist_ok=True)
        self.model.save(os.path.join(path, 'ad_rating_model'))
        joblib.dump(self.scaler, os.path.join(path, 'scaler.pkl'))

    def load(self, path='models'):
        """Load the model and scaler"""
        try:
            self.model = tf.keras.models.load_model(os.path.join(path, 'ad_rating_model'))
            self.scaler = joblib.load(os.path.join(path, 'scaler.pkl'))
            return True
        except:
            return False

class TrainingSession:
    def __init__(self):
        self.action_sequences = []
        self.ratings = []
        self.current_sequence = []
        self.model = AdRatingModel()

    def start_sequence(self):
        """Start recording a new action sequence"""
        self.current_sequence = []

    def add_action(self, action):
        """Add an action to the current sequence"""
        self.current_sequence.append(action)

    def end_sequence(self, rating):
        """End current sequence and add rating"""
        if self.current_sequence:
            self.action_sequences.append(self.current_sequence.copy())
            self.ratings.append(rating)
            self.current_sequence = []

    def train_model(self):
        """Train the model on collected sequences"""
        if not self.action_sequences:
            return None
        return self.model.train(self.action_sequences, self.ratings)

    def save_training_data(self, path='training_data'):
        """Save training data to file"""
        os.makedirs(path, exist_ok=True)
        data = {
            'sequences': self.action_sequences,
            'ratings': self.ratings
        }
        filename = os.path.join(path, f'training_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4, default=str)

    def load_training_data(self, filename):
        """Load training data from file"""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.action_sequences = data['sequences']
            self.ratings = data['ratings']
