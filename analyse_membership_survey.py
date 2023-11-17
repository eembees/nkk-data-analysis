#!/usr/bin/python
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pytz


DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./output")
MD_DIR = Path("./md-files")

METADATA_COLS = [
    "Submission ID",
    "Created",
    "Last Change",
    "Country",
    "City",
    "User Agent",
    "Device",
]

DATA_TYPES = {
    "00 - Medlemstype (radio)": str,
    "0 - Køn (radio)": str,
    "01 - Rutebyg - højde (slider)": "Int32",
    "03 - Problemerne i NKK passer til min klatrestil.  (slider)": "Int32",
    "04 - Problemerne i NKK passer til mit niveau. (slider)": "Int32",
    "05 - Ruterne, indenfor mit niveau, er varierede og interessante. (slider)": "Int32",
    "06 - Der er nok ruter på mit niveau i klubben. (slider)": "Int32",
    "07 - Hvordan føles densiteten (greb pr. kvm) i klubben? (slider)": "Int32",
    "08 - Jeg kunne godt tænke mig mere af disse typer problemer: (checkbox)": "Int32",
    "Rutebyg - kommentarer (textarea)": str,
    "10 - Stemningen i NKK er inklusiv, og jeg føler mig hjemme i klubben. (slider)": "Int32",
    "10c - NKKs stemning - kommentarer (textfield)": str,
    "11 - Jeg ved, hvordan jeg kan bidrage til NKK som frivillig (slider)": "Int32",
    "12 - Jeg har lyst til, at være frivillig i NKK (slider)": "Int32",
    "13 - Frivillighed - Kommentarer (textarea)": str,
}


def load_and_preprocess_df(p: Path) -> pd.DataFrame:
    df = pd.read_excel(p)
    # remove full null values
    df = df.dropna(subset=df.columns.difference(METADATA_COLS), how="all")

    # merge, somehow, find out later.
    # data types
    for _col, _type in DATA_TYPES.items():
        if _type != str:
            df[_col] = pd.to_numeric(df[_col], errors="coerce").astype(_type)
            #  df[_col] = df[_col].astype(_type)

    df["00 - Medlemstype (radio)"] = df["00 - Medlemstype (radio)"].map(
        {'"2"': "morgen", '"1"': "normal"}
    )

    df["0 - Køn (radio)"] = df["0 - Køn (radio)"].map(
        {'"M"': "Mand", '"K"': "Kvinde", "nan": "X", "O": "Andet Køn"}
    )

    df["02 - Rutebyg - mit niveau (tekst)"] = df[
        "02 - Rutebyg - mit niveau (radio)"
    ].map(
        {
            "1": "Grøn",
            "2": "Gul",
            "3": "Blå",
            "4": "Lilla",
            "5": "Rød",
            "6": "Sort",
            '"1"': "Grøn",
            '"2"': "Gul",
            '"3"': "Blå",
            '"4"': "Lilla",
            '"5"': "Rød",
            '"6"': "Sort",
            1: "Grøn",
            2: "Gul",
            3: "Blå",
            4: "Lilla",
            5: "Rød",
            6: "Sort",
        }
    )

    return df


def extract_comments(df: pd.DataFrame):
    _NKK_METADATA = [
        "00 - Medlemstype (radio)",
        "0 - Køn (radio)",
        "01 - Rutebyg - højde (slider)",
        "02 - Rutebyg - mit niveau (radio)",
        "02 - Rutebyg - mit niveau (tekst)",
    ]
    col_list = _NKK_METADATA + [
        "Rutebyg - kommentarer (textarea)",
        "10c - NKKs stemning - kommentarer (textfield)",
        "13 - Frivillighed - Kommentarer (textarea)",
    ]
    df_comments = df[col_list]
    df_comments = df_comments.dropna(
        subset=df_comments.columns.difference(_NKK_METADATA), how="all"
    )

    return df_comments


def format_to_markdown_rutebyg(row):
    return (
        f"> {row['Rutebyg - kommentarer (textarea)']}.\n\n-- <cite>{row['00 - Medlemstype (radio)']}medlem, {row['0 - Køn (radio)']} {row['01 - Rutebyg - højde (slider)']}cm, klatrer {row['02 - Rutebyg - mit niveau (tekst)']}</cite>"
        if str(row["Rutebyg - kommentarer (textarea)"]) != "nan"
        else None
    )


def format_to_markdown_vibe(row):
    return (
        f"> {row['10c - NKKs stemning - kommentarer (textfield)']}.\n\n-- <cite>{row['00 - Medlemstype (radio)']}medlem, {row['0 - Køn (radio)']} {row['01 - Rutebyg - højde (slider)']}cm, klatrer {row['02 - Rutebyg - mit niveau (tekst)']}</cite>"
        if str(row["10c - NKKs stemning - kommentarer (textfield)"]) != "nan"
        else None
    )


def format_to_markdown_volunteer(row):
    return (
        f"> {row['13 - Frivillighed - Kommentarer (textarea)']}.\n\n-- <cite>{row['00 - Medlemstype (radio)']}medlem, {row['0 - Køn (radio)']} {row['01 - Rutebyg - højde (slider)']}cm, klatrer {row['02 - Rutebyg - mit niveau (tekst)']}</cite>"
        if str(row["13 - Frivillighed - Kommentarer (textarea)"]) != "nan"
        else None
    )


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    MD_DIR.mkdir(exist_ok=True)

    file_list = list(DATA_DIR.glob("submission*.xlsx"))
    submissions_file = file_list[0]

    print(submissions_file)

    df = load_and_preprocess_df(submissions_file)
    df_c = extract_comments(df)
    df_c.sort_values(by="02 - Rutebyg - mit niveau (radio)", inplace=True)

    # Save rutebyg feedback to markdown
    md_text_rutebyg = "\n\n".join(
        filter(
            None,
            (format_to_markdown_rutebyg(row) for _, row in df_c.iterrows()),
        )
    )
    with open(MD_DIR/"output_rutebyg.md", "w") as file:
        file.write("# Medlemsundersøgelse 2023\n")
        file.write("## Feedback for rutebyg\n")
        file.write(md_text_rutebyg)

    # Save vibe feedback to markdown
    md_text_vibe = "\n\n".join(
        filter(
            None,
            (format_to_markdown_vibe(row) for _, row in df_c.iterrows()),
        )
    )
    with open(MD_DIR / "output_vibe.md", "w") as file:
        file.write("# Medlemsundersøgelse 2023\n")
        file.write("## Feedback for nkks vibe\n")
        file.write(md_text_vibe)

    # Save volunteering feedback to markdown
    md_text_volunteering = "\n\n".join(
        filter(
            None,
            (format_to_markdown_volunteer(row) for _, row in df_c.iterrows()),
        )
    )
    with open(MD_DIR/"output_volunteer.md", "w") as file:
        file.write("# Medlemsundersøgelse 2023\n")
        file.write("## Feedback for frivillighed\n")
        file.write(md_text_volunteering)
