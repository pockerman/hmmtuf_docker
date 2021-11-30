"""
Various helpers for plotting with Dash
"""
from typing import List, Tuple
import numpy as np
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash

from db.db_connector import DBConnectorBase
from compute_engine.src.exceptions import InvalidGCLimiter, InvalidGCLimitType, NoDataQuery

# TODO: maybe move these to DB?
gc_limit_type = [(0, "Select"), (1, "AVG"), (2, "MIN"), (3, "MAX")]
gc_limit = [(0, "Select"), (1, "<"), (2, ">"), (3, "<="), (4, ">="), (5, "=")]
gc_limit_map = {0: "Select", 1: "<", 2: ">", 3: "<=", 4: ">=", 5: "="}

# TODO: move these to DB
#uique_seq_types = [(0, 'Select'), (1, 'NORMAL'), (2, 'PURINE'), (3, 'AMINO'), (4, 'WEAK_HYDROGEN')]
#uique_dist_types = [(0, 'Select'), (1, 'Bag'), (2, 'Cosine'),
#                     (3, 'DamerauLevenshtein'), (4, 'Gotoh'), (5, 'Hamming'),
#                     (6, 'Jaccard'), (7, 'JaroWinkler'), (8, 'LCSSeq'),
#                    (9, 'LCSStr'), (10, 'Levenshtein'), (11, 'MLIPNS'),
#                    (12, 'MongeElkan'), (13, 'NeedlemanWunsch'),
#                    (14, 'Overlap'), (15, 'Sorensen'), (16, 'StrCmp95'),
#                    (17, 'SmithWaterman'), (18, 'Tanimoto'), (19, 'Tversky')]


def get_layout(unique_seq_types: List[Tuple], unique_dist_types: List[Tuple]) -> html.Div:

    layout = html.Div([
        html.H1("Distances Plot"),
        html.H3("Sequence type"),
        dcc.Dropdown(
            id="dropdown-sequence",
            options=[{"label": x[1], "value": x[0]} for x in unique_seq_types],
            value=unique_seq_types[0][0],
            clearable=False,
        ),

        html.H3("Distance type"),
        dcc.Dropdown(
            id="dropdown-distance",
            options=[{"label": x[1], "value": x[0]} for x in unique_dist_types],
            value=unique_dist_types[0][0],
            clearable=False,
        ),

        html.H3("GC Limit Variable"),
        dcc.Dropdown(
            id="dropdown-gc-limit-type",
            options=[{"label": x[1], "value": x[0]} for x in gc_limit_type],
            value=gc_limit_type[0][0],
            clearable=False,
        ),

        html.H3("GC Limiter"),
        dcc.Dropdown(
            id="dropdown-gc-limit",
            options=[{"label": x[1], "value": x[0]} for x in gc_limit],
            value=gc_limit[0][0],
            clearable=False,
        ),

        html.H3("GC Value"),
        dcc.Input(
            id="gc-limit-value",
            type="number",
        ),
        html.Br(id="break-id-1"),
        html.Br(id="break-id-2"),
        html.Button(children='Compute', id='compute-btn', n_clicks=0),
        html.Br(id="break-id-3"),
        html.Br(id="break-id-4"),
        html.Div(children=[html.H5("Messages"), html.Div(id="error-messages-id")]),
        html.Br(id="break-id-5"),
        html.Br(id="break-id-6"),
        html.H3("Normal state"),
        html.Div(children=[html.H5("Number of sequences"), html.Div(id="normal-n-distances")]),
        dcc.Graph(id="normal-bar-chart"),
        html.H3("TUF state"),
        html.Div(children=[html.H5("Number of sequences"), html.Div(id="tuf-n-distances")]),
        dcc.Graph(id="tuf-bar-chart"),
        html.H3("Core"),
        html.Div(children=[html.H5("Number of sequences"), html.Div(id="core-n-distances")]),
        dcc.Graph(id="core-bar-chart"),

    ])
    return layout

