import os
from pathlib import Path
from datetime import date

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

APP_DIR = Path(__file__).parent
CSV_FILE = APP_DIR / "expenses.csv"
PHOTO_DIR = APP_DIR / "expense_photos"

CATEGORIES = [
    "Food",
    "Travel",
    "Education",
    "Shopping",
    "Entertainment",
    "Other"
]

COLUMNS = [
    "Date",
    "Category",
    "Amount",
    "Description"
]


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 35px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    border: 1px solid #cccccc;
    border-radius: 12px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD EXPENSE DATA
# ============================================================

def load_expenses():

    if not CSV_FILE.exists():

        df = pd.DataFrame(columns=COLUMNS)

        df.to_csv(
            CSV_FILE,
            index=False
        )

    try:

        df = pd.read_csv(CSV_FILE)

    except Exception:

        df = pd.DataFrame(columns=COLUMNS)

    # Make sure all columns exist

    for column in COLUMNS:

        if column not in df.columns:

            df[column] = ""

    df = df[COLUMNS]

    # Convert date

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Convert amount

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    ).fillna(0)

    df["Category"] = (
        df["Category"]
        .fillna("Other")
        .astype(str)
    )

    df["Description"] = (
        df["Description"]
        .fillna("")
        .astype(str)
    )

    return df


# ============================================================
# SAVE EXPENSE DATA
# ============================================================

def save_expenses(df):

    output = df.copy()

    output["Date"] = (
        pd.to_datetime(
            output["Date"],
            errors="coerce"
        )
        .dt.strftime("%Y-%m-%d")
    )

    output.to_csv(
        CSV_FILE,
        index=False
    )


# ============================================================
# ADD EXPENSE FUNCTION
# ============================================================

def add_expense(
    expense_date,
    category,
    amount,
    description
):

    df = load_expenses()

    new_expense = pd.DataFrame(
        [[
            pd.Timestamp(expense_date),
            category,
            float(amount),
            description
        ]],
        columns=COLUMNS
    )

    df = pd.concat(
        [df, new_expense],
        ignore_index=True
    )

    save_expenses(df)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💰 Personal Expense Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Record daily expenses and analyze your spending patterns'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

df = load_expenses()


# ============================================================
# ADD EXPENSE FORM
# ============================================================

st.subheader("➕ Add New Expense")

with st.form(
    "expense_form",
    clear_on_submit=True
):

    col1, col2, col3 = st.columns(3)

    with col1:

        expense_date = st.date_input(
            "Date",
            value=date.today()
        )

    with col2:

        category = st.selectbox(
            "Category",
            CATEGORIES
        )

    with col3:

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            step=1.0,
            format="%.2f"
        )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch at college"
    )

    submit = st.form_submit_button(
        "Add Expense",
        type="primary"
    )

    if submit:

        if amount <= 0:

            st.error(
                "Amount must be greater than 0."
            )

        elif not description.strip():

            st.warning(
                "Please enter a description."
            )

        else:

            add_expense(
                expense_date,
                category,
                amount,
                description.strip()
            )

            st.success(
                "Expense added successfully!"
            )

            st.rerun()


# Reload data after adding expense

df = load_expenses()


# ============================================================
# SUMMARY CALCULATIONS
# ============================================================

if df.empty:

    total = 0
    average = 0
    highest = 0
    lowest = 0

else:

    total = df["Amount"].sum()

    average = df["Amount"].mean()

    highest = df["Amount"].max()

    lowest = df["Amount"].min()


# ============================================================
# SUMMARY CARDS
# ============================================================

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "💰 Total",
        f"₹{total:,.2f}"
    )

with col2:

    st.metric(
        "📊 Average",
        f"₹{average:,.2f}"
    )

with col3:

    st.metric(
        "⬆️ Highest",
        f"₹{highest:,.2f}"
    )

with col4:

    st.metric(
        "⬇️ Lowest",
        f"₹{lowest:,.2f}"
    )


# ============================================================
# EXPENSE RECORDS TABLE
# ============================================================

st.divider()

st.subheader("📋 Expense Records")


if not df.empty:

    col1, col2 = st.columns(2)

    # Category filter

    with col1:

        selected_category = st.selectbox(
            "Filter by Category",
            ["All"] +
            sorted(
                df["Category"]
                .dropna()
                .unique()
                .tolist()
            )
        )

    # Sorting

    with col2:

        sort_option = st.selectbox(
            "Sort Expenses",
            [
                "Newest first",
                "Oldest first",
                "Highest amount",
                "Lowest amount"
            ]
        )

    view_df = df.copy()

    # Apply category filter

    if selected_category != "All":

        view_df = view_df[
            view_df["Category"] ==
            selected_category
        ]

    # Apply sorting

    if sort_option == "Newest first":

        view_df = view_df.sort_values(
            "Date",
            ascending=False
        )

    elif sort_option == "Oldest first":

        view_df = view_df.sort_values(
            "Date",
            ascending=True
        )

    elif sort_option == "Highest amount":

        view_df = view_df.sort_values(
            "Amount",
            ascending=False
        )

    elif sort_option == "Lowest amount":

        view_df = view_df.sort_values(
            "Amount",
            ascending=True
        )

    display_df = view_df.copy()

    display_df["Date"] = (
        display_df["Date"]
        .dt.strftime("%Y-%m-%d")
    )

    display_df["Amount"] = (
        display_df["Amount"]
        .apply(lambda x: f"₹{x:,.2f}")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No expense records found."
    )


