import math, bcrypt
import time, datetime, calendar
import base64, json
import plotly.express as px
import pandas as pd
from calendar import month_name
import dbAction, passwords, dash
from dash import dcc, Dash, html, Input, Output, State, callback_context, no_update

app = Dash(__name__, update_title=None, suppress_callback_exceptions=True)

# Color scheme used for website, changing a color here will change it everywhere
colors={
    'background': '#192440',
    'text': '#7B8CAA',
    'mtpgreen': '#60C31B',
    'mtpblue': '#085DAD',
    'mtpnavy': '#0C2752',
    'lightgray': '#f8f8f8',
    'transparent': 'rgba(0,0,0,0)'
}

# Dash requires a special image format
def format_img(img):
    b64encoded_img=base64.b64encode(open(f'assets/{img}', 'rb').read())
    return f'data:image/png;base64,{b64encoded_img.decode()}'
    
# Dimensions for logos
logo_sizes={ 
    'square': {'width': '80px', 'height': '80px'},
    'long': {'width': '140px', 'height': '35px'}}

# Customer dictionary (stores customer with their buckets, logo, and logo dimensions)
# Update this if a new customer is added
customers={
    'Morris Technology Partners': { 
        'account': 'mtp',
        'buckets': ['mtpcf', 'mtpcfbackup'],
        'logo': format_img('MTP.png'),
        'logo-dimensions': {'width': '140px', 'height': '50px'}
    },
    'Jersey Staffing Solutions': {
        'account': 'jss',
        'buckets': ['jerseystaffing', 'jerseystaffingbackup'],
        'logo': format_img('jerseystaffing.png'),
        'logo-dimensions': logo_sizes['long']
    },
    'LBU Inc.': {
        'account': 'lbu',
        'buckets': ['lbuinc', 'lbubackup'],
        'logo': format_img('lbu.png'),
        'logo-dimensions': {'width': '75px', 'height': '100px'}
    },
    'Chanel': {
        'account': 'chanel',
        'buckets': ['chanelrubrik0'],
        'logo': format_img('chanel.png'),
        'logo-dimensions': {'width': '90px', 'height': '60px'}
    },
    'Nextiva': {
        'account': 'nextiva',
        'buckets': ['nextiva'],
        'logo': format_img('nextiva.png'),
        'logo-dimensions': logo_sizes['long']
    },
    'Gramon Schools': {
        'account': 'gramon',
        'buckets': ['gramonbackup'],
        'logo': format_img('gramon.png'),
        'logo-dimensions': logo_sizes['square']
    },
    'Town Motors': {
        'account': 'townmotors',
        'buckets': ['townbackup'],
        'logo': format_img('townmotors.png'),
        'logo-dimensions': logo_sizes['square']
    }
}

# Generate dropdown list (company)
dropdown_list=[]
dropdown_list.append({'label': 'All buckets', 'value': 'all'})
for customer in customers:
    dropdown_list.append({'label': customer, 'value': customer})

# Get every database for admin
dfs = []
for item in customers.items():
    for bucket in item[1]['buckets']:
        dfs.append(pd.DataFrame(dbAction.selectDBWithBucket(bucket), columns = ['Date', 'GB', 'Obj', 'Bucket']))
admin_df = pd.concat(dfs)

