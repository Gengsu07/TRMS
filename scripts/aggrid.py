import st_aggrid as st_ag
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder


def aggrid(df_explore):
    try:
        numeric_columns = df_explore.select_dtypes(include=["int", "float"]).columns

        df_explore[[numeric_columns]] = df_explore[[numeric_columns]].round(0)
    except:
        pass
    gb = GridOptionsBuilder.from_dataframe(df_explore)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=30)
    gb.configure_side_bar()
    gb.configure_default_column(
        groupable=True,
        value=True,
        enableRowGroup=True,
        aggFunc="sum",
        resizable=True,
        filterable=True,
        sortable=True,
    )
    # k_sep_formatter = st_ag.JsCode
    # (
    #     """function(params) {return (params.value == null) ? params.value : params.value.toLocaleString(); } """
    # )

    # gb.configure_columns(["NOMINAL", "sum"], valueFormatter=k_sep_formatter)
    gb.configure_column(
        "NOMINAL",
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.NOMINAL.toLocaleString('en-US');",
    )
    gb.configure_columns(
        numeric_columns, valueFormatter="value.toLocaleString()", aggFunc="sum"
    )
    # gb.configure_column(
    #     "sum(NOMINAL)",
    #     type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
    #     valueFormatter="data.NOMINAL.toLocaleString('en-US');",
    # )
    gridOptions = gb.build()

    df_explore_df = AgGrid(
        df_explore,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        # reload_data=True,
        editable=True,
        allow_unsafe_jscode=True,
    )
    return df_explore_df