# ============================================================
# DOWNLOAD CSV
# ============================================================

if not df.empty:

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Expense CSV",
        data=csv_data,
        file_name="expenses.csv",
        mime="text/csv"
    )


# ============================================================
# HIGHEST AND LOWEST EXPENSE
# ============================================================

if not df.empty:

    st.divider()

    st.subheader(
        "🔎 Highest & Lowest Expenses"
    )

    highest_row = df.loc[
        df["Amount"].idxmax()
    ]

    lowest_row = df.loc[
        df["Amount"].idxmin()
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"""
            **Highest Expense**

            ₹{highest_row['Amount']:,.2f}

            Category: {highest_row['Category']}

            Description: {highest_row['Description']}
            """
        )

    with col2:

        st.info(
            f"""
            **Lowest Expense**

            ₹{lowest_row['Amount']:,.2f}

            Category: {lowest_row['Category']}

            Description: {lowest_row['Description']}
            """
        )


# ============================================================
# SPENDING ANALYSIS
# ============================================================

if not df.empty:

    st.divider()

    st.subheader(
        "📊 Spending Analysis"
    )

    analysis_df = df.copy()

    analysis_df["Month"] = (
        analysis_df["Date"]
        .dt.to_period("M")
        .astype(str)
    )


    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📅 Monthly",
            "📂 Category-wise",
            "📈 Line Chart",
            "📊 Histogram"
        ]
    )


    # ========================================================
    # MONTHLY EXPENDITURE
    # ========================================================

    with tab1:

        monthly = (
            analysis_df
            .groupby(
                "Month",
                as_index=False
            )["Amount"]
            .sum()
        )

        fig, ax = plt.subplots(
            figsize=(9, 4)
        )

        ax.bar(
            monthly["Month"],
            monthly["Amount"]
        )

        ax.set_title(
            "Monthly Expenditure"
        )

        ax.set_xlabel(
            "Month"
        )

        ax.set_ylabel(
            "Amount (₹)"
        )

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        st.pyplot(fig)

        plt.close(fig)


        st.dataframe(
            monthly.rename(
                columns={
                    "Amount": "Total (₹)"
                }
            ),
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # CATEGORY-WISE EXPENDITURE
    # ========================================================

    with tab2:

        category_data = (
            analysis_df
            .groupby(
                "Category",
                as_index=False
            )["Amount"]
            .sum()
            .sort_values(
                "Amount",
                ascending=False
            )
        )

        col1, col2 = st.columns(2)


        # BAR CHART

        with col1:

            fig, ax = plt.subplots(
                figsize=(7, 4)
            )

            ax.bar(
                category_data["Category"],
                category_data["Amount"]
            )

            ax.set_title(
                "Category-wise Expenditure"
            )

            ax.set_xlabel(
                "Category"
            )

            ax.set_ylabel(
                "Amount (₹)"
            )

            plt.xticks(
                rotation=30
            )

            plt.tight_layout()

            st.pyplot(fig)

            plt.close(fig)


        # PIE CHART

        with col2:

            fig, ax = plt.subplots(
                figsize=(6, 6)
            )

            ax.pie(
                category_data["Amount"],
                labels=category_data["Category"],
                autopct="%1.1f%%"
            )

            ax.set_title(
                "Expense Distribution"
            )

            st.pyplot(fig)

            plt.close(fig)


        st.dataframe(
            category_data.rename(
                columns={
                    "Amount": "Total (₹)"
                }
            ),
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # LINE CHART
    # ========================================================

    with tab3:

        daily = (
            analysis_df
            .groupby(
                "Date",
                as_index=False
            )["Amount"]
            .sum()
        )

        fig, ax = plt.subplots(
            figsize=(9, 4)
        )

        ax.plot(
            daily["Date"],
            daily["Amount"],
            marker="o"
        )

        ax.set_title(
            "Daily Expense Trend"
        )

        ax.set_xlabel(
            "Date"
        )

        ax.set_ylabel(
            "Amount (₹)"
        )

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        st.pyplot(fig)

        plt.close(fig)


    # ========================================================
    # HISTOGRAM
    # ========================================================

    with tab4:

        bins = min(
            10,
            max(
                1,
                len(analysis_df)
            )
        )

        fig, ax = plt.subplots(
            figsize=(9, 4)
        )

        ax.hist(
            analysis_df["Amount"],
            bins=bins
        )

        ax.set_title(
            "Expense Amount Distribution"
        )

        ax.set_xlabel(
            "Amount (₹)"
        )

        ax.set_ylabel(
            "Frequency"
        )

        plt.tight_layout()

        st.pyplot(fig)

        plt.close(fig)


# ============================================================
# RECEIPT / EXPENSE PHOTO
# ============================================================

st.divider()

st.subheader(
    "📷 Expense Receipt / Photo"
)

uploaded_photo = st.file_uploader(
    "Upload a receipt or expense photo",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


if uploaded_photo is not None:

    PHOTO_DIR.mkdir(
        exist_ok=True
    )

    photo_path = (
        PHOTO_DIR /
        uploaded_photo.name
    )

    with open(
        photo_path,
        "wb"
    ) as file:

        file.write(
            uploaded_photo.getbuffer()
        )

    st.image(
        uploaded_photo,
        caption=uploaded_photo.name,
        width=350
    )

    st.success(
        f"Photo saved in expense_photos/{uploaded_photo.name}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Personal Expense Tracker & Analysis System "
    "• Python • Streamlit • Pandas • Matplotlib"
)