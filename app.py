from h2o_wave import ui, Q, app, main, data
import requests


@app('/covid')
async def serve(q: Q):
    if not q.client.initialized:
        initialize(q)
    if q.args.country is not None:
        q.client.selected_country = q.args.country
        get_filters(q)
        show_stats(q)
    if q.args.stat is not None:
        q.client.selected_stat = q.args.stat
        get_filters(q)
        show_stats(q)
    await q.page.save()


def initialize(q: Q):
    q.page['meta'] = ui.meta_card(
        box="",
        layouts=[
            ui.layout(
                breakpoint="xs",
                zones=[
                    ui.zone("header"),
                    ui.zone("navigation"),
                    ui.zone("daily_content", direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone("daily_stat", size='30%', zones=[
                            ui.zone('country_daily_stat'),
                            ui.zone('global_daily_stat'),
                        ]),
                        ui.zone('graph_daily', size='70%'),
                    ]),
                    ui.zone("total_content", direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone("country_stat", size='30%', zones=[
                            ui.zone('country_total_stat'),
                            ui.zone('global_total_stat'),
                        ]),
                        ui.zone('graph_total', size='70%'),
                    ]),
                ]
            )
        ]
    )

    q.client.countries = []

    q.page['header'] = ui.header_card(
        box="header",
        title="Covid-19",
        subtitle="Stats visualizer for Covid-19"
    )

    set_meta(q)
    q.client.stats = [('Confirmed', 'confirmed'), ('Deaths', 'deaths')]
    q.client.selected_country = 'Sri Lanka'
    q.client.selected_stat = 'confirmed'
    get_filters(q)
    show_stats(q)
    display_global_total_stat(q)
    display_global_daily_stat(q)
    q.client.initialized = True


def set_meta(q: Q):
    url = 'https://webhooks.mongodb-stitch.com/api/client/v2.0/app/covid-19-qppza/service/REST-API/incoming_webhook/metadata'
    resp = requests.get(url=url)
    json = resp.json()
    q.client.countries = json['countries']
    q.client.first_date = json['first_date']
    q.client.last_date = json['last_date']

    set_summary_meta(q)


def set_summary_meta(q: Q):
    url = f'https://webhooks.mongodb-stitch.com/api/client/v2.0/app/covid-19-qppza/service/REST-API/incoming_webhook/global_and_us?hide_fields=_id,%20country,%20country_code,%20country_iso2,%20country_iso3,%20loc,%20state,%20uid&min_date={q.client.last_date}&max_date={q.client.last_date}'
    resp = requests.get(url=url)
    json = resp.json()

    global_confirmed_total = 0
    global_deaths_total = 0
    global_recovered_total = 0
    global_confirmed_daily = 0
    global_deaths_daily = 0
    global_recovered_daily = 0

    for i in json:
        global_confirmed_total = global_confirmed_total + (0 if 'confirmed' not in i else i['confirmed'])
        global_deaths_total = global_deaths_total + (0 if 'deaths' not in i else i['deaths'])
        global_recovered_total = global_recovered_total + (0 if 'recovered' not in i else i['recovered'])

        global_confirmed_daily = global_confirmed_daily + (0 if 'confirmed_daily' not in i else i['confirmed_daily'])
        global_deaths_daily = global_deaths_daily + (0 if 'deaths_daily' not in i else i['deaths_daily'])
        global_recovered_daily = global_recovered_daily + (0 if 'recovered_daily' not in i else i['recovered_daily'])

    q.client.global_confirmed_total = global_confirmed_total
    q.client.global_deaths_total = global_deaths_total
    q.client.global_recovered_total = global_recovered_total

    q.client.global_confirmed_daily = global_confirmed_daily
    q.client.global_deaths_daily = global_deaths_daily
    q.client.global_recovered_daily = global_recovered_daily


