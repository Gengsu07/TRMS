import io
import pandas as pd


def to_excel(df) -> bytes:
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="data")
    writer.save()
    processed_df = output.getvalue()
    return processed_df
