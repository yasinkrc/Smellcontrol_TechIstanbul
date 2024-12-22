from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model and scaler
model = joblib.load('knn_classifier.pkl')
scaler = joblib.load('scaler.pkl')

# Define the class names
class_names = {0: 'air', 1: 'coffe', 2: 'kolonya'}

def generate_random_features(num_features=66):
    return np.random.rand(num_features).tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_features', methods=['POST'])
def generate_features():
    # Generate random features
    random_features = generate_random_features()
    features = np.array(random_features).reshape(1, -1)

    # Scale the features
    scaled_features = scaler.transform(features)

    # Predict using the model
    try:
        prediction = model.predict(scaled_features)
        predicted_class = prediction[0]
        class_name = class_names[predicted_class]
        print("Something predicted")
        image_name = f'{class_name}.jpg'
        return jsonify({'class_name': class_name, 'image_name': image_name})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