def show_stats(q: Q):
    url = f'https://webhooks.mongodb-stitch.com/api/client/v2.0/app/covid-19-qppza/service/REST-API/incoming_webhook/global?country={q.client.selected_country}&hide_fields=_id,%20country,%20country_code,%20country_iso2,%20country_iso3,%20loc,%20state,%20uid'
    resp = requests.get(url=url)
    json = resp.json()
    show_country_daily_stat(q, json)
    show_country_total_stat(q, json)
    display_country_total_stat(q, json[-1])
    display_country_daily_stat(q, json[-1])


def show_country_daily_stat(q: Q, data_list):
    q.page['daily_plot'] = ui.plot_card(
        box='graph_daily',
        title='Daily count',
        data=data('date count', len(data_list)),
        plot=ui.plot([ui.mark(type='line', x_scale='time', x='=date', y='=count', y_min=0)])
    )
    q.page['daily_plot'].data = [(data_list[i]['date'], data_list[i][f'{q.client.selected_stat}_daily']) for i in
                                 range(len(data_list))]


def show_country_total_stat(q: Q, data_list):
    q.page['total_plot'] = ui.plot_card(
        box='graph_total',
        title='Total count',
        data=data('date count', len(data_list)),
        plot=ui.plot([ui.mark(type='line', x_scale='time', x='=date', y='=count', y_min=0)])
    )
    q.page['total_plot'].data = [(data_list[i]['date'], data_list[i][q.client.selected_stat]) for i in
                                 range(len(data_list))]


def get_filters(q: Q):
    q.page['filters'] = ui.form_card(
        box="navigation",
        items=[
            ui.text_xl("Covid stats"),
            ui.inline(items=[
                ui.dropdown(
                    name='country',
                    label='Country',
                    choices=[
                        ui.choice(name=country, label=country) for country in q.client.countries
                    ],
                    trigger=True,
                    value=q.client.selected_country
                ),
                ui.dropdown(
                    name='stat',
                    label='Select Stat',
                    choices=[
                        ui.choice(name=selected[1], label=selected[0]) for selected in q.client.stats
                    ],
                    trigger=True,
                    value=q.client.selected_stat
                )
            ])
        ]
    )


def display_global_total_stat(q: Q):
    q.page['global_total_stat'] = ui.stat_list_card(
        box='global_total_stat',
        title=f'Total figures in World',
        items=[
            ui.stat_list_item(
                label='Total confirmed',
                value=str(q.client.global_confirmed_total),
            ),
            ui.stat_list_item(
                label='Total deaths',
                value=str(q.client.global_deaths_total)
            ),
        ]
    )


def display_global_daily_stat(q: Q):
    q.page['global_daily_stat'] = ui.stat_list_card(
        box='global_daily_stat',
        title=f'Daily figures in World',
        items=[
            ui.stat_list_item(
                label='Daily confirmed',
                value=str(q.client.global_confirmed_daily),
            ),
            ui.stat_list_item(
                label='Daily deaths',
                value=str(q.client.global_deaths_daily)
            ),
        ]
    )


def display_country_total_stat(q: Q, last):
    q.page['country_total_stat'] = ui.stat_list_card(
        box='country_total_stat',
        title=f'Total figures in {q.client.selected_country}',
        items=[
            ui.stat_list_item(
                label='Total confirmed',
                value=str(last['confirmed']),
            ),
            ui.stat_list_item(
                label='Total deaths',
                value=str(last['deaths'])
            ),
        ]
    )


def display_country_daily_stat(q: Q, last):
    q.page['country_daily_stat'] = ui.stat_list_card(
        box='country_daily_stat',
        title=f'Daily figures in {q.client.selected_country}',
        items=[
            ui.stat_list_item(
                label='Daily confirmed',
                value=str(last['confirmed_daily']),
            ),
            ui.stat_list_item(
                label='Daily deaths',
                value=str(last['deaths_daily'])
            ),
        ]
    )