def create_plot_from_state_type(state_type_id: int, metric_type_id: int,
                                sequence_type_id: int, db_connector: DBConnectorBase) -> tuple:
    """
    Create the plot based on the
    state_type_id, metric_type_id, sequence_type_id
    """

    sql = "SELECT value FROM repeats_distances WHERE hmm_state_id_1 = {0}".format(state_type_id)
    sql += " AND  hmm_state_id_2 = {0}".format(state_type_id)
    sql += " AND metric_type_id={0} AND sequence_type_id={1}".format(metric_type_id,
                                                                     sequence_type_id)

    error_message = ""

    try:
        print("{0} Executing sql={1}".format(INFO, sql))
        rows = db_connector.fetch_all(sql=sql)
        print("{0} Fetched number of rows={1}".format(INFO, len(rows)))
    except Exception as e:
        rows = []
        error_message = str(e)

    if len(rows) == 0 and error_message == "":
        # if not data is returned and
        # the error_message is empty
        # then the query returned not data
        error_message = "Query={0} returned no data".format(sql)

    counts, bins = np.histogram(rows, bins=35)
    bins = 0.5 * (bins[:-1] + bins[1:])

    fig = px.bar(x=bins, y=counts, orientation='v',
                 labels={'x': 'distance', 'y': 'count'}, range_x=[0, 1])
    fig.update_layout(xaxis=dict(
        tickmode='linear',
        tick0=0.0,
        dtick=0.15))

    return error_message, fig, len(rows)


