from pathlib import Path

import pandas as pd


OUTPUT_DIR = Path("output")


def export_excel(
    issues: list[dict],
) -> Path:

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    dataframe = pd.DataFrame(
        issues
    )

    output_path = (
        OUTPUT_DIR
        / "chamados_jira.xlsx"
    )

    dataframe.to_excel(
        output_path,
        index=False,
    )

    return output_path