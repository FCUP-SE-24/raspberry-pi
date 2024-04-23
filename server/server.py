from flask import Flask, jsonify, request
from communication.comm import get_bowl_weight


app = Flask(__name__)

bowls_data = {
    'Bowl 1': {
        'daily_dose': 50,
        'weight': 110
    },
    'Bowl 2': {
        'daily_dose': 40,
        'weight': 100
    },
    'Bowl 3': {
        'daily_dose': 60,
        'weight': 95
    }
}

@app.route('/add_bowl', methods=['POST'])
def add_bowl():
    data = request.json
    new_bowl_name = data.get('bowl_name')
    
    # Verifica se a tigela já existe
    if new_bowl_name in bowls_data:
        return jsonify({'error': 'Bowl already exists'}), 400
    
    # Adiciona a nova tigela com peso zero
    bowls_data[new_bowl_name] = {'daily_dose': 0, 'weight': 0}
    
    # Solicita o peso da nova tigela ao Arduino
    new_bowl_weight = get_bowl_weight(new_bowl_name)
    bowls_data[new_bowl_name]['weight'] = new_bowl_weight
    
    return jsonify({'message': f'Bowl {new_bowl_name} added successfully', 'weight': new_bowl_weight})

@app.route('/get_bowls_list', methods=['GET'])
def get_bowls_list():
    bowls_list = list(bowls_data.keys())
    return jsonify({'bowls': bowls_list})

@app.route('/get_daily_dose/<bowl_name>', methods=['GET'])
def get_daily_dose(bowl_name):
    bowl = bowls_data.get(bowl_name)
    if bowl:
        return jsonify({'bowl': bowl_name, 'daily_dose': bowl['daily_dose']})
    else:
        return jsonify({'error': 'Bowl not found'}), 404

@app.route('/set_daily_dose/<bowl_name>', methods=['PUT'])
def set_daily_dose(bowl_name):
    bowl = bowls_data.get(bowl_name)
    if bowl:
        data = request.json
        new_daily_dose = data.get('daily_dose')
        bowl['daily_dose'] = new_daily_dose
        return jsonify({'message': f'Daily dose for {bowl_name} updated successfully'})
    else:
        return jsonify({'error': 'Bowl not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
