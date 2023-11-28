#!/usr/bin/python
import ast
from pathlib import Path
import string
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pytz


DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./output")
MD_DIR = Path("./md-files")
FIG_DIR = Path("./figures")

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
    "08 - Jeg kunne godt tænke mig mere af disse typer problemer: (checkbox)": str,
    "Rutebyg - kommentarer (textarea)": str,
    "10 - Stemningen i NKK er inklusiv, og jeg føler mig hjemme i klubben. (slider)": "Int32",
    "10c - NKKs stemning - kommentarer (textfield)": str,
    "11 - Jeg ved, hvordan jeg kan bidrage til NKK som frivillig (slider)": "Int32",
    "12 - Jeg har lyst til, at være frivillig i NKK (slider)": "Int32",
    "13 - Frivillighed - Kommentarer (textarea)": str,
}

COLUMN_MAP_LANGUAGE = {
    "00 - Member Type (radio)": "00 - Medlemstype (radio)",
    "0 - Gender (radio)": "0 - Køn (radio)",
    "01 - Routesetting - height (slider)": "01 - Rutebyg - højde (slider)",
    "02 - Routesetting - level (radio)": "02 - Rutebyg - mit niveau (radio)",
    "03 - NKKs problems fit my climbing style (slider)": "03 - Problemerne i NKK passer til min klatrestil.  (slider)",
    "04 - NKKs problems fit my climbing level (slider)": "04 - Problemerne i NKK passer til mit niveau. (slider)",
    "05 - The Problems within my level are varied and interesting (slider)": "05 - Ruterne, indenfor mit niveau, er varierede og interessante. (slider)",
    "06 - There are enough problems to fit my level in NKK (slider)": "06 - Der er nok ruter på mit niveau i klubben. (slider)",
    "07 - How is the density of holds in NKKs wall? (slider)": "07 - Hvordan føles densiteten (greb pr. kvm) i klubben? (slider)",
    "08 - I would like more of this type of problem in NKK (checkbox)": "08 - Jeg kunne godt tænke mig mere af disse typer problemer: (checkbox)",
    "09 - Routesetting Comments (textarea)": "Rutebyg - kommentarer (textarea)",
    "10 - NKK has an inclusive vibe, and I feel at home in NKK (slider)": "10 - Stemningen i NKK er inklusiv, og jeg føler mig hjemme i klubben. (slider)",
    "10c - NKK's vibe - comments (textarea)": "10c - NKKs stemning - kommentarer (textfield)",
    "11 - I know how I can contribute to NKK as a volunteer (slider)": "11 - Jeg ved, hvordan jeg kan bidrage til NKK som frivillig (slider)",
    "12 - I want to volunteer in NKK (slider)": "12 - Jeg har lyst til, at være frivillig i NKK (slider)",
    "13 - Volunteering - Comments (textarea)": "13 - Frivillighed - Kommentarer (textarea)",
}


def load_and_preprocess_df(p_dk: Path, p_en: Path) -> pd.DataFrame:
    df_dk = pd.read_excel(p_dk)
    df_dk = df_dk.dropna(subset=df_dk.columns.difference(METADATA_COLS), how="all")
    df_dk["Language"] = "Danish"
    print(f"Danish responses: {len(df_dk)}")

    df_en = pd.read_excel(p_en)
    df_en = df_en.dropna(subset=df_en.columns.difference(METADATA_COLS), how="all")
    df_en["Language"] = "English"
    print(f"English responses: {len(df_en)}")

    df_en.rename(columns=COLUMN_MAP_LANGUAGE, inplace=True)

    # merge, somehow, find out later.
    df = pd.concat([df_dk, df_en], ignore_index=True)

    # data types
    for _col, _type in DATA_TYPES.items():
        if _type != str:
            df[_col] = pd.to_numeric(df[_col], errors="coerce").astype(_type)
            #  df[_col] = df[_col].astype(_type)

    print(df["00 - Medlemstype (radio)"].value_counts())
    df["00 - Medlemstype (radio)"] = df["00 - Medlemstype (radio)"].map(
        {'"2"': "morgen", '"1"': "normal"}
    )
    print(df["0 - Køn (radio)"].value_counts())
    df["0 - Køn (radio)"] = df["0 - Køn (radio)"].map(
        {'"M"': "Mand", '"F"': "Kvinde", "NaN": "X", "O": "Andet"}
    )
    df["02 - Rutebyg - mit niveau (radio)"] = (
        df["02 - Rutebyg - mit niveau (radio)"]
        .replace(np.nan, "1")
        .apply(lambda s: s.strip('" '))
    )
    print(df["02 - Rutebyg - mit niveau (radio)"].value_counts(dropna=False))
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
            1: "Grøn",
            2: "Gul",
            3: "Blå",
            4: "Lilla",
            5: "Rød",
            6: "Sort",
        }
    )
    print(df["02 - Rutebyg - mit niveau (tekst)"].value_counts())

    return df


