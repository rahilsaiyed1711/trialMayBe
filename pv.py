import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from google.cloud import bigquery

project_id = 'agel-svc-winddata-dmz-prod'
client = bigquery.Client(project=project_id)
Tablename = "Static_plants"

# Assuming selectQuery is defined and correct
selectQuery = f"SELECT * FROM {project_id}.{Tablename}"
df = client.query(selectQuery).to_dataframe()
plants = df.Plantname.unique()

def listToString(s):
    return "".join(s)

def remove(string):
    return string.replace(" ", "")

app = Flask(__name__)

@app.route('/load_data')
def load_data():
    plant = request.args.get('plant')
    block = request.args.get('block')
    
    filter_plant = df[df['Plantname'] == plant]
    mytable = filter_plant.Tablename.unique()
    mytable = listToString(mytable)
    mytable = remove(mytable)
    
    selectQuery = f"SELECT * FROM {project_id}.winddata.{mytable}"
    df1 = client.query(selectQuery).to_dataframe()
    df2 = df1[df1['Plant'] == plant]
    
    if block:
        block_data = df2[df2['Block'] == block]
        return jsonify(block_data.to_dict(orient='records'))
    
    blocks = df2.Block.unique()
    return jsonify(blocks.tolist())

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PV Form</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #ffffff;
                margin: 0;
                padding: 20px;
            }

            h1 {
                font-size: 5rem;
                color: #333;
                text-align: center;
                animation: colorChange infinite 3s;
            }

            @keyframes colorChange {
                0% { color: #0a7caa; }
                25% { color: #5b58a5; }
                50% { color: #0056b3; }
                75% { color: #8f298f; }
                100% { color: #0a7caa; }
            }

            button {
                display: block;
                width: 150px;
                padding: 10px;
                margin: 20px auto;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            button:hover {
                background-color: #0056b3;
            }

            #tabs {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }

            .tab {
                padding: 10px 20px;
                margin: 0 5px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            .tab:hover {
                background-color: #0056b3;
            }

            #data {
                margin-top: 20px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            th, td {
                padding: 10px;
                text-align: left;
                border: 1px solid #ddd;
            }

            th {
                background-color: #007BFF;
                color: white;
            }

            tr:nth-child(even) {
                background-color: #f2f2f2;
            }

            td[contenteditable="true"] {
                background-color: #fffdd0;
                cursor: pointer;
            }

            td[contenteditable="true"]:hover {
                background-color: #fffacd;
            }

            .logo {
                position: absolute;
                top: 20px;
                left: 20px;
                width: 150px; /* Adjust size as needed */
            }

            .search-bar {
                display: block;
                width: 300px;
                padding: 10px;
                margin: 20px auto;
                background-color: #fff;
                border: 2px solid #007BFF;
                border-radius: 5px;
                font-size: 16px;
                transition: border-color 0.3s ease, box-shadow 0.3s ease;
            }

            .search-bar:focus {
                border-color: #005bb3;
                box-shadow: 0 0 8px rgba(0, 91, 187, 0.5);
                outline: none;
            }

            .dropdown {
                display: block;
                width: 300px;
                padding: 10px;
                margin: 20px auto;
                background-color: #fff;
                border: 2px solid #007BFF;
                border-radius: 5px;
                font-size: 16px;
                transition: border-color 0.3s ease, box-shadow 0.3s ease;
            }
        </style>
    </head>
    <body>
        <img src="https://logowik.com/content/uploads/images/adani-renewables-green-energy1681.logowik.com.webp" alt="Company Logo" class="logo">
        <h1>PV Form</h1>

        <select class="dropdown" id="plantDropdown" onchange="selectPlant()">
            {% for plant in plants %}
            <option value="{{ plant }}">{{ plant }}</option>
            {% endfor %}
        </select>

        <div id="tabs"></div>
        <input type="text" placeholder="Search.." class="search-bar">
        <div id="data"></div>
        <button onclick="saveData()">Save Data</button>

        <script>
        let currentBlock = '';
        let currentPlant = '';

        function createTabs(blocks) {
            const tabsContainer = document.getElementById('tabs');
            tabsContainer.innerHTML = '';
            blocks.forEach(block => {
                const button = document.createElement('button');
                button.className = 'tab';
                button.innerText = block;
                button.onclick = () => loadData(block);
                tabsContainer.appendChild(button);
            });
        }

        function selectPlant() {
            const dropdown = document.getElementById('plantDropdown');
            currentPlant = dropdown.value;
            fetch(`/load_data?plant=${currentPlant}`)
                .then(response => response.json())
                .then(blocks => createTabs(blocks));
        }

        function loadData(block) {
            currentBlock = block;
            fetch(`/load_data?plant=${currentPlant}&block=${block}`)
                .then(response => response.json())
                .then(data => {
                    let table = '<table><tr>';
                    for (let key in data[0]) {
                        table += `<th>${key}</th>`;
                    }
                    table += '</tr>';
                    data.forEach(row => {
                        table += '<tr>';
                        for (let key in row) {
                            table += `<td contenteditable="true">${row[key]}</td>`;
                        }
                        table += '</tr>';
                    });
                    table += '</table>';
                    document.getElementById('data').innerHTML = table;
                });
        }

        function saveData() {
            let data = [];
            
            let table = document.querySelector('table');
            let headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
            let rows = table.querySelectorAll('tr');
            for (let i = 1; i < rows.length; i++) {
                let row = {};
                let cells = rows[i].querySelectorAll('td');
                headers.forEach((header, index) => {
                    row[header] = cells[index].textContent;
                });
                data.push(row);
            }
            fetch(`/save_data?block=${currentBlock}&plant=${currentPlant}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(result => alert(result.message));
        }
        </script>
    </body>
    </html>
    """, plants=plants)

@app.route('/save_data', methods=['POST'])
def save_data():
    block = request.args.get('block')
    plant = request.args.get('plant')
    data = request.json
    
    block_df = pd.DataFrame(data)
    selectQuery = f"SELECT * FROM {project_id}.winddata.{Tablename}"
    df = client.query(selectQuery).to_dataframe()
    
    df = df[df['Block'] != block].append(block_df, ignore_index=True)
    
    csv_file_path = f"D:\\OneDrive - Adani\\Documents\\{plant}.csv"
    df.to_csv(csv_file_path, index=False)
    
    table_id = f"{project_id}.winddata.{Tablename}"
    table = bigquery.Table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = "WRITE_TRUNCATE"
    df = df.astype(str)
    job = client.load_table_from_dataframe(df, table, job_config=job_config)
    job.result()
    
    return jsonify({"message": "Data saved successfully"})

if __name__ == '__main__':
    app.run(port=5000)