def form_gc_sql(state_type_id: int, gc_limit_type,
                gc_limiter, gc_value: float) -> str:
    """
    Create the sql when GC limit is used
    """

    sql = '''CREATE TEMPORARY TABLE temp_repeats AS SELECT'''
    if gc_limiter == 1:
        if gc_limit_type == 1:
            sql += ''' id FROM repeats where gc < {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_min < {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_max < {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        else:
            raise InvalidGCLimitType(expression=None,
                                     message="Invalid gc_limit_type. gc_limit_type={0} not in [1,3]".format(
                                         gc_limit_type))

    elif gc_limiter == 2:

        if gc_limit_type == 1:
            sql += ''' id FROM repeats where gc > {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_min > {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_max > {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        else:
            raise InvalidGCLimitType(expression=None,
                                     message="Invalid gc_limit_type. gc_limit_type={0} not in [1,3]".format(
                                         gc_limit_type))

    elif gc_limiter == 3:
        if gc_limit_type == 1:
            sql += ''' id FROM repeats where gc <= {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_min <= {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_max <= {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        else:
            raise InvalidGCLimitType(expression=None,
                                     message="Invalid gc_limit_type. gc_limit_type={0} not in [1,3]".format(
                                         gc_limit_type))

    elif gc_limiter == 4:
        if gc_limit_type == 1:
            sql += ''' id FROM repeats where gc >= {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_min >= {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 3:
            sql += ''' id FROM repeats where gc_max >= {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        else:
            raise InvalidGCLimitType(expression=None,
                                     message="Invalid gc_limit_type. gc_limit_type={0} not in [1,3]".format(
                                         gc_limit_type))

    elif gc_limiter == 5:
        if gc_limit_type == 1:
            sql += ''' id FROM repeats where gc = {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 2:
            sql += ''' id FROM repeats where gc_min = {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        elif gc_limit_type == 3:
            sql += ''' id FROM repeats where gc_max = {0} AND repeat_seq != 'NO_REPEATS' '''.format(gc_value)
        else:
            raise InvalidGCLimitType(expression=None,
                                     message="Invalid gc_limit_type. gc_limit_type={0} not in [1,3]".format(
                                         gc_limit_type))
    else:
        raise InvalidGCLimiter(expression=None,
                               message="Invalid gc_limiter. gc_limiter={0} not in [1,5]".format(gc_limiter))

    sql += ''' AND hmm_state_id = {0}'''.format(state_type_id)
    return sql


def create_figure_plot(state_type_id: int, metric_type_id: int,
                       sequence_type_id: int, gc_limit_type: int,
                       gc_limiter: int, gc_value: float, btn_clicks: int,
                       db_connector: DBConnectorBase) -> tuple:

    if btn_clicks == 0:

        # nothing to compute
        rows = []
        error_message = ""

    elif btn_clicks != 0 and sequence_type_id == 0 or metric_type_id == 0:
        # we have nothing to plot
        rows = []
        error_message = "Sequence type or distance type is not set."
    else:

        if gc_limit_type == 0 and gc_limiter == 0 and gc_value is None:

            # we don't want GC limiters
            return create_plot_from_state_type(state_type_id=state_type_id,
                                               metric_type_id=metric_type_id,
                                               sequence_type_id=sequence_type_id,
                                               db_connector=db_connector)
        else:

            ## error handling
            if gc_limit_type != 0 and gc_limiter == 0 or gc_value is None:
                rows = []
                error_message = " GC limit variable specified but"
                error_message += " not the GC limiter direction or the GC value."
            elif gc_limiter != 0 and gc_limit_type == 0 or gc_value is None:
                rows = []
                error_message = " GC limiter specified but"
                error_message += " not the GC limit variable direction or the GC value."
            elif gc_value is not None and gc_limiter == 0 or gc_limit_type == 0:
                rows = []
                error_message = " GC value specified but"
                error_message += " not the GC limit variable or the GC limiter."

            else:

                sql = form_gc_sql(state_type_id=state_type_id,
                                  gc_limit_type=gc_limit_type,
                                  gc_limiter=gc_limiter,
                                  gc_value=gc_value)

                print("{0} Fetching data for GC {1} {2}".format(INFO,
                                                                gc_limit_map[gc_limiter],
                                                                gc_value))
                print("{0} Create temporary table sql={1}".format(INFO, sql))

                try:

                   # local_db = SQLiteDBConnector(db_file=db_file)
                   # local_db.connect()
                    db_connector.create_tmp_table(sql=sql)

                    sql = "SELECT COUNT(*) FROM temp_repeats"
                    rows = local_db.fetch_all(sql=sql)

                    print("{0} Found {1} repeats with GC {2} {3}".format(INFO, rows[0][0],
                                                                         gc_limit_map[gc_limiter],
                                                                         gc_value))

                    if rows[0][0] == 0:
                        error_message = "Query={0} returned no data".format(sql)
                        rows = []
                    else:

                        sql = "SELECT value FROM repeats_distances WHERE"
                        sql += " repeat_idx_1 IN (SELECT * FROM temp_repeats)"
                        sql += " AND repeat_idx_2 IN (SELECT * FROM temp_repeats)"
                        sql += " AND metric_type_id={0}".format(metric_type_id)
                        sql += " AND sequence_type_id={0}".format(sequence_type_id)

                        print("{0} Executing sql={1}".format(INFO, sql))
                        rows = db_connector.fetch_all(sql=sql)
                        print("{0} Fetched number of rows={1}".format(INFO, len(rows)))

                        error_message = ""
                        if len(rows) == 0:
                            error_message = "Query={0} returned no data".format(sql)

                except Exception as e:
                    error_message = str(e)
                    rows = []
                finally:
                    print("{0} Deleting table...".format(INFO))
                    sql = '''DROP TABLE IF EXISTS temp_repeats'''
                    db_connector.execute_sql(sql=sql)

    counts, bins = np.histogram(rows, bins=35)
    bins = 0.5 * (bins[:-1] + bins[1:])

    fig = px.bar(x=bins, y=counts, orientation='v', labels={'x': 'distance', 'y': 'count'}, range_x=[0, 1])
    fig.update_layout(xaxis=dict(
        tickmode='linear',
        tick0=0.0,
        dtick=0.15))

    return error_message, fig, len(rows)