def make_hist_data_from_df(
    df: pd.DataFrame, data_column: str, seg_column: str, reverse_seg_types=False
) -> tuple[list[np.array], list[str]]:
    seg_types = sorted(df[seg_column].dropna().unique(), reverse=reverse_seg_types)
    return [
        df[df[seg_column] == seg_type][data_column].dropna().values
        for seg_type in seg_types
    ], seg_types


def make_survey_plots(df: pd.DataFrame):
    _NKK_METADATA = [
        "00 - Medlemstype (radio)",
        "0 - Køn (radio)",
        # "01 - Rutebyg - højde (slider)",
        "02 - Rutebyg - mit niveau (radio)",
        # "02 - Rutebyg - mit niveau (tekst)",
    ]
    _COLUMNS_SLIDER = [
        "03 - Problemerne i NKK passer til min klatrestil.  (slider)",
        "04 - Problemerne i NKK passer til mit niveau. (slider)",
        "05 - Ruterne, indenfor mit niveau, er varierede og interessante. (slider)",
        "06 - Der er nok ruter på mit niveau i klubben. (slider)",
        "07 - Hvordan føles densiteten (greb pr. kvm) i klubben? (slider)",
        "10 - Stemningen i NKK er inklusiv, og jeg føler mig hjemme i klubben. (slider)",
        "11 - Jeg ved, hvordan jeg kan bidrage til NKK som frivillig (slider)",
        "12 - Jeg har lyst til, at være frivillig i NKK (slider)",
    ]

    _ROUTESET_LABEL_DICT = {
        "1": "green",
        "2": "xkcd:dark yellow",
        "3": "blue",
        "4": "purple",
        "5": "red",
        "6": "black",
    }
    for _DATA_COLUMN in _COLUMNS_SLIDER:
        print("Now generating plots for: " + _DATA_COLUMN)
        _ix = _DATA_COLUMN.split("-")[0].strip()

        fig, axes = plt.subplots(
            1, 3, figsize=(12, 6)
        )  # TODO: noget med højde. Find lige ud af det på et tidspunkt...
        for i, _SEG_COLUMN in enumerate(_NKK_METADATA):
            x, _SEG_TYPES = make_hist_data_from_df(df, _DATA_COLUMN, _SEG_COLUMN)
            if "niveau" in _SEG_COLUMN:
                axes[i].hist(
                    x,
                    density=True,
                    bins=np.arange(-0.5, 6.5, 1),
                    histtype="bar",
                    label=_SEG_TYPES,
                    color=_ROUTESET_LABEL_DICT.values(),
                )
            else:
                axes[i].hist(
                    x,
                    density=True,
                    bins=np.arange(-0.5, 6.5, 1),
                    histtype="bar",
                    label=_SEG_TYPES,
                )
            axes[i].set_xticks(
                range(6),
                labels=["<NA>", "M.Uenig", "Uenig", "Neutral", "Enig", "M.Enig"],
                rotation=60,
            )
            axes[i].legend(loc="upper left")
            axes[i].set_title(
                _SEG_COLUMN.replace("(radio)", "").strip(string.punctuation + " ")
            )

        fig.suptitle(
            _DATA_COLUMN.removeprefix(_ix)
            .replace("(slider)", "")
            .strip(string.punctuation + " ")
        )
        fig.savefig(FIG_DIR / f"hist_{_ix}.png")
        plt.close(fig)

    # Selvrapporteret grad
    fig, ax = plt.subplots()
    _SEG_COLUMN = _NKK_METADATA[1]
    _DATA_COLUMN = _NKK_METADATA[2]
    print("Now generating plots for: " + _DATA_COLUMN + "segmented on " + _SEG_COLUMN)
    x, _SEG_TYPES = make_hist_data_from_df(
        df, _DATA_COLUMN, _SEG_COLUMN, reverse_seg_types=True
    )

    ax.hist(
        x,
        bins=np.arange(-0.5, 6.5, 1),
        histtype="bar",
        label=_SEG_TYPES,
        density=True,
    )
    ax.set_xticklabels(["Grøn", "Gul", "Blå", "Lilla", "Rød", "Sort"], rotation=45)
    ax.legend(loc="upper left")
    fig.suptitle(_DATA_COLUMN.replace("(radio)", "").strip(string.punctuation + " "))
    fig.savefig(FIG_DIR / "hist_grades")
    plt.close(fig)

    # Checkbox svar
    _COLUMN_CHECKBOX = (
        "08 - Jeg kunne godt tænke mig mere af disse typer problemer: (checkbox)"
    )

    df[_COLUMN_CHECKBOX] = df[_COLUMN_CHECKBOX].apply(
        lambda o: ast.literal_eval(o) if isinstance(o, str) else []
    )
    df_expanded = df.explode(_COLUMN_CHECKBOX)
    df_expanded[_COLUMN_CHECKBOX].replace(
        {
            "balance": np.NaN,
            "tension": np.NaN,
            "sitstart": np.NaN,
            "udtopning": np.NaN,
        },
        inplace=True,
    )

    _SEG_COLUMN = _NKK_METADATA[2]
    _DATA_COLUMN = _COLUMN_CHECKBOX
    print(f"Now generating plots for: {_DATA_COLUMN}")
    _ix = _DATA_COLUMN.split("-")[0].strip()

    fig, axes = plt.subplots(
        1, 3, figsize=(12, 6)
    )  # TODO: noget med højde. Find lige ud af det på et tidspunkt...
    for i, _SEG_COLUMN in enumerate(_NKK_METADATA):
        x, _SEG_TYPES = make_hist_data_from_df(df_expanded, _DATA_COLUMN, _SEG_COLUMN)
        if "niveau" in _SEG_COLUMN:
            axes[i].hist(
                x,
                # density=True,
                histtype="bar",
                label=_SEG_TYPES,
                color=_ROUTESET_LABEL_DICT.values(),
            )
        else:
            axes[i].hist(
                x,
                # density=True,
                histtype="bar",
                label=_SEG_TYPES,
            )
        axes[i].legend()
        axes[i].set_title(
            _SEG_COLUMN.replace("(radio)", "").strip(string.punctuation + " ")
        )

    fig.suptitle(_DATA_COLUMN.replace("(checkbox)", "").strip(string.punctuation + " "))
    plt.savefig(FIG_DIR / "hist_08_routeset_type.png")
    plt.close(fig)


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

    return df_comments.sort_values(by="02 - Rutebyg - mit niveau (radio)")


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


