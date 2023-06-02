from flask import Flask, render_template,request
import csv
import io
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Create the Flask application
app = Flask(__name__)

# Define a route and its corresponding function
@app.route('/')
def hello_world():
    return render_template("index.html")

def gen_data(df,key_word,year):
    new_column_names = ['date','value_addon']
    df.rename(columns=dict(zip(df.columns, new_column_names)), inplace=True)
    df['month'] = df['date'].apply(lambda x:x.split('-')[1])
    df['year'] = df['date'].apply(lambda x:x.split('-')[0])
    df['value_addon'] = pd.to_numeric(df['value_addon'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['month'] = pd.to_numeric(df['month'], errors='coerce')
    month_names = {1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul',8: 'Aug',9: 'Sep',10: 'Oct',11: 'Nov',12: 'Dec'}
    df['month_name'] = df['month'].map(month_names)
    df = df[df.year>=year]
    fig = px.line(df, x='month_name', y='value_addon', color='year', labels={'month_name': 'Month', 'value_addon': 'values_addon', 'year': 'Year'})
    fig.update_layout(title= key_word+'--> Yearly values_addon')
    pio.write_html(fig, file='Templates/figure.html')
    res = []
    for i in range(len(df)):
        if i!=0:
            res.append(df.value_addon.iloc[i] - df.value_addon.iloc[i-1])
        else:
             res.append(df.value_addon.iloc[i])
    df['res'] = res
    df[['year','month','res']]
    df_pivot = df.pivot(index='month', columns=['year'], values='res')
    df_pivot.insert(0, 'month_name', df_pivot.index.map(month_names))
    df_pivot['total'] = df_pivot.sum(axis=1)
    df_pivot['average'] = df_pivot.loc[:, df_pivot.columns != 'total'].mean(axis=1).round(decimals=2)
    df_pivot = df_pivot.reset_index(drop=True)
    months_lis = df_pivot[df_pivot.average>0].month_name.tolist()
    # df_pivot.to_csv("pivot.csv",index=False)
    return months_lis, df_pivot


@app.route('/form_data', methods=['POST'])
def process_form():
    year = int(request.form['year'])
    csv_file = request.files['csv_file']
    df = pd.read_csv(csv_file, skiprows=1)
    key_word = df.columns[-1].split(":")[0]
    months_lis, csv_data_pivot = gen_data(df,key_word,year)
    csv_data = []
    column_names = list(csv_data_pivot.columns)
    csv_data.append(column_names)
    for row in csv_data_pivot.itertuples(index=False):
        csv_data.append(list(row))
    return render_template('dis.html', months_lis = months_lis,job_title=key_word, csv_data=csv_data)



    

# Run the application if the script is executed directly
if __name__ == '__main__':
    app.run(port=5002, debug=True)