# Draw the graph
fig=px.line(admin_df, x="Date", y="GB", color='Bucket', markers=True)
fig.update_layout(
    font_color=colors['text'],
    paper_bgcolor='white',
    plot_bgcolor=colors['lightgray'],
    margin=dict(l=20, r=20, t=20, b=20)
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(gridcolor='#a9a9a9')

spinner = html.Div([html.Div(), html.Div(), html.Div(), html.Div()], className='lds-ellipsis')

morelogincontent = html.Div([
    html.Button(
                [html.Img(className='back-button-img', src=format_img('back.png'))], 
                id='back-button', style={'display': 'none'}),
    html.Img(className='login-logo', src=format_img('mtp.png')),
    html.Div(['Sign in'], className='login-title'),
    html.Div([
        dcc.Input(id="input1", type="text", className='login-field'),
        html.Div(['Username'], className='login-indicator'),
    ], className='loginitem'),
    html.Div([
        dcc.Input(id="input2", type="password", className='login-field'),
        html.Div(['Password',], className='login-indicator')
    ], className='loginitem'),
    html.Button('Reset password', id='resetpassword'),
    html.Div(id='incorrect-login', className='login-message'),
    html.Button('Continue', className='loginbutton', id='login')
])

logincontent = html.Div(morelogincontent, id = 'login-page-content', className='login-content')
login = html.Div(logincontent, id='loginpage')

reset_pass = html.Div([
    html.Img(className='login-logo', src=format_img('mtp.png')),
    html.Div([html.Button(
                [html.Img(className='back-button-img', src=format_img('back.png'))], 
                id='back-button'), 
            'Reset password'], 
            className='login-title'),
    html.Div([
        dcc.Input(id="input11", type="text", className='login-field'),
        html.Div(['Username'], className='login-indicator'),
    ], className='loginitem'),
    html.Div([
        dcc.Input(id="input14", type="password", className='login-field'),
        html.Div(['Old Password'], className='login-indicator'),
    ], className='loginitem'),
    html.Div(className='spacer'),
    html.Div('At least 8 characters long', className='pw-requirement', id='pw-length'),
    html.Div('At least one uppercase letter', className='pw-requirement', id='pw-upper'),
    html.Div('At least one number', className='pw-requirement', id='pw-special'),
    html.Div([
        html.Button('Reset password', id='resetpassword', style={'display': 'none'}),
        dcc.Input(id="input12", type="password", className='login-field'),
        html.Div(['New password'], className='login-indicator'),
    ], className='loginitem'),
    html.Div([
        dcc.Input(id="input13", type="password", className='login-field'),
        html.Div(['Confirm password'], className='login-indicator'),
    ], className='loginitem'),
    html.Div(id='incorrect-reset', className='login-message'),
    html.Button('Continue', className='loginbutton', id='resetthepassword'),
    
    # Invisible inputs to make callbacks work
    dcc.Input(id="input1", type="text", className='login-field', style={'display': 'none'}),
    dcc.Input(id="input2", type="text", className='login-field', style={'display': 'none'}),
    html.Button('Continue', className='loginbutton', id='login', style={'display': 'none'}),
    html.Div(id='incorrect-login', className='login-message', style={'display': 'none'}),
], id='resetpass-page-content')

# Layout for webpage (html)
success = html.Div(id='layout',
    children=[html.Div(className='grid-container',
        children=[
            # Customer Navbar
            html.Div(className='navbar',
            children=[
                html.Div([html.Img(className='mtp-logo', src=format_img('MTP.png'))], 
                className = 'mtp-logo-container'),
                dcc.RadioItems([
                    {"value": "default", "label": html.Div('Default', className='theme-btn default')},
                    {"value": "light", "label": html.Div('Light', className='theme-btn light')},
                    {"value": "dark", "label": html.Div('Dark', className='theme-btn dark')},
                ], value='default', id='theme-buttons', inline=True),
                html.Div('Search by Company', className='customer-dropdown-title'),
                dcc.Dropdown(
                    options=dropdown_list,
                    className='customer-dropdown',
                    id='customer-dropdown',
                    value='all',
                    clearable=False,
                    searchable=True,
                    placeholder=''),
                html.Div(dcc.RadioItems([], id='bucket-buttons'), className='bucket-buttons-container'),
            ]),

            # Main information (all to right of navbar)
            html.Div(className='content',
                children=[
                    html.Div([
                        'Dashboard',
                        html.Button([ 
                            html.Img(src=format_img('logout.png')),
                            html.Span('Logout')
                        ], id='logout'),
                    ], className = 'header'),

                    # Main statistics (All below)
                    html.Div(className='stats',
                        children=[
                        html.Div(className='graph-container',
                            children=[
                                dcc.Tabs(id="datatype-tabs", value='GB', children=[
                                    dcc.Tab(label='Gigabytes', className='datatype-tab', selected_className='datatype-tab--selected', value='GB'),
                                    dcc.Tab(label='Objects', className='datatype-tab', selected_className='datatype-tab--selected', value='Obj'),
                                ]),

                                html.Span([
                                    html.Div(className='graph-buttons',
                                        children=[
                                            dcc.RadioItems([
                                                # GB Button
                                                {
                                                    "value": "Week",
                                                    "label": html.Div(['Week'], className='date-range-button', id='gb_btn')
                                                },
                                                # TO Button
                                                {
                                                    "value": "Month",
                                                    "label": html.Div(['Month'], className='date-range-button', id='to_btn')
                                                },                                        
                                            ], value='Week', id='graph_datatype', inline=True),
                                        ]
                                    ),
                                    dcc.Dropdown(
                                        options=[],
                                        value="Last 7 days",
                                        clearable=False,
                                        searchable=False,
                                        placeholder='',  
                                        className='timedropdown',
                                        id='timedropdown'
                                    ),
                                    html.Span(className='graph-buttons right',
                                    children=[
                                        dcc.RadioItems([
                                            # GB Button
                                            {
                                                "value": "line",
                                                "label": html.Img(
                                                            id='line-btn',
                                                            className='graph-type-btn',
                                                            src=format_img('line.png')),
                                            },
                                            # TO Button
                                            {
                                                "value": "bar",
                                                "label": html.Img(id='bar-btn',
                                                            className='graph-type-btn',
                                                            src=format_img('bar.png')),
                                            },                                        
                                        ], value='line', id='graph_type', className='graphtype', inline=True),
                                    ]),

                                ], className='graph-selection'),
                                # Additional information for bucket (BI, BO, Costs/Savings)
                                # TODO: Divs for numbers

                                # Line graph
                                dcc.Graph(id='graph', config={"displayModeBar": False}),
                                html.Div('', id='jstestbox'),  
                            ]
                        ),

                        # Begin graphs
                        html.Div([
                            html.Img(
                                id='customer-logo',
                                src=format_img('default.png'),
                                style={'width': '75px', 'height': '50px'}
                            ),
                            html.Div(id='customer-name'),
                            html.Div([
                                html.Img(
                                    className='bucket-img',
                                    src=format_img('bucket.png'),
                                ),
                                html.Div(id='customer-bucket')
                            ], className='bucket-line'),
                            
                            html.Div(['Bucket size:'], className='bucket-stats-label', 
                                style={'color': colors['mtpgreen']}
                            ),
                            html.Div([
                                html.Span('0', id='gigabytes'), 
                                html.Span(' GBs')
                            ], className='gigabytes-container'),

                            html.Div([
                                html.Div([ # Total Objects
                                    html.Img(
                                        src=format_img('object.png'), 
                                        className='icon-indicator',
                                        style={'width': '25px', 'height': '25px'}
                                    ),
                                    html.Div('Current objects', className='bucket-stats-label'),
                                    html.Div([
                                        html.Span(['0'], 
                                            className = 'bucket-stats-value suffix', 
                                            id='objects'),
                                    ], className='bucket-stats-element') 
                                ], className='bucket-stats-container'),
                                html.Div([
                                    html.Img(
                                        src=format_img('dollarsign.png'), 
                                        className='icon-indicator',
                                        style={'width': '15px', 'height': '25px'}
                                    ),
                                    html.Div(['Current price'], className='bucket-stats-label'),
                                    html.Div([
                                        html.Span(['$'], className='bucket-stats-unit'),
                                        html.Span(['0'], 
                                            className = 'bucket-stats-value prefix', 
                                            id='cost',
                                            style={'padding-bottom': '0px'}),
                                    ], className='bucket-stats-element')
                                ], className='bucket-stats-container'),
                                html.Div([
                                    html.Img(
                                        src=format_img('bytesout.png'), 
                                        className='icon-indicator',
                                        style={
                                        'width': '15px',
                                        'height': '25px'}
                                    ),
                                    html.Div(['Bytes in (Last 30 days)'], className='bucket-stats-label'),
                                    html.Div([
                                        html.Span(['0'], 
                                            className = 'bucket-stats-value suffix', 
                                            id='bytesin'),
                                        html.Span(['GBs'], className='bucket-stats-unit')
                                    ], className='bucket-stats-element') 
                                ], className='bucket-stats-container'),
                                html.Div([
                                    html.Img(
                                        src=format_img('bytesin.png'), 
                                        className='icon-indicator',
                                        style={
                                        'width': '15px',
                                        'height': '25px'}
                                    ),
                                    html.Div(['Bytes out (Last 30 days)'], className='bucket-stats-label'),
                                        html.Div([
                                        html.Span(['0'], 
                                            className = 'bucket-stats-value suffix', 
                                            id='bytesout'),
                                        html.Span(['GBs'], className='bucket-stats-unit')
                                    ], className='bucket-stats-element') 
                                ], className='bucket-stats-container'),
                            ], className='bucket-stats-grid')
                        ], className='bucket-info'),
                    ])
                ]
            ),
        ]
    ),
])

app.layout = login

# I/O for onClick() (dash callback somewhat emulates js)
@app.callback(
    Output('customer-name', 'children'),
    Output('customer-logo', 'src'),
    Output('customer-logo', 'style'),
    Output('customer-bucket', 'children'),
    Output('gigabytes', 'children'),
    Output('objects', 'children'),
    Output('timedropdown', 'options'),
    Output('timedropdown', 'value'),
    Output('bytesin', 'children'),
    Output('bytesout', 'children'),
    Input('bucket-buttons', 'value'),
    Input('graph_datatype', 'value'),
    prevent_initial_call=True)
def onClick(value, time):
    df=pd.DataFrame(dbAction.selectDB(value), columns = ['Date', 'GB', 'Obj'])

    temp = []
    week_list, month_years = [], []
    itervalue = math.trunc((len(df.index) / 7) + 1)
    timerange = ''
    if time == 'Week': #If week is selected  
        first_date = datetime.datetime.strptime(df['Date'][0], "%m-%d-%Y").date()
        today = datetime.date.today()
        days_between = (today - first_date).days
        start = math.trunc(days_between/7)
        for day in range(start):
            base = day * 7
            starting = first_date + datetime.timedelta(days=base)
            weekrange = [starting, starting + datetime.timedelta(days=6)]
            fweekrange = [date.strftime("%m/%d/%Y") for date in weekrange]
            week_list.insert(0, {'label': f'{fweekrange[0]} - {fweekrange[1]}', 'value': f"{fweekrange[0]}:{fweekrange[1]}"})
        week_list.insert(0, {'label': 'Last 7 days', 'value': 'Last 7 days'})
        timerange = 'Last 7 days'

    else: #If month is selected
        for row in df.index:
            month_number = int(df['Date'][row][:2].replace('0', ''))
            year = df['Date'][row][6:11]
            month_year = f'{month_name[month_number]} {year}'
            if month_year not in month_years:
                week_list.insert(0, {'label': month_year, 'value': month_year})
                month_years.append(month_year)      
        week_list.insert(0, {'label': 'Last 30 days', 'value': 'Last 30 days'})
        timerange = 'Last 30 days'

    # Get customer name from bucket name in dict
    for item in customers.items():
        for bucket in item[1]['buckets']:
            if (value == bucket):
                customer_name=item[0]    
    
    # Get the logo and logo dimensions
    logo=customers[customer_name]['logo']
    logo_dimensions=customers[customer_name]['logo-dimensions']

    # Most recent row
    recent_stats = df.iloc[-1]
    
    current_gb = recent_stats['GB']
    current_obj = "{:,}".format(recent_stats['Obj'])

    today = datetime.date.today()
    thirty_day_range = [today, today - datetime.timedelta(days=30)]
    fthirty_day_range = [date.strftime('%Y%m%d') for date in thirty_day_range]
    try:
        bytesin = json.loads(passwords.bucketTraffic(value, fthirty_day_range[1], fthirty_day_range[0])['BI'])[0]['value']
        bytesout = json.loads(passwords.bucketTraffic(value, fthirty_day_range[1], fthirty_day_range[0])['BO'])[0]['value']
        gigabytesin = "{:,}".format(round(int(bytesin)/(10 ** 9), 2))
        gigabytesout = "{:,}".format(round(int(bytesout)/(10 ** 9), 2))
    except:
        gigabytesin = 'N/A'
        gigabytesout = 'N/A'
    
    return customer_name, logo, logo_dimensions, value, current_gb, current_obj, week_list, timerange, gigabytesin, gigabytesout

@app.callback(
    Output('graph', 'figure'),
    Input('customer-bucket', 'children'),
    Input('graph', 'figure'),
    Input('datatype-tabs', 'value'),
    Input('graph_type', 'value'),
    Input('timedropdown', 'value'),
    Input('bucket-buttons', 'value'),
    prevent_initial_call=True)
def onemoreclick(bucket_name, graph_figure, graph_datatype, graph_type, time_value, value):
    df=pd.DataFrame(dbAction.selectDB(bucket_name), columns = ['Date', 'GB', 'Obj'])
    fdf = pd.DataFrame(columns = ['Date', 'GB', 'Obj'])

    today = datetime.date.today()
    if time_value[0].isdigit() == False:
        if 'Last' in time_value:
            days = time_value.split()[1]
            date_list = [(today - datetime.timedelta(days=x)).strftime("%m-%d-%Y") for x in range(int(days) -1, -1, -1)]
            for date in date_list:
                fdf = pd.concat([fdf, df.loc[df['Date'] == date]])
        else:
            monthyear = time_value.split()
            monthyear[0] = (datetime.datetime.strptime(monthyear[0], "%B")).month
            num_days = calendar.monthrange(int(monthyear[1]), int(monthyear[0]))[1]
            days = [(datetime.date(int(monthyear[1]), int(monthyear[0]), day)).strftime("%m-%d-%Y") for day in range(1, num_days+1)]
            for day in days:
                fdf = pd.concat([fdf, df.loc[df['Date'] == day]])
    else:
        startdate = [time_value.split(':')[0], time_value.split(':')[1]]
        ranges = [datetime.datetime.strptime(x.replace('/', ''), "%m%d%Y").date() for x in startdate]
        delta = ranges[1] - ranges[0]
        for i in range(delta.days + 1):
            day = ranges[0] + datetime.timedelta(days=i)
            fday = day.strftime("%m-%d-%Y")
            fdf = pd.concat([fdf, df.loc[df['Date'] == fday]])

    if graph_type == 'line':
        # Line graph
        line=px.line(fdf, 
            x="Date", 
            y=graph_datatype, 
            markers=True)
        line.update_layout(
            hoverlabel=dict(
                bgcolor='white',
                font_color='black',
                bordercolor='#a8a9a8',
            ),
            font_color=colors['text'],
            paper_bgcolor='rgb(0,0,0,0)',
            plot_bgcolor='rgb(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            xaxis_title='',
            yaxis_title='',)
        line.update_xaxes(showgrid=False, fixedrange=True)
        line.update_yaxes(ticksuffix="", gridcolor='#a9a9a9', fixedrange=True)
        line.update_traces(line_color=colors['mtpgreen'])
        return line
        
    else:
        # Define ranges to prevent long bars and text cutoff for bar graph
        bar_range=fdf[graph_datatype].tolist()
        min_range=min(bar_range) - min(bar_range)/50
        max_range=max(bar_range)*1.01

        # Horizontal bar graph
        bar=px.bar(fdf, 
            x=graph_datatype, 
            y='Date', 
            orientation='h',
            text_auto=True,   
            barmode='group')
        bar.update_layout(
            xaxis=dict(range=[min_range, max_range]),
            font_color=colors['text'],
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgb(0,0,0,0)',
            plot_bgcolor='rgb(0,0,0,0)',
            xaxis_title='',
            yaxis_title='')
        bar.update_xaxes(showgrid=False, zeroline=False,)
        bar.update_yaxes(ticksuffix=" ")
        bar.update_traces(textposition="outside", cliponaxis=False, marker_color=colors['mtpgreen'])
        return bar
     
@app.callback(
    Output('bucket-buttons', 'value'),
    Output('bucket-buttons', 'options'),
    Input('customer-dropdown', 'value'),
    prevent_initial_call=True,
)
def dropdown(value):
    customer_buckets = []
    
    if value == 'all':
        for item in customers.items():
            for bucket in item[1]['buckets']:
                customer_buckets.append(
                    {"value": bucket, "label": html.Div(bucket, className='bucket-btn')})
        return customer_buckets[0]['value'], customer_buckets

    for item in customers.items():
        for bucket in item[1]['buckets']:
            if bucket in customers[value]['buckets']:
                customer_buckets.append(
                    {"value": bucket, "label": html.Div(bucket, className='bucket-btn')})

    return customer_buckets[0]['value'], customer_buckets

# Switch user chain
@app.callback(
    Output('loginpage', 'children'),
    Output('incorrect-login', 'children'),
    Output('input1', 'value'),
    Input('login', 'children'),
    State('input1', 'value'),
    State('input2', 'value'),
    prevent_initial_call=True)
def updatelayout(loginchildren, i1, i2):
    if i1 == None and i2 == None:
        raise dash.exceptions.PreventUpdate
    if i1 == None or i2 == None:
        time.sleep(0.5)
        return login, 'A field is missing, try again', i1 
    if passwords.validate_login(i1, i2):
        if (i1 == 'mtpadmin'):
            dropdown_list.clear()
            dropdown_list.append({'label': 'All buckets', 'value': 'all'})
            for customer in customers:
                dropdown_list.append({'label': customer, 'value': customer})
            return success, no_update, no_update
        else:
            dropdown_list.clear()
            for key, value in customers.items():
                if i1.lower() == value['account']:
                    dropdown_list.append({'label': key, 'value': key})
                    return success, no_update, no_update
    else:
        return login, 'Incorrect login, try again', i1
    
@app.callback(
    Output('login-page-content', 'children'),
    Input('resetpassword', 'n_clicks'),
    Input('back-button', 'n_clicks'),
    Input('input1', 'n_submit'),
    Input('input2', 'n_submit'),
    Input('login', 'n_clicks'),
    State('input2', 'value'),
    prevent_initial_call=True)
def reset(reset, back, i1, i2, login, i2value):
    clicked=[p['prop_id'] for p in callback_context.triggered][0]
    if clicked == '.': 
        raise dash.exceptions.PreventUpdate
    if 'back-button' in clicked:
        return morelogincontent
    if 'n_submit' in clicked or 'login' in clicked:
        if i2value == 'Welcome.2022':
            return reset_pass
        else:
            return no_update
    return reset_pass

@app.callback(
    Output('login', 'children'),
    Input('input1', 'n_submit'),
    Input('input2', 'n_submit'),
    Input('login', 'n_clicks'),
    prevent_initial_call=True)
def logout(j, m, n):
    clicked=[p['prop_id'] for p in callback_context.triggered][0]
    print(clicked)
    return spinner

@app.callback(
    Output('customer-dropdown', 'value'),
    Input('loginpage', 'children'))
def update_dropdown_value(n):
    return dropdown_list[0]['value']

@app.callback(
    Output('layout', 'children'),
    Input('logout', 'n_clicks'),
    prevent_initial_call=True)
def logout(logout):
    return login

@app.callback(
    Output('incorrect-reset', 'children'),
    Input('resetthepassword', 'n_clicks'),
    Input('input13', 'n_submit'),
    State('input11', 'value'),
    State('input12', 'value'),
    State('input13', 'value'),
    State('input14', 'value'),
    prevent_initial_call=True)
def yer(reset, button, i11, i12, i13, i14):
    if passwords.validate_login(i11, i14):
        print('Starting')
        dbAction.change_pw(i11, i13)
        print('Finished')
        return 'Your password has been successfully reset'
    else:
        return 'Check your credentials and try again'

@app.callback(
    Output('pw-length', 'style'),
    Output('pw-upper', 'style'),
    Output('pw-special', 'style'),
    Output('resetthepassword', 'className'),
    Input('input12', 'value'),
    Input('input13', 'value'),
)
def twelve(i12, i13):
    requirements = [0, 0, 0]
    styles = {
        'length': {'color': 'grey'}, 
        'upper': {'color': 'grey'}, 
        'special': {'color': 'grey'},
        'reset-button': 'loginbutton-disabled'}
    if (i12 == '' or i12 == None):
        return styles['length'], styles['upper'], styles['special'], styles['reset-button']
    if len(i12) >= 8:
        requirements[0] = 1
        styles['length'] = {'color': '#60C31B'}
    else:
        styles['length'] = {'color': 'grey'}
    for letter in i12:
        if letter.isdigit():
            requirements[1] = 1
            styles['special'] = {'color': '#60C31B'}
        if letter.isupper():
            requirements[2] = 1
            styles['upper'] = {'color': '#60C31B'}
    if requirements == [1, 1, 1] and i12 == i13:
        styles['reset-button'] = 'loginbutton'
    return styles['length'], styles['upper'], styles['special'], styles['reset-button']

app.clientside_callback(
    """
    function(value) {
        const stylesheet = document.styleSheets[8];

        for(let i = 0; i < stylesheet.cssRules.length; i++) {
            if(stylesheet.cssRules[i].selectorText === '.header') {
                header = stylesheet.cssRules[i];
            }
            
            if(stylesheet.cssRules[i].selectorText === 'input:checked + .date-range-button') {
                checkedInput = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.navbar') {
                navbar = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '#logout') {
                logout = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '#logout > img') {
                logoutimg = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '#logout:hover > img, #logout:hover > span') {
                logouthover = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.graph-buttons') {
                statsButtons = stylesheet.cssRules[i];
            }
            if(stylesheet.cssRules[i].selectorText === '.timedropdown > .Select-control') {
                dropdownControl = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '#customer-name') {
                customername = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-info') {
                customertwo = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-stats-container') {
                customerthree = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-stats-container img') {
                statsIcon = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '#timedropdown > .is-focused:not(.is-open) > .Select-control') {
                openInput = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.date-range-button') {
                graphType = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '#theme-buttons') {
                theme = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.content') {
                grid = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.has-value.Select--single > .Select-control .Select-value .Select-value-label, .has-value.is-pseudo-focused.Select--single > .Select-control .Select-value .Select-value-label') {
                dropdownText = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.VirtualizedSelectFocusedOption') {
                dropdownFocusOption = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.VirtualizedSelectOption') {
                dropdownOption = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.VirtualizedSelectOption:hover') {
                dropdownHoverOption = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.VirtualizedSelectSelectedOption') {
                dropdownSelectedOption = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.Select-menu-outer') {
                outerMenu = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-btn:hover') {
                navButtonHover = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-btn') {
                navButton = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === 'input:checked + .bucket-btn') {
                undaCheck = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.date-range-button:hover') {
                graphTypeHover = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.gigabytes-container') {
                gigabytes = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === 'input:checked + .graph-type-btn') {
                graphtypebtn = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-line') {
                bucket = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.bucket-line > img') {
                bucketimg = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.tab.jsx-3468109796') {
                tabbottom = stylesheet.cssRules[i];
            }

            if(stylesheet.cssRules[i].selectorText === '.tab.jsx-3468109796:last-of-type') {
                tabbottomlast = stylesheet.cssRules[i];
            }
        }

        if (value === 'light') {
            grid.style.setProperty('background-color', '#fff');
            outerMenu.style.setProperty('background-color', '#fff');
            undaCheck.style.setProperty('background-color', '#0C2752');
            checkedInput.style.setProperty('background-color', '#0C2752');
            navbar.style.setProperty('background-color', '#fff');
            dropdownControl.style.setProperty('background-color', '#fff');
            customertwo.style.setProperty('background-color', '#fff');
            statsButtons.style.setProperty('background-color', '#fff');
            graphType.style.setProperty('background-color', '#fff');
            customerthree.style.setProperty('background-color', '#fff');
            bucket.style.setProperty('background-color', '#fff');
            theme.style.setProperty('background-color', '#fff');
            dropdownSelectedOption.style.setProperty('background-color', '#fff');
            
            checkedInput.style.setProperty('font-weight', '900');
            dropdownText.style.setProperty('color', '#0C2752');
            customerthree.style.setProperty('color', '#000000');
            bucket.style.setProperty('color', '#555555');
            navButtonHover.style.setProperty('color', '#0C2752');
            graphTypeHover.style.setProperty('color', '#000000');
            header.style.setProperty('color', '#000000');
            logout.style.setProperty('color', '#000000');
            gigabytes.style.setProperty('color', '#000000');
            customername.style.setProperty('color', '#000000');
            navButton.style.setProperty('color', '#707070');
            dropdownFocusOption.style.setProperty('color', '#000000');
            dropdownOption.style.setProperty('color', '#707070');
            dropdownHoverOption.style.setProperty('color', '#000000');
            dropdownSelectedOption.style.setProperty('color', '#000000');
            
            statsButtons.style.setProperty('border', '1px solid grey');
            navbar.style.setProperty('border-right', '1px solid grey');
            dropdownControl.style.setProperty('border', '1px solid grey');
            customertwo.style.setProperty('border', '1px solid grey');
            customerthree.style.setProperty('border', '1px solid grey');
            openInput.style.setProperty('border', '1px solid grey');
            theme.style.setProperty('border', '1px solid grey');
            outerMenu.style.setProperty('border', '1px solid grey');
            bucket.style.setProperty('border', '1px solid grey');
            tabbottom.style.setProperty('border-bottom', '1px solid #d6d6d6');
            tabbottomlast.style.setProperty('border-bottom', '1px solid #d6d6d6');

            statsIcon.style.setProperty('filter', 'none');
            graphtypebtn.style.setProperty('filter', 'brightness(0) saturate(100%) invert(14%) sepia(12%) saturate(7331%) hue-rotate(194deg) brightness(93%) contrast(100%)');
            logoutimg.style.setProperty('filter', 'invert(0%) sepia(55%) saturate(1983%) hue-rotate(8deg) brightness(102%) contrast(109%)');
            bucketimg.style.setProperty('filter', 'none');
        }

        if (value === 'default') {
            grid.style.setProperty('background-color', '#fff');
            outerMenu.style.setProperty('background-color', '#fff');
            undaCheck.style.setProperty('background-color', '#0C2752');
            checkedInput.style.setProperty('background-color', '#0C2752');
            navbar.style.setProperty('background-color', '#f3f9ff');
            dropdownControl.style.setProperty('background-color', '#f3f9ff');
            customertwo.style.setProperty('background-color', '#f3f9ff');
            statsButtons.style.setProperty('background-color', '#f3f9ff');
            graphType.style.setProperty('background-color', '#f3f9ff');
            customerthree.style.setProperty('background-color', '#fff');
            bucket.style.setProperty('background-color', '#DDDDDD');
            theme.style.setProperty('background-color', '#fff');
            dropdownSelectedOption.style.setProperty('background-color', '#EEEEEE');
            
            checkedInput.style.setProperty('font-weight', '900');
            dropdownText.style.setProperty('color', '#0C2752');
            customerthree.style.setProperty('color', '#000000');
            bucket.style.setProperty('color', '#555555');
            navButtonHover.style.setProperty('color', '#0C2752');
            graphTypeHover.style.setProperty('color', '#000000');
            header.style.setProperty('color', '#000000');
            logout.style.setProperty('color', '#000000');
            gigabytes.style.setProperty('color', '#000000');
            customername.style.setProperty('color', '#000000');
            navButton.style.setProperty('color', '#707070');
            dropdownFocusOption.style.setProperty('color', '#000000');
            dropdownOption.style.setProperty('color', '#707070');
            dropdownHoverOption.style.setProperty('color', '#000000');
            dropdownSelectedOption.style.setProperty('color', '#000000');
            
            statsButtons.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            navbar.style.setProperty('border-right', '1px solid rgba(0,0,0,0)');
            dropdownControl.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            customertwo.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            customerthree.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            openInput.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            theme.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            outerMenu.style.setProperty('border', '1px solid grey');
            bucket.style.setProperty('border', '1px solid rgba(0,0,0,0)');
            tabbottom.style.setProperty('border-bottom', '1px solid #d6d6d6');
            tabbottomlast.style.setProperty('border-bottom', '1px solid #d6d6d6');

            statsIcon.style.setProperty('filter', 'none');
            graphtypebtn.style.setProperty('filter', 'brightness(0) saturate(100%) invert(14%) sepia(12%) saturate(7331%) hue-rotate(194deg) brightness(93%) contrast(100%)');
            logoutimg.style.setProperty('filter', 'invert(0%) sepia(55%) saturate(1983%) hue-rotate(8deg) brightness(102%) contrast(109%)');
            bucketimg.style.setProperty('filter', 'none');
        }

        if (value === 'dark') {
            grid.style.setProperty('background-color', '#202025');
            outerMenu.style.setProperty('background-color', '#202025');
            undaCheck.style.setProperty('background-color', '#095cad');
            checkedInput.style.setProperty('background-color', '#095cad');
            navbar.style.setProperty('background-color', '#35363a');
            dropdownControl.style.setProperty('background-color', '#35363a');
            customertwo.style.setProperty('background-color', '#35363a');
            statsButtons.style.setProperty('background-color', '#35363a');
            graphType.style.setProperty('background-color', '#35363a');
            customerthree.style.setProperty('background-color', '#35363a');
            bucket.style.setProperty('background-color', '#35363a');
            theme.style.setProperty('background-color', '#35363a');
            dropdownSelectedOption.style.setProperty('background-color', '#35363a');
            
            checkedInput.style.setProperty('font-weight', '900');
            dropdownText.style.setProperty('color', '#fff');
            customerthree.style.setProperty('color', '#fff');
            bucket.style.setProperty('color', '#fff');
            navButtonHover.style.setProperty('color', '#fff');
            graphTypeHover.style.setProperty('color', '#fff');
            header.style.setProperty('color', '#fff');
            logout.style.setProperty('color', '#fff');
            gigabytes.style.setProperty('color', '#fff');
            customername.style.setProperty('color', '#fff');
            navButton.style.setProperty('color', '#83878d');
            dropdownFocusOption.style.setProperty('color', '#fff');
            dropdownOption.style.setProperty('color', '#83878d');
            dropdownHoverOption.style.setProperty('color', '#fff');
            dropdownSelectedOption.style.setProperty('color', '#fff');

            statsButtons.style.setProperty('border', '1px solid #606164');
            navbar.style.setProperty('border-right', '1px solid #606164');
            dropdownControl.style.setProperty('border', '1px solid #606164');
            customertwo.style.setProperty('border', '1px solid #606164');
            customerthree.style.setProperty('border', '1px solid #606164');
            openInput.style.setProperty('border', '1px solid #606164');
            theme.style.setProperty('border', '1px solid #606164');
            outerMenu.style.setProperty('border', '1px solid #606164');
            bucket.style.setProperty('border', '1px solid #606164');
            tabbottom.style.setProperty('border-bottom', '1px solid #d6d6d6');
            tabbottomlast.style.setProperty('border-bottom', '1px solid #d6d6d6');

            statsIcon.style.setProperty('filter', 'brightness(0) saturate(100%) invert(100%) sepia(100%) saturate(1%) hue-rotate(173deg) brightness(108%) contrast(101%)');
            graphtypebtn.style.setProperty('filter', 'brightness(0) saturate(100%) invert(18%) sepia(96%) saturate(2647%) hue-rotate(198deg) brightness(95%) contrast(93%)');
            logoutimg.style.setProperty('filter', 'invert(100%) sepia(100%) saturate(1%) hue-rotate(173deg) brightness(108%) contrast(101%)');
            bucketimg.style.setProperty('filter', 'brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(2%) hue-rotate(320deg) brightness(108%) contrast(101%)');
        }
    }
    """,
    Output('jstestbox', 'children'),
    Input('theme-buttons', 'value'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
    
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050", debug=True)
# debug=False,dev_tools_ui=False,dev_tools_props_check=False