def make_comment_documents(df_c: pd.DataFrame):
    # Save rutebyg feedback to markdown
    md_text_rutebyg = "\n\n".join(
        filter(
            None,
            (format_to_markdown_rutebyg(row) for _, row in df_c.iterrows()),
        )
    )
    with open(MD_DIR / "output_rutebyg.md", "w") as file:
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
    with open(MD_DIR / "output_volunteer.md", "w") as file:
        file.write("# Medlemsundersøgelse 2023\n")
        file.write("## Feedback for frivillighed\n")
        file.write(md_text_volunteering)


def make_plots_document():
    figure_paths = sorted(list(FIG_DIR.glob("*.png")))
    # make the grade distribution chart come first
    figure_paths.insert(0, figure_paths.pop(-1))

    with open(MD_DIR / "collated.md", "w") as file:
        file.write("# Medlemsundersøgelse 2023\n")
        file.write("## Oversigt over svar\n")
        for path in figure_paths:
            file.write(f"![{path.stem}]({str(path)})")
            file.write("\n")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    MD_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)

    submissions_files = (
        DATA_DIR / "submissions_dk.xlsx",
        DATA_DIR / "submissions_en.xlsx",
    )

    df = load_and_preprocess_df(*submissions_files)
    print(f"Loaded responses: {len(df)} responses")

    make_survey_plots(df)

    make_plots_document()

    df_c = extract_comments(df)
    print("Making comment documents....")
    make_comment_documents(df_c)
    print(
        f"DONE with comment documents, find them in {MD_DIR.absolute()}",
    )
