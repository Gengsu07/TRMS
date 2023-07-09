import st_aggrid as st_ag
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder


def aggrid(df_explore):
    gb = GridOptionsBuilder.from_dataframe(df_explore)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_side_bar()
    gb.configure_default_column(
        groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True
    )
    k_sep_formatter = st_ag.JsCode
    (
        """function(params) {return (params.value == null) ? params.value : params.value.toLocaleString(); } """
    )
    gb.configure_columns(["NOMINAL", "sum"], valueFormatter=k_sep_formatter)
    gridOptions = gb.build()

    df_explore_df = AgGrid(
        df_explore,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        reload_data=True,
        editable=True,
        allow_unsafe_jscode=True,
    )
    return df_explore_df
