from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import os

# Defina o caminho completo para a pasta de templates
app = Flask(__name__, template_folder='../templates')
UPLOAD_FOLDER = '../uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar o diretório de uploads se ele não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and file2:
            file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
            
            file1.save(file1_path)
            file2.save(file2_path)
            
            planilha1 = pd.read_excel(file1_path)
            planilha2 = pd.read_excel(file2_path)

            # Verificar as colunas e ajustar conforme necessário
            planilha1.columns = ['Cliente', 'Valor']
            planilha2.columns = ['Cliente', 'Valor']

            merged_df = planilha1.merge(planilha2, on='Cliente', suffixes=('_planilha1', '_planilha2'))
            
            # Definir a tolerância para a comparação dos valores
            tol = 1e-10

            # Filtrar as diferenças dentro da tolerância
            diferencas = merged_df[abs(merged_df['Valor_planilha1'] - merged_df['Valor_planilha2']) > tol]
            
            # Calcular a diferença
            diferencas['Diferenca'] = diferencas['Valor_planilha1'] - diferencas['Valor_planilha2']

            # Renomear as colunas
            diferencas = diferencas.rename(columns={
                'Valor_planilha1': 'ERP',
                'Valor_planilha2': 'PBI'
            })

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'diferencas.xlsx')
            diferencas.to_excel(output_path, index=False)

            return redirect(url_for('download_file', filename='diferencas.xlsx'))

    return render_template('index.